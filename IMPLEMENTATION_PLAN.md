# Medicine Management Platform Implementation Plan

## Purpose

This document captures the current agreed plan for evolving the repository into a production-ready medicine management platform. It is intended to be the working reference for backend, cloud, and future Android app implementation.

The plan prioritizes:

- learning-friendly architecture
- production-oriented structure
- incremental delivery
- low operational complexity early
- product-first decisions over infrastructure-first decisions

## Product Vision

We are building a medicine management and reminder platform to help users:

- manage medicine inventory at home
- reduce medicine waste
- store prescriptions safely
- follow dosage schedules correctly
- track adherence
- receive refill and expiry alerts
- get intelligent assistance for medicine-related questions
- support caregiver visibility and monitoring

Primary client:

- Android app built with Jetpack Compose

## Current State

The backend already has:

- FastAPI application
- Docker packaging
- Firestore integration
- Cloud Run deployment
- structured logging
- basic endpoints:
  - `GET /`
  - `GET /health`
  - `GET /medicines`
  - `POST /medicine`

Current cloud path:

```text
Source Code
  -> Cloud Build
  -> Artifact Registry
  -> Cloud Run
  -> Firestore
```

## Core Architecture Decision

Start with a **modular monolith** on Cloud Run.

Why:

- easier to learn and evolve
- lower cost than premature microservices
- easier debugging
- better fit for current product maturity
- still production-capable

Target runtime architecture for the near term:

```text
Android App
   |
   v
Firebase Auth
   |
   v
FastAPI on Cloud Run
   |
   +-> Firestore
   +-> Cloud Storage
   +-> later: Cloud Tasks / Pub/Sub / AI adapters
```

## App and Backend Priority Order

We are not treating reminders as the first feature anymore.

Agreed product-first order:

1. Identity and login
2. Inventory foundation
3. Prescription storage
4. Search foundation
5. Reminder and adherence
6. Caregiver workflows
7. AI and advanced async systems

This ordering matches the real product problems better than starting with reminder infrastructure.

## Authentication Strategy

### Decision

Use **Firebase Authentication**.

### Why

- best fit for Android
- works well with Google Cloud
- avoids building custom password auth
- enables backend token verification using trusted identity tokens

### Important architectural implication

The app handles sign-in UX. The backend verifies bearer tokens.

That means we do **not** plan a traditional backend `/login` endpoint for password handling.

Expected auth flow:

```text
Android App
  -> user signs in with Firebase Auth
  -> app gets ID token
  -> app sends Authorization: Bearer <token>
  -> backend verifies token
  -> backend loads or provisions user profile
```

### Backend auth goals

- add auth dependency layer
- add `/me`
- make all product data user-scoped
- keep design JWT-ready

## Domain Model Plan

### User

- `id`
- `name`
- `email`
- `role`
- `created_at`
- `updated_at`

### Medicine

- `id`
- `user_id`
- `name`
- `dosage`
- `frequency`
- `start_date`
- `end_date`
- `quantity`
- `quantity_unit`
- `expiry_date`
- `instructions`
- `active`
- `created_at`
- `updated_at`

### Prescription

- `id`
- `user_id`
- `image_url`
- `extracted_text`
- `ocr_status`
- `medicine_ids` or extracted structured medicines
- `created_at`

### Reminder

- `id`
- `user_id`
- `medicine_id`
- `time`
- `frequency`
- `timezone`
- `enabled`
- `next_trigger_at`
- `created_at`
- `updated_at`

### DoseLog

- `id`
- `user_id`
- `medicine_id`
- `reminder_id`
- `timestamp`
- `status`
- `source`
- `created_at`

### Likely future model

`CaregiverLink`

- `id`
- `caregiver_user_id`
- `patient_user_id`
- `status`
- `permissions`
- timestamps

## Firestore Collection Plan

Use top-level collections with explicit foreign-key style IDs.

Planned collections:

- `users`
- `medicines`
- `prescriptions`
- `reminders`
- `dose_logs`
- later: `caregiver_links`
- later: `medicine_catalog`

### Why top-level collections

- easier cross-user/admin/caregiver queries later
- easier analytics and reporting
- easier onboarding for engineers familiar with relational thinking

## Backend Package Structure Plan

Target structure:

```text
app/
  main.py
  core/
  auth/
  routes/
  services/
  repositories/
  models/
  workers/
  ai/
```

Responsibilities:

- `core/`: config, logging, shared errors, middleware
- `auth/`: token verification, current-user dependency
- `routes/`: HTTP endpoints
- `services/`: business logic
- `repositories/`: Firestore access
- `models/`: request/response/domain schemas
- `workers/`: future async job handlers
- `ai/`: AI provider integration adapters

Desired request flow:

```text
route -> service -> repository -> Firestore
```

## App Architecture Plan

Target Android stack:

- Jetpack Compose
- MVVM
- Retrofit
- repository pattern
- local reminder scheduling with WorkManager / AlarmManager

### MVP screen order

1. Auth gate / login
2. Dashboard
3. Inventory list
4. Add/Edit medicine
5. Medicine detail
6. Prescription upload/list
7. Reminder timeline
8. Dose action flow
9. Search

### UX priorities

- card-based layout
- low cognitive load
- large tap targets
- visible expiry / refill warnings
- clear taken / skipped actions
- calm health-oriented visuals
- safe disclaimers for AI features

## Reminder Strategy

### Decision

Use a **hybrid reminder model**.

### Phase 1

Schedule reminders locally in the Android app.

Why:

- fastest MVP
- lowest infrastructure complexity
- works well for single-device reminder UX

### Backend role during early reminder phase

- store reminder definitions
- store dose logs
- provide adherence summaries

### Phase 2

Add backend-triggered workflows later for:

- caregiver escalation
- refill alerts
- cross-device coordination
- advanced notification workflows

### Async infrastructure decision

When backend scheduling becomes necessary, prefer:

- **Cloud Tasks** first for scheduled backend work
- **Pub/Sub** later for event fan-out

## Prescription Storage Strategy

### Decision

Use:

- Firestore for metadata
- Cloud Storage for prescription image files

### Why

Firestore is not the right place for binary image storage.

## Search Strategy

Implement search in this order:

1. user inventory search
2. medicine catalog search
3. symptom-based AI-assisted search

This keeps search grounded in product value before introducing AI variability.

## AI Strategy

AI is important, but not phase 1.

Planned AI capabilities:

- prescription OCR
- medicine explanation
- symptom guidance
- drug interaction checks
- package detection later

### Architectural rule

Keep AI behind service adapters:

```text
routes -> services -> ai adapters
```

### Why

- easier to swap providers
- easier to test
- easier to control cost and risk

## Observability Plan

Already in progress / present:

- structured JSON logging
- request logging for core medicine endpoints
- Firestore operation logging
- health endpoint

Planned next:

- request logging middleware
- consistent error envelope
- metrics hooks
- uptime checks
- monitoring alerts

## Security Plan

- Firebase Auth bearer token verification
- service account-based GCP access
- request validation with Pydantic
- user-scoped data access everywhere
- no direct trust of client-supplied `user_id`

## Deployment Strategy

Current deployment remains:

```text
Source Code
  -> Cloud Build
  -> Artifact Registry
  -> Cloud Run
```

Developer workflow should support:

- local FastAPI run
- local Docker run
- Cloud Run deployment
- later worker deployment

## Implementation Phases

### Phase 0: Foundation Refactor

Goals:

- introduce `repositories/`
- introduce `core/` and shared config/errors
- stabilize code boundaries

Outputs:

- cleaner backend package structure
- route -> service -> repository flow

### Phase 1: Identity and Login Foundation

Goals:

- backend auth dependency
- `/me`
- user profile collection
- user-scoped API design

Outputs:

- `users` collection
- token verification support
- protected routes foundation

### Phase 2: Inventory MVP

Goals:

- production-ready `Medicine` schema
- medicine CRUD
- inventory endpoints
- inventory search

Outputs:

- backend inventory foundation
- Android inventory screens can be built against stable APIs

### Phase 3: Prescription MVP

Goals:

- prescription metadata model
- image storage integration
- upload/list APIs

Outputs:

- prescription vault capability

### Phase 4: Search Foundation

Goals:

- user inventory search
- medicine search structure

Outputs:

- practical utility for “do I already have this medicine?”

### Phase 5: Reminder and Adherence MVP

Goals:

- reminder schema
- dose log schema
- backend sync for app-local reminders
- adherence summaries

Outputs:

- reminder timeline support
- dashboard adherence support

### Phase 6: Caregiver Foundation

Goals:

- caregiver-patient links
- authorization model for caregiver access

Outputs:

- caregiver monitoring capability

### Phase 7: AI and Advanced Async Systems

Goals:

- OCR
- symptom guidance
- medicine explanation
- interaction checks
- event-driven workflows if needed

Outputs:

- intelligent assistance features

## Immediate Next Working Slice

This is the agreed next implementation focus.

### Design and implement:

1. auth flow contract
2. `/me` endpoint design
3. production-ready `Medicine` schema v1
4. repository layer introduction
5. inventory-first backend slice

### Why this slice

It aligns:

- login as first app entrypoint
- real product utility
- low infrastructure complexity
- clean foundation for later reminders, prescriptions, and AI

## What We Are Explicitly Not Doing Yet

To keep complexity under control, we are **not** prioritizing these yet:

- microservice split
- Kubernetes / GKE
- standalone load balancer
- backend-driven reminder scheduling
- full caregiver feature set
- AI-heavy features

These remain future phases, not day-one implementation targets.

## Definition of Early Success

The platform is on the right path when:

- users can authenticate
- backend can identify the current user
- medicines are user-scoped
- inventory APIs are stable
- Android app can implement login + inventory against real backend contracts
- code structure supports growth without a major rewrite
