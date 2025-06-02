ALTER TABLE "scheduled_job_runs"
    DROP CONSTRAINT scheduled_job_runs_pkey CASCADE,
    ADD COLUMN "success" BOOLEAN,
    ADD COLUMN "inserted_rows" BIGINT,
    ADD COLUMN "error_msg" TEXT,
    ADD COLUMN id BIGSERIAL,
    ADD PRIMARY KEY (id),
ALTER
COLUMN "last_run_at" SET DEFAULT now();