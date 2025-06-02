ALTER TABLE "scheduled_job_runs"
    ADD COLUMN "success" BOOLEAN,
    ADD COLUMN "inserted_rows" BIGINT,
ALTER
COLUMN "last_run_at" SET DEFAULT now();