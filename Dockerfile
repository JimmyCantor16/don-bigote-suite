FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r backend/requirements.txt && pip install --no-cache-dir uvicorn
ENV PORT=10000
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
