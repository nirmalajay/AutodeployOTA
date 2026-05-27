# AutoDeploy

A small proof-of-concept OTA (Over-The-Air) update pipeline for simulated vehicle ECUs.

This project was built to understand how modern automotive software deployment works in connected vehicles. The idea was to simulate a very lightweight version of the infrastructure used in software-defined vehicles where updates are pushed remotely instead of flashing ECUs manually in a workshop.

The system uses GitHub Actions for CI/CD, MQTT for communication, MinIO for artifact storage, and a Python-based ECU simulator that listens for updates and installs them automatically.

---

## Why I Built This

Modern vehicles are becoming heavily software-driven.

Companies are now deploying:
- infotainment updates,
- ECU firmware patches,
- security fixes,
- telemetry services,
- and cloud-connected features remotely.

I wanted to build something that combines:
- CI/CD pipelines,
- cloud-native workflows,
- edge device simulation,
- and automotive software concepts

into one practical project.

Instead of creating a generic web app or AI demo, I focused on deployment infrastructure because that's closer to the kind of engineering happening behind connected vehicles today.

---

# Architecture

```text
Developer Push
      ↓
GitHub Actions Pipeline
      ↓
Build Firmware Artifact
      ↓
Upload to MinIO Storage
      ↓
OTA Backend Notification
      ↓
MQTT Update Event
      ↓
Vehicle ECU Simulator
      ↓
Installation Status + Logs
```

---

# Tech Stack

| Component | Technology |
|---|---|
| CI/CD | GitHub Actions |
| Backend API | FastAPI |
| Messaging | MQTT (Mosquitto) |
| Artifact Storage | MinIO |
| Dashboard | Streamlit |
| Containers | Docker / Docker Compose |
| Language | Python |

---

# Features

- Automated CI/CD pipeline
- Simulated OTA firmware deployment
- MQTT-based update notifications
- Version management for ECUs
- Artifact storage using S3-compatible storage
- Dockerized infrastructure
- Simple deployment dashboard
- Update status reporting

---

# Project Structure

```text
autodeploy/
│
├── backend/
│   ├── app.py
│   ├── ota_logic.py
│   └── requirements.txt
│
├── vehicle_simulator/
│   ├── simulator.py
│   └── current_version.txt
│
├── dashboard/
│   ├── dashboard.py
│   └── requirements.txt
│
├── artifacts/
│
├── .github/workflows/
│   └── pipeline.yml
│
├── docker-compose.yml
├── README.md
└── architecture.png
```

---

# How It Works

## 1. Developer Pushes New Code

A firmware version change is pushed to GitHub.

Example:

```python
version = "1.0.2"
```

---

## 2. GitHub Actions Starts Automatically

The pipeline:
- checks out the repository,
- builds the firmware artifact,
- packages it,
- uploads it to storage.

---

## 3. Artifact Gets Stored

Artifacts are uploaded to MinIO.

Example:

```text
firmware_v1.0.2.zip
```

---

## 4. OTA Backend Publishes Update Event

The backend sends an MQTT message notifying vehicles that a newer version is available.

Example:

```json
{
  "version": "1.0.2",
  "artifact": "firmware_v1.0.2.zip"
}
```

---

## 5. Vehicle ECU Simulator Updates Itself

The simulated ECU:
- receives the notification,
- compares versions,
- downloads the artifact,
- installs the update,
- reports status back.

---

# Running the Project

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+
- Git

---

## Clone the Repository

```bash
git clone <your-repo-url>
cd autodeploy
```

---

## Start Infrastructure

```bash
docker compose up
```

This starts:
- Mosquitto MQTT broker
- MinIO storage
- backend services

---

## Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

---

## Run Vehicle Simulator

```bash
cd vehicle_simulator
python simulator.py
```

---

## Run Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

---

# Example OTA Flow

```text
Current ECU Version : 1.0.1
Available Version   : 1.0.2

Downloading artifact...
Installing update...
Restarting ECU...
Update successful.
```

---

# What This Project Demonstrates

This project focuses more on infrastructure engineering than frontend development.

Key areas covered:
- CI/CD workflows
- distributed communication
- cloud artifact storage
- edge device simulation
- deployment automation
- automotive software concepts
- containerized services

---

# Possible Improvements

A few things I would like to add later:

- rollback support
- signed firmware artifacts
- Kubernetes deployment
- multiple simulated vehicles
- Prometheus + Grafana monitoring
- deployment authentication
- secure artifact validation

---

# Automotive Relevance

This project is inspired by real OTA systems used in connected vehicles and software-defined vehicle platforms.

The overall workflow resembles how modern automotive systems handle:
- ECU firmware deployment,
- fleet-wide updates,
- remote diagnostics,
- and cloud-managed software delivery.

---

# Screenshots

_Add screenshots here_

- CI/CD pipeline
- dashboard
- update logs
- MinIO storage
- vehicle simulator output

---

# Learning Outcome

The biggest takeaway from this project was understanding how deployment pipelines interact with edge devices in distributed systems.

Even though this is a simplified implementation, it helped me connect:
- DevOps practices,
- cloud infrastructure,
- and automotive software workflows

into one complete system.

---

# License

MIT License