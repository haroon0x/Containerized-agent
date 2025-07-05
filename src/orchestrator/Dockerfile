FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly
RUN pip install --no-cache-dir \
    fastapi>=0.115.14 \
    uvicorn>=0.35.0 \
    docker>=7.1.0 \
    requests>=2.32.0 \
    python-dotenv>=1.1.1 \
    pydantic>=2.0.0

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.orchestrator.api.orchestrator:app", "--host", "0.0.0.0", "--port", "8000"] 