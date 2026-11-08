# Deploy Runway to Google Cloud Run (public demo link for Devpost)

One container serves the React dashboard and the API. Uses the event's Google Cloud credits.

> **Before you publish:** ask the organizers in Discord whether the Tangerine data may sit behind a public URL.
> It is re-dated public PKDD'99 data, but it is the track's dataset. If not, demo locally and link the repo + video.

## Once (about 10 minutes)
1. Install the Google Cloud CLI: `brew install --cask google-cloud-sdk`
2. Sign in and pick the project that has the credits:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
   ```
3. Store the Gemini key as a secret (it is never baked into the image):
   ```bash
   gcloud services enable secretmanager.googleapis.com
   printf '%s' "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
   ```

## Deploy (from the repo root, with the CSVs in ./data)
```bash
gcloud run deploy runway --source . --region us-central1 --allow-unauthenticated \
  --memory 4Gi --cpu 2 --min-instances 1 --set-secrets GEMINI_API_KEY=gemini-api-key:latest
```
`--min-instances 1` keeps one copy warm so a judge never waits for a cold start (about $1-2 for the weekend).
The command prints the public URL. Open it logged out and click Demo mode before putting it on Devpost.

## Check it
- Top bar says "AI: Gemini API (…)"; Demo mode opens 93172 at Dec 2024 with "no shortfall (120+)".
- Stress test → "Job loss + bills +15%" on 20111 reads **3.4 months** (the answer key).

## Take it down after judging
```bash
gcloud run services delete runway --region us-central1
```
