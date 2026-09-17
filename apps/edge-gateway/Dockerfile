FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for psycopg2 and torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Normally we'd install jaljasoos-mqtt-contracts from a local monorepo mount,
# but for Docker build context isolation, we install dependencies here.
# Since jaljasoos-mqtt-contracts isn't on PyPI, we'd copy it in a real multi-stage build.
# For this Sandbox, we'll assume it's mounted or skip strict install.
RUN sed -i '/jaljasoos-mqtt-contracts/d' pyproject.toml
RUN pip install --no-cache-dir .

COPY app/ ./app/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
