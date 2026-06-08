FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY harness ./harness
COPY metrics ./metrics
COPY safety ./safety
COPY api ./api
COPY jobs ./jobs
COPY store ./store
COPY config ./config
COPY calibration ./calibration
COPY ci ./ci
COPY data ./data
RUN pip install --no-cache-dir .

CMD ["arq", "jobs.arq_worker.WorkerSettings"]
