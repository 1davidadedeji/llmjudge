CREATE TABLE IF NOT EXISTS eval_runs (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_eval_runs_repo_created ON eval_runs (repo, created_at DESC);

CREATE TABLE IF NOT EXISTS eval_scores (
    run_id TEXT NOT NULL REFERENCES eval_runs (id),
    metric TEXT NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (run_id, metric)
);
