# Medicine Reminder Project

A minimal cloud-native backend for a medicine reminder system, built to learn backend development and Google Cloud infrastructure.

The current implementation focuses on a production-style deployment path:

- FastAPI backend
- Docker container packaging
- Google Cloud Build image build
- Artifact Registry image storage
- Google Cloud Run deployment
- Mock medicine data and placeholder AI response

## Project Goal

Build a backend that:

- works locally first
- runs in Docker on port `8080`
- deploys to Google Cloud Run
- stays modular and easy to extend
- starts with mock data before Firestore and Gemini integration

## Current Features

- `GET /health` returns service status
- `GET /medicines` returns mock medicine data
- `POST /medicine` creates an in-memory medicine entry
- `POST /ask-ai` returns a placeholder AI response
- Cloud Run deployment with a public HTTPS endpoint

## Run Instructions

### Run Locally

From the repository root:

```bash
cd medicine-cloud-project/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Open:

- `http://127.0.0.1:8080/health`
- `http://127.0.0.1:8080/medicines`
- `http://127.0.0.1:8080/docs`

### Run With Docker

From the repository root:

```bash
cd medicine-cloud-project/backend
docker build -t medicine-backend:latest .
docker run --rm -p 8080:8080 medicine-backend:latest
```

### Verify the API

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/medicines
curl -X POST http://127.0.0.1:8080/medicine \
  -H "Content-Type: application/json" \
  -d '{"name":"Aspirin","dosage":"75mg","time":"09:30"}'
curl -X POST http://127.0.0.1:8080/ask-ai \
  -H "Content-Type: application/json" \
  -d '{"question":"Can I take medicine after food?"}'
```

## Project Structure

```text
medicine-cloud-project/
└── backend/
    ├── app/
    │   ├── ai/
    │   │   └── ai_service.py
    │   ├── models/
    │   │   └── medicine.py
    │   ├── routes/
    │   │   ├── health.py
    │   │   └── medicines.py
    │   ├── services/
    │   └── main.py
    ├── Dockerfile
    └── requirements.txt
```

## Architecture

### Conceptual Flow

```text
Mobile App / Postman / Browser
            |
            v
      Cloud Run Service
            |
            v
    Docker Container (FastAPI)
            |
            v
      Artifact Registry
            ^
            |
         Cloud Build
            ^
            |
       Source Code Repo
```

### Deployment Pipeline

1. Source code is written in this repository.
2. `gcloud builds submit` sends the source to Google Cloud Build.
3. Cloud Build uses the `Dockerfile` to build a container image.
4. The built image is pushed to Artifact Registry.
5. `gcloud run deploy` deploys that image to Cloud Run.
6. Cloud Run exposes a public HTTPS API endpoint.

### Runtime Request Flow

1. A client sends a request to the Cloud Run URL.
2. Cloud Run routes the request to the active container revision.
3. Uvicorn serves the FastAPI app inside the container.
4. FastAPI executes the matching route handler.
5. JSON response is returned to the client.

## Components

- `FastAPI`: backend application framework for routes, request handling, and JSON responses
- `Docker`: packages the app and its dependencies into a portable container
- `Cloud Build`: builds the Docker image remotely in Google Cloud
- `Artifact Registry`: stores built container images
- `Cloud Run`: runs the container as a serverless HTTP service

## API Endpoints

### `GET /health`

Response:

```json
{"status":"ok"}
```

### `GET /medicines`

Response:

```json
[
  {"id": 1, "name": "Paracetamol", "dosage": "500mg", "time": "08:00"},
  {"id": 2, "name": "Vitamin D", "dosage": "1000 IU", "time": "21:00"}
]
```

### `POST /medicine`

Request:

```json
{"name":"Aspirin","dosage":"75mg","time":"09:30"}
```

Response:

```json
{"id":3,"name":"Aspirin","dosage":"75mg","time":"09:30"}
```

### `POST /ask-ai`

Request:

```json
{"question":"Can I take medicine after food?"}
```

Response:

```json
{"answer":"Placeholder AI response for question: Can I take medicine after food?"}
```

## Local Development

From [backend](/Users/prashantmahskey/Documents/New%20project/medicine-cloud-project/backend):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Useful local URLs:

- `http://127.0.0.1:8080/health`
- `http://127.0.0.1:8080/medicines`
- `http://127.0.0.1:8080/docs`

## Docker Usage

From [backend](/Users/prashantmahskey/Documents/New%20project/medicine-cloud-project/backend):

```bash
docker build -t medicine-backend:latest .
docker run --rm -p 8080:8080 medicine-backend:latest
```

## Google Cloud Deployment

Current deployed stack:

- Project: `medicine-cloud-system`
- Region: `asia-south1`
- Cloud Run service: `medicine-backend`
- Artifact Registry repository: `medicine-backend-repo`

Current public API:

- [Cloud Run URL](https://medicine-backend-vb5delfjra-el.a.run.app)

Typical deploy commands:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud artifacts repositories create medicine-backend-repo --repository-format=docker --location=asia-south1
gcloud auth configure-docker asia-south1-docker.pkg.dev
gcloud builds submit --tag asia-south1-docker.pkg.dev/medicine-cloud-system/medicine-backend-repo/medicine-backend:v1
gcloud run deploy medicine-backend \
  --image asia-south1-docker.pkg.dev/medicine-cloud-system/medicine-backend-repo/medicine-backend:v1 \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 1
```

## Current Limits

- medicine data is in-memory only
- no Firestore integration yet
- no real Gemini integration yet
- no authentication yet
- no automated test suite yet

## Next Recommended Steps

1. Add Firestore persistence for medicines.
2. Add environment-based configuration.
3. Add tests for API routes.
4. Add CI/CD from GitHub to Cloud Run.
5. Replace placeholder AI response with Gemini integration.
