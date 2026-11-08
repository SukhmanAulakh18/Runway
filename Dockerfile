# One container for Cloud Run: builds the React dashboard, then serves it and the API with uvicorn.
# Build from a checkout that has the Tangerine CSVs in ./data (they are gitignored, never committed).
# No key is baked in: on Cloud Run Gemini runs on Vertex AI with the service's own identity (see docs/DEPLOY.md).
# Without GOOGLE_CLOUD_PROJECT the app runs fully offline (rules + templates).
FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=web /web/dist ./web/dist
ENV RUNWAY_DATA=/app/data PORT=8080
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
