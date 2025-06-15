import logging
import multiprocessing
import threading
from datetime import datetime, time, timedelta
from typing import Callable, Optional

from app.core.mail.notify_job_failure import notify_job_failure
from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperResult

TABLE_NAME = "scheduled_job_runs"


class ScheduledJob:
    def __init__(
        self,
        name: str,
        func: Callable,
        interval: Optional[timedelta] = None,
        grace_seconds: int = 30,
        run_in_process: bool = False,
        time_of_day: Optional[time] = None,
    ):
        """
        Initializes a ScheduledJob instance.
        :param name: Unique name for the job.
        :param func: The function to run for this job.
        :param interval: Time interval between runs (mutually exclusive with time_of_day).
        :param grace_seconds: Grace period in seconds after the scheduled time during which the job can still run.
        :param run_in_process: If True, runs the job in a separate process; otherwise, runs in a thread.
        :param time_of_day: UTC time of day to run the job (mutually exclusive with interval).
        """
        if not (interval or time_of_day):
            raise ValueError("Must specify either interval or time_of_day")
        if interval and time_of_day:
            raise ValueError("Cannot specify both interval and time_of_day")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.func = func
        self.interval = interval
        self.grace = timedelta(seconds=grace_seconds)
        self.run_in_process = run_in_process
        self.time_of_day = time_of_day
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

    def should_run(self, now: datetime) -> bool:
        if self.time_of_day:
            scheduled_time = datetime.combine(now.date(), self.time_of_day)
            after = scheduled_time - self.grace
            before = scheduled_time + self.grace
            return after <= now <= before
        elif self.interval:
            if self.last_run_at is None:
                return True
            elapsed = now - self.last_run_at
            return elapsed + self.grace >= self.interval
        else:
            return False

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

    def run_async(self):
        if self.run_in_process:
            multiprocessing.Process(target=self._run, daemon=True).start()
        else:
            threading.Thread(target=self._run, daemon=True).start()


class JobScheduler:
    def __init__(self):
        self.jobs: dict[str, ScheduledJob] = {}
        self.job_names: set[str] = set()
        self.logger = logging.getLogger(self.__class__.__name__)

    def register(
        self,
        name: str,
        func: Callable,
        interval_minutes: Optional[int] = None,
        run_in_process: bool = False,
        time_of_day: Optional[time] = None,
    ):
        if interval_minutes and time_of_day:
            raise ValueError(f"Cannot specify both interval_minutes and time_of_day for job '{name}'")
        if interval_minutes and interval_minutes % 10 != 0:
            raise ValueError(f"Interval for job '{name}' must be a multiple of 10 minutes.")
        if name in self.job_names:
            raise ValueError(f"Job '{name}' is already registered, name must be unique.")

        self.job_names.add(name)
        interval = timedelta(minutes=interval_minutes) if interval_minutes else None
        self.jobs[name] = ScheduledJob(
            name, func, interval=interval, run_in_process=run_in_process, time_of_day=time_of_day
        )
        self.logger.info(f"Registered job '{name}' to run every {interval_minutes} minutes.")

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
