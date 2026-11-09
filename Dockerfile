FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . && useradd -r -u 10001 agentops && mkdir -p /app/data && chown -R agentops:agentops /app/data
USER agentops
EXPOSE 8000
CMD ["uvicorn","agentops.api:app","--host","0.0.0.0","--port","8000"]
