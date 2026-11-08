# Deploy Runway: Docker locally, then Google Cloud Run

One container serves the React dashboard and the API (FastAPI + uvicorn). Gemini runs on **Vertex AI**, so no API key
is stored anywhere: on Cloud Run the service's own Google identity is allowed to call Gemini.

> **Before you publish:** ask the organizers whether the Tangerine data may sit behind a public URL. It is re-dated
> public PKDD'99 data, but it is the track's dataset. If not, demo locally and link the repo + video.

## 1. Run the container on your laptop (no cloud needed)
```bash
cp -R ~/Downloads/runway/data ./data            # the CSVs; gitignored, never committed
docker build --platform linux/amd64 -t runway:local .
docker run --rm -p 8080:8080 runway:local       # offline: rules read twist cards, templates write text
python scripts/smoke.py http://localhost:8080   # 8 checks: answer key, pitch numbers, evidence, twist, speed
```
Open http://localhost:8080. The top bar says "AI: offline rules"; everything else works. To use Gemini from the
container on your laptop, mount your Google sign-in:
```bash
docker run --rm -p 8080:8080 -e GOOGLE_CLOUD_PROJECT=runway-datathon-11072341 -e GOOGLE_CLOUD_LOCATION=global \
  -v ~/.config/gcloud:/root/.config/gcloud:ro runway:local
```

## 2. Deploy to Cloud Run (about 10 minutes, uses the event credits)
```bash
gcloud config set project runway-datathon-11072341
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com
PN=$(gcloud projects describe runway-datathon-11072341 --format='value(projectNumber)')
gcloud projects add-iam-policy-binding runway-datathon-11072341 \
  --member="serviceAccount:${PN}-compute@developer.gserviceaccount.com" --role=roles/aiplatform.user
gcloud run deploy runway --source . --region us-central1 --allow-unauthenticated \
  --memory 4Gi --cpu 2 --min-instances 1 --max-instances 3 --timeout 120 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=runway-datathon-11072341,GOOGLE_CLOUD_LOCATION=global
```
- `--source .` builds this Dockerfile in Cloud Build (with ./data in the build context) and prints the public URL.
- `--min-instances 1` keeps one copy warm so a judge never waits for a cold start (a few dollars for the weekend).
- `--max-instances 3` caps the bill if the link is shared widely.

## 3. Check it
```bash
python scripts/smoke.py https://YOUR-URL.run.app
```
Then open the URL in a private window: the top bar says "AI: Gemini on Vertex AI", Pitch mode opens 93172 at Dec 2024.

## 4. Take it down after judging
```bash
gcloud run services delete runway --region us-central1
gcloud projects delete runway-datathon-11072341   # stops everything, including Vertex
```
