CREATE TABLE IF NOT EXISTS eval_runs (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS eval_scores (
    run_id TEXT NOT NULL REFERENCES eval_runs (id),
    metric TEXT NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (run_id, metric)
);
