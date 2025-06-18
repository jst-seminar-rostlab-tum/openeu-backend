import logging
import multiprocessing
import multiprocessing.synchronize
import threading
from datetime import datetime, timedelta
from typing import Callable
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
        interval: timedelta,
        timeout_minutes: int,
        grace_seconds: int = 30,
        run_in_process: bool = False,
    ):
        """
        Initializes a ScheduledJob instance.
        :param name: Unique name for the job.
        :param func: The function to run for this job. Will receive the stop_event as parameter.
            stop_event is required to ensure developers handle stopping the job gracefully.
        :param timeout_minutes: Timeout in minutes for the job to complete.
        :param interval: Time interval between runs.
        :param grace_seconds: Grace period in seconds after the interval during which the job can still run.
        :param run_in_process: If True, runs the job in a separate process; otherwise, runs in a thread.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.func = func
        self.interval = interval
        self.timeout = timedelta(minutes=timeout_minutes)
        self.grace = timedelta(seconds=grace_seconds)
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

    def should_run(self, now: datetime) -> bool:
        if self.last_run_at is None:
            return True
        elapsed = now - self.last_run_at
        return elapsed + self.grace >= self.interval

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
            self.result = self.func(self.stop_event)
            self.success = True
        except Exception as e:
            self.logger.error(f"Error in job '{self.name}': {e}")
            self.error = e
            notify_job_failure(self.name, e)
        finally:
            self.mark_just_ran()

    def run_async(self):
        """
        Runs the job asynchronously, either in a separate thread or process.
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
        interval_minutes: int,
        run_in_process: bool = False,
        timeout_minutes: int = 15,
    ):
        if interval_minutes % 10 != 0:
            raise ValueError(f"Interval for job '{name}' must be a multiple of 10 minutes.")
        if name in self.job_names:
            raise ValueError(f"Job '{name}' is already registered, name must be unique.")
        self.job_names.add(name)
        self.jobs[name] = ScheduledJob(
            name,
            func,
            timedelta(minutes=interval_minutes),
            run_in_process=run_in_process,
            timeout_minutes=timeout_minutes,
        )
        self.logger.info(
            f"Registered job '{name}' to run every {interval_minutes} minutes "
            f" with a timeout of {timeout_minutes} minutes."
        )

    def tick(self):
        now = datetime.now()
        for job in self.jobs.values():
            if job.should_run(now):
                job.run_async()

    def run_job(self, name: str):
        if name not in self.jobs:
            raise ValueError(f"Job '{name}' is not registered.")
        self.jobs[name].run_async()


scheduler = JobScheduler()
