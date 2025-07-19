# Scheduling System Documentation

## Overview

The scheduling system manages periodic execution of background jobs using:

- Python `schedule` library for basic scheduling
- Custom `JobScheduler` wrapper for enhanced functionality
- Runs as a background thread checking for pending jobs every minute

Key features:

- Supports both process-based (CPU-bound) and thread-based (I/O-bound) execution
- Automatic timeout handling
- Comprehensive error tracking and notifications
- Database logging of all job runs

## Adding New Jobs

### Step 1: Define Job Function

```python
def my_job(stop_event: multiprocessing.synchronize.Event) -> ScraperResult:
    """
    Job functions must:
    - Accept stop_event parameter
    - Regularly check stop_event.is_set()
    - Return ScraperResult
    """
    try:
        # Job implementation
        if stop_event.is_set():
            return ScraperResult(success=False, error=Exception("Job stopped"))

        # ... job logic ...

        return ScraperResult(success=True)
    except Exception as e:
        return ScraperResult(success=False, error=e)
```

### Step 2: Register Job

Register in `setup_scheduled_jobs()` (app/core/jobs.py):

```python
def setup_scheduled_jobs():
    scheduler.register(
        name="my_job",  # Unique name
        func=my_job,    # Job function
        job_schedule=schedule.every().day.at("03:00"),  # Absolute schedule
        run_in_process=True,  # For CPU-intensive jobs
        timeout_minutes=30    # Custom timeout (default: 15)
    )
```

### Important Configurations

| Parameter         | Description                         | Example                               |
| ----------------- | ----------------------------------- | ------------------------------------- |
| `name`            | Unique job identifier               | "scrape_mep_meetings"                 |
| `func`            | Job function reference              | scrape_mep_meetings                   |
| `job_schedule`    | Schedule pattern                    | `schedule.every().monday.at("02:00")` |
| `run_in_process`  | Run in separate process (CPU-bound) | True                                  |
| `timeout_minutes` | Maximum runtime in minutes          | 30                                    |

**Important**: Always use absolute schedule values (e.g., "every day at 3:00") rather than relative values ("every two weeks") since server restarts will reset the schedule library's memory.

## Timeout Handling

The system provides two timeout mechanisms:

1. **Process-based jobs**:

   - Terminated after timeout
   - Results logged as timeout failure

2. **Thread-based jobs**:
   - `stop_event` is set
   - Job should check `stop_event.is_set()` periodically
   - System waits for graceful exit

Example timeout check:

```python
if stop_event.is_set():
    return ScraperResult(success=False, error=Exception("Job stopped"))
```

## Error Handling

The system provides comprehensive error handling:

1. **Exception Capture**:

   - All exceptions are caught and logged
   - Error details stored in database

2. **Notifications**:

   - Email alerts via `notify_job_failure`
   - Includes job name and error details

3. **Result Tracking**:
   - Success/failure status recorded
   - Error messages stored
   - For scrapers: lines added/processed

## Database Logging

All job runs are logged to `scheduled_job_runs` table with:

- Job name
- Timestamp
- Success status
- Error message (if any)
- Runtime metrics

## Best Practices

1. **Job Design**:

   - Implement periodic `stop_event` checks
   - Return meaningful `ScraperResult`
   - Handle cleanup in finally blocks

2. **Scheduling**:

   - Use absolute schedule times
   - Space out CPU-intensive jobs
   - Consider job dependencies

3. **Timeouts**:

   - Set reasonable timeouts
   - Longer for complex jobs
   - Shorter for frequent jobs

4. **Error Handling**:
   - Provide descriptive error messages
   - Include context in ScraperResult
   - Test failure scenarios

## Example Jobs

See `app/core/jobs.py` for complete examples:

1. **Simple Job** (send_weekly_newsletter)
2. **Process-based Job** (scrape_mep_meetings)
3. **Complex Job** (send_smart_alerts)
4. **Timeout Handling** (clean_up_embeddings)
