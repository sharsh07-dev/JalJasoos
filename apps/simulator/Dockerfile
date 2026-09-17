FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY simulator/ ./simulator/
ENV PYTHONPATH=/app
CMD ["python", "-m", "simulator.main"]
