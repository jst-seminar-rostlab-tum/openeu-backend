import logging
import multiprocessing
import threading
from datetime import datetime
from typing import Callable

import schedule

from app.core.mail.notify_job_failure import notify_job_failure
from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperResult

TABLE_NAME = "scheduled_job_runs"


class ScheduledJob:
    def __init__(
        self,
        name: str,
        func: Callable,
        run_in_process: bool = False,
    ):
        """
        Initializes a ScheduledJob instance.
        :param name: Unique name for the job.
        :param func: The function to run for this job.
        :param run_in_process: If True, runs the job in a separate process; otherwise, runs in a thread.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.func = func
        self.run_in_process = run_in_process
        self.last_run_at: datetime | None = None
        self.success: bool = False
        self.result: ScraperResult | None = None
        self.error: Exception | None = None

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
            self.result = self.func()
            self.success = True
        except Exception as e:
            self.logger.error(f"Error in job '{self.name}': {e}")
            self.error = e
            notify_job_failure(self.name, e)
        finally:
            self.mark_just_ran()

    def execute(self):
        if self.run_in_process:
            multiprocessing.Process(target=self._run, daemon=True).start()
        else:
            threading.Thread(target=self._run, daemon=True).start()


class JobScheduler:
    def __init__(self):
        self.jobs: dict[str, ScheduledJob] = {}
        self.job_names: set[str] = set()
        self.logger = logging.getLogger(self.__class__.__name__)

    def register(self, name: str, func: Callable, job_schedule: schedule.Job, run_in_process: bool = False):
        if name in self.job_names:
            raise ValueError(f"Job '{name}' is already registered, name must be unique.")

        self.job_names.add(name)
        job = ScheduledJob(name, func, run_in_process)
        self.jobs[name] = job

        job_schedule.do(job.execute)
        logging.info(f"Registered job '{name}' with schedule: {job_schedule}")

    def tick(self):
        schedule.run_pending()

    def run_job(self, name: str):
        if name not in self.jobs:
            raise ValueError(f"Job '{name}' is not registered.")
        self.jobs[name].execute()


scheduler = JobScheduler()
