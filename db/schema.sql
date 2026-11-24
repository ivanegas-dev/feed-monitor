CREATE TABLE IF NOT EXISTS feed_runs (
    id SERIAL PRIMARY KEY,
    feed_name TEXT NOT NULL CHECK (feed_name IN ('students', 'staff')),
    status TEXT NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'passed', 'failed')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    total_records INTEGER NOT NULL DEFAULT 0,
    valid_records INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS feed_errors (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES feed_runs(id) ON DELETE CASCADE,
    record_number INTEGER NOT NULL,
    record_id TEXT,
    field_name TEXT,
    error_type TEXT NOT NULL CHECK (error_type IN (
        'missing_field', 'invalid_date', 'invalid_email', 'duplicate_id')),
    message TEXT NOT NULL,
    raw_record JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()

);
CREATE INDEX IF NOT EXISTS idx_feed_errors_run_id ON feed_errors (run_id);
CREATE INDEX IF NOT EXISTS idx_feed_runs_started_at ON feed_runs (started_at DESC);