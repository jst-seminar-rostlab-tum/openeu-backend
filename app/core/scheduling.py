import logging
import threading
from datetime import datetime, timedelta
from typing import Callable


class ScheduledJob:
    def __init__(self, name: str, func: Callable, interval: timedelta, grace_seconds: int = 30):
        self.name = name
        self.func = func
        self.interval = interval
        self.grace = timedelta(seconds=grace_seconds)
        self.last_run: datetime | None = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def should_run(self, now: datetime) -> bool:
        if self.last_run is None:
            return True
        elapsed = now - self.last_run
        return elapsed + self.grace >= self.interval

    def run_async(self):
        def _run():
            try:
                self.logger.info(f"Running job '{self.name}' at {datetime.now()}")
                self.func()
            except Exception as e:
                self.logger.error(f"Error in job '{self.name}': {e}")

        threading.Thread(target=_run, daemon=True).start()


class JobScheduler:
    def __init__(self):
        self.jobs: dict[str, ScheduledJob] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register(self, name: str, func: Callable, interval_minutes: int):
        if interval_minutes % 10 != 0:
            raise ValueError(f"Interval for job '{name}' must be a multiple of 10 minutes.")
        self.jobs[name] = ScheduledJob(name, func, timedelta(minutes=interval_minutes))
        self.logger.info(f"Registered job '{name}' to run every {interval_minutes} minutes.")

    def tick(self):
        now = datetime.now()
        for job in self.jobs.values():
            if job.should_run(now):
                job.last_run = now
                job.run_async()


scheduler = JobScheduler()
