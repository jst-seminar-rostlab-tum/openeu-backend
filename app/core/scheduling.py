import logging
import multiprocessing
import multiprocessing.synchronize
import threading
from datetime import datetime, timedelta
from typing import Callable

import schedule
import typing

from app.core.mail.notify_job_failure import notify_job_failure
from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperResult

TABLE_NAME = "scheduled_job_runs"


class ScheduledJob:
    def __init__(
        self,
        name: str,
        func: Callable[[multiprocessing.synchronize.Event], typing.Any],
        job_schedule: schedule.Job,
        timeout_minutes: int,
        run_in_process: bool = False,
    ):
        """
        Initializes a ScheduledJob instance.
        :param name: Unique name for the job.
        :param func: The function to run for this job. Will receive the stop_event as parameter.
            stop_event is required to ensure developers handle stopping the job gracefully.
        :param timeout_minutes: Timeout in minutes for the job to complete.
        :param run_in_process: If True, runs the job in a separate process; otherwise, runs in a thread.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.func = func
        self.job_schedule = job_schedule
        self.timeout = timedelta(minutes=timeout_minutes)
        self.run_in_process = run_in_process
        self.last_run_at: datetime | None = None
        self.success: bool = False
        self.result: ScraperResult | None = None
        self.error: Exception | None = None
        self.stop_event: multiprocessing.synchronize.Event = multiprocessing.Event()

        try:
            result = (
                supabase.table(TABLE_NAME)
                .select("last_run_at")
                .eq("name", name)
                .order("last_run_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data and len(result.data) == 1 and result.data[0].get("last_run_at"):
                self.last_run_at = datetime.fromisoformat(result.data[0]["last_run_at"])
                self.logger.info(f"Loaded last run for '{name}': {self.last_run_at}")
        except Exception as e:
            self.logger.error(f"Failed to load last run for job '{name}': {e}")

    def mark_just_ran(self):
        now = datetime.now()
        self.last_run_at = now
        try:
            # Some jobs are not scraper jobs and there don't return a scraper result. Handle it by checking for None.
            is_result_none = self.result is None
            supabase.table(TABLE_NAME).upsert(
                {
                    "name": self.name,
                    "last_run_at": now.isoformat(),
                    "success": self.success if is_result_none else self.result.success,
                    "inserted_rows": 0 if is_result_none else self.result.lines_added,
                    "error_msg": repr(self.error) if is_result_none else repr(self.result.error),
                },
            ).execute()
        except Exception as e:
            self.logger.error(f"Failed to update last run time for job '{self.name}': {e}")

    def _run(self):
        self.success = False
        self.error = None
        self.result = None
        try:
            self.logger.info(f"Running job '{self.name}' at {datetime.now()}")
            # self.stop_event.set()  # uncomment to test timeout handling by stopping the job immediately
            self.result = self.func(self.stop_event)
            self.success = True
        except Exception as e:
            self.logger.error(f"Error in job '{self.name}': {e}")
            self.error = e
            notify_job_failure(self.name, e)
        finally:
            self.mark_just_ran()

    def execute(self):
        """
        Executes the job, either in a separate thread or process.
        If the job does not complete within the specified timeout, it will log an error and notify of the failure.
        Since threads cannot be killed safely, they are gracefully stopped using the
        stop_event which must be checked periodically by the job itself.
        """
        timeout_seconds = self.timeout.total_seconds()
        timeout_error = f"Timeout: Job '{self.name}' timed out after {(timeout_seconds / 60):.2f} minutes."

        if self.run_in_process:
            proc = multiprocessing.Process(target=self._run, daemon=True)
            proc.start()

            def monitor_process():
                proc.join(timeout=timeout_seconds)
                if proc.is_alive():
                    self.logger.error(timeout_error)
                    notify_job_failure(self.name, "Timeout reached")
                    proc.terminate()
                    # log job run in db manually, because when killing
                    # the process self.mark_just_ran() in _run() won't be reached
                    self.success = False
                    self.error = Exception("Timeout reached")
                    self.mark_just_ran()

            threading.Thread(target=monitor_process, daemon=True).start()

        else:
            thread = threading.Thread(target=self._run, daemon=True)
            thread.start()

            def monitor_thread():
                thread.join(timeout=timeout_seconds)
                if thread.is_alive():
                    self.logger.error(timeout_error + " Waiting gracefully for the thread to stop.")
                    self.stop_event.set()  # signal the thread to stop if it supports it
                    notify_job_failure(self.name, "Timeout reached")
                    thread.join()  # finally wait for the thread to cleanup and finish

            threading.Thread(target=monitor_thread, daemon=True).start()


class JobScheduler:
    def __init__(self):
        self.jobs: dict[str, ScheduledJob] = {}
        self.job_names: set[str] = set()
        self.logger = logging.getLogger(self.__class__.__name__)

    def register(
        self,
        name: str,
        func: Callable[[multiprocessing.synchronize.Event], typing.Any],
        job_schedule: schedule.Job,
        run_in_process: bool = False,
        timeout_minutes: int = 15,
    ):
        if name in self.job_names:
            raise ValueError(f"Job '{name}' is already registered, name must be unique.")

        self.job_names.add(name)
        job = ScheduledJob(name, func, job_schedule, timeout_minutes, run_in_process)
        self.jobs[name] = job

        job_schedule.do(job.execute)
        logging.info(f"Registered job '{name}' with schedule: {job_schedule}; and timeout: {timeout_minutes} minutes")

    def tick(self):
        schedule.run_pending()

    def run_job(self, name: str):
        if name not in self.jobs:
            raise ValueError(f"Job '{name}' is not registered.")
        self.jobs[name].execute()


scheduler = JobScheduler()
