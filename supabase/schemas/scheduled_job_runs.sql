CREATE TABLE IF NOT EXISTS scheduled_job_runs (
  "id" BIGSERIAL PRIMARY KEY,
  "name" VARCHAR(255),
  "last_run_at" TIMESTAMP,
  "success" BOOLEAN,
  "inserted_rows" BIGINT,
  "error_msg" TEXT
);
