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

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
