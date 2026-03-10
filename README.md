# Medicine Reminder Project

A minimal cloud-native backend for a medicine reminder system, built to learn backend development and Google Cloud infrastructure.

The current implementation focuses on a production-style deployment path:

- FastAPI backend
- Docker container packaging
- Google Cloud Build image build
- Artifact Registry image storage
- Google Cloud Run deployment
- Firestore-backed medicine storage
- Placeholder AI response for future Gemini integration

## Project Goal

Build a backend that:

- works locally first
- runs in Docker on port `8080`
- deploys to Google Cloud Run
- stays modular and easy to extend
- uses Firestore for persistent medicine data
- is ready for later Gemini integration

## Current Features

- `GET /health` returns service status
- `GET /medicines` reads medicine documents from Firestore
- `POST /medicine` creates a document in Firestore collection `medicines`
- `POST /ask-ai` returns a placeholder AI response
- Cloud Run deployment with a public HTTPS endpoint
- Firestore-backed persistence across container restarts

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
        Firestore Database

Build and Deploy Path
Source Code Repo -> Cloud Build -> Artifact Registry -> Cloud Run
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
5. The route calls the Firestore service layer when medicine data is needed.
6. Firestore reads or writes documents in the `medicines` collection.
7. JSON response is returned to the client.

## Components

- `FastAPI`: backend application framework for routes, request handling, and JSON responses
- `Docker`: packages the app and its dependencies into a portable container
- `Cloud Build`: builds the Docker image remotely in Google Cloud
- `Artifact Registry`: stores built container images
- `Cloud Run`: runs the container as a serverless HTTP service
- `Firestore`: stores persistent medicine documents as a managed NoSQL database

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
  {"id":"abc123","name":"Paracetamol","dosage":"500mg","time":"08:00"},
  {"id":"xyz789","name":"Vitamin D","dosage":"1000 IU","time":"21:00"}
]
```

### `POST /medicine`

Request:

```json
{"name":"Aspirin","dosage":"75mg","time":"09:30"}
```

Response:

```json
{"id":"generated-doc-id","name":"Aspirin","dosage":"75mg","time":"09:30"}
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
- Firestore database: enabled and used by the backend

Current public API:

- [Cloud Run URL](https://medicine-backend-vb5delfjra-el.a.run.app)

Typical deploy commands:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud artifacts repositories create medicine-backend-repo --repository-format=docker --location=asia-south1
gcloud auth configure-docker asia-south1-docker.pkg.dev
gcloud builds submit --tag asia-south1-docker.pkg.dev/medicine-cloud-system/medicine-backend-repo/medicine-backend:v3
gcloud run deploy medicine-backend \
  --image asia-south1-docker.pkg.dev/medicine-cloud-system/medicine-backend-repo/medicine-backend:v3 \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 1
```

### Firestore Setup Concept

- Collection: `medicines`
- Document: one medicine record
- Fields:
  - `name`
  - `dosage`
  - `time`

Example document:

```text
medicines/
  abc123
    name: "Paracetamol"
    dosage: "500mg"
    time: "08:00"
```

### Cloud Run Authentication to Firestore

The backend does not embed a credentials file inside the container.

- Cloud Run runs the container as a Google service account.
- `firestore.Client()` uses Application Default Credentials automatically.
- Google client libraries obtain short-lived credentials for that service account.
- Firestore authorizes read and write access using IAM roles on that service account.

In practice, this means the code can call Firestore directly in Cloud Run without manually loading a JSON key file.

## Current Limits

- no real Gemini integration yet
- no authentication yet
- no automated test suite yet
- local Firestore development setup is not documented yet
- Firestore failures currently return `503`, but there is no retry strategy yet

## Next Recommended Steps

1. Add environment-based configuration.
2. Add tests for the Firestore-backed routes.
3. Add CI/CD from GitHub to Cloud Run.
4. Replace placeholder AI response with Gemini integration.
