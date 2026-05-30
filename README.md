# Purplle Retail Intelligence Platform

## Overview

Purplle Retail Intelligence Platform is a computer vision and analytics solution designed to generate actionable retail insights from CCTV footage and Point-of-Sale (POS) data.

The system uses **YOLOv8n** and **ByteTrack** to detect and track visitors in retail stores, generates visitor events such as ENTRY, EXIT, and REENTRY, stores events in SQLite, exposes analytics through FastAPI APIs, and visualizes business metrics through a Streamlit dashboard.

---

## Key Features

### Computer Vision Pipeline

* YOLOv8n-based person detection
* ByteTrack multi-object tracking
* Visitor identification and tracking
* Entry, Exit, and Reentry event generation
* JSONL event export

### Analytics Engine

* Unique visitor counting
* Entry and exit tracking
* Conversion rate calculation
* Revenue analytics
* Average order value calculation
* Heatmap analytics
* Anomaly detection

### Dashboard

* Store performance overview
* Visitor analytics
* Revenue metrics
* Conversion funnel visualization
* Heatmap analytics
* Operational monitoring

---

## Architecture

### Data Sources

* CCTV Footage (CAM1–CAM5)
* POS Transaction Dataset

### Computer Vision Layer

* YOLOv8n Person Detection
* ByteTrack Multi-Object Tracking

### Event Processing Layer

* Visitor Identification
* Entry Detection
* Exit Detection
* Reentry Detection
* Event Generation

### Data Storage Layer

* JSONL Event Store
* SQLite Database

### Analytics Layer

* Visitor Metrics
* Conversion Funnel Analytics
* Revenue Analytics
* Heatmap Analytics
* Anomaly Detection

### API Layer

* FastAPI REST Endpoints

### Presentation Layer

* Streamlit Dashboard

---

## Store Configuration

### Store ID

```text
ST1008
```

### Store

```text
Brigade Bangalore
```

### Camera Layout

| Camera | Zone            |
| ------ | --------------- |
| CAM_1  | Skincare        |
| CAM_2  | Makeup          |
| CAM_3  | Entry / Exit    |
| CAM_4  | Backroom        |
| CAM_5  | Billing Counter |

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* SQLite

### Computer Vision

* YOLOv8n
* ByteTrack
* OpenCV

### Analytics

* Pandas

### Dashboard

* Streamlit

### Testing

* Pytest

### Deployment

* Docker
* Docker Compose

---

## API Endpoints

### Health Check

```http
GET /health
```

### Event Ingestion

```http
POST /events/ingest
```

### Retrieve Events

```http
GET /events
```

### Store Metrics

```http
GET /stores/{store_id}/metrics
```

Returns:

* Unique visitors
* Entries
* Exits
* Reentries

### Store Analytics

```http
GET /stores/{store_id}/analytics
```

Returns:

* Orders
* Revenue
* Conversion Rate
* Average Order Value

### Conversion Funnel

```http
GET /stores/{store_id}/funnel
```

### Heatmap Analytics

```http
GET /stores/{store_id}/heatmap
```

### Anomaly Detection

```http
GET /stores/{store_id}/anomalies
```

---

## Example API Response

### Metrics Endpoint

```json
{
  "store_id": "ST1008",
  "unique_visitors": 62,
  "total_events": 80,
  "entries": 12,
  "exits": 4,
  "reentries": 2
}
```

### Analytics Endpoint

```json
{
  "store_id": "ST1008",
  "unique_visitors": 62,
  "orders": 24,
  "revenue": 34331.71,
  "conversion_rate": 38.71,
  "average_order_value": 1430.49
}
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd purplle-store-intelligence
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Detection Pipeline

The detection pipeline processes CCTV footage, detects visitors, tracks movement across frames, and generates structured retail events.

### Generate Events

Run the detection pipeline:

```bash
python pipeline/detect.py
```

The pipeline uses:

* YOLOv8n for person detection
* ByteTrack for multi-object tracking
* Direction-based logic for ENTRY, EXIT, and REENTRY detection

Generated events are exported to:

```text
data/events_cam3_v2.jsonl
```

### Load Events into SQLite

After event generation, load the events into the analytics database:

```bash
python pipeline/load_events.py
```

This imports the generated events into:

```text
events.db
```

### Verify Event Ingestion

Start the FastAPI backend and query:

```http
GET /events
```

or

```http
GET /stores/ST1008/metrics
```

to verify that events were successfully ingested.

### Challenge Assets

The original CCTV footage and POS datasets provided as part of the challenge are excluded from this repository in accordance with the challenge guidelines.

To reproduce the full pipeline, place the provided challenge assets in the appropriate project directories before running the detection pipeline.

---


## Running the Application

### Start FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### Start Streamlit Dashboard

```bash
streamlit run dashboard/dashboard.py
```

Dashboard URL:

```text
http://localhost:8501
```

---

## Docker Deployment

Build and start all services:

```bash
docker compose up --build
```

FastAPI:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

Streamlit Dashboard:

```text
http://localhost:8501
```

---

## Running Tests

```bash
pytest
```

Current Test Coverage:

* Root endpoint
* Health endpoint
* Metrics endpoint

---

## Business Metrics

The provided POS dataset contains:

| Metric              | Value      |
| ------------------- | ---------- |
| Orders              | 24         |
| Revenue             | ₹34,331.71 |
| Average Order Value | ₹1,430.49  |

---

## Known Limitations

* Current implementation uses CAM_3 (Entry/Exit camera) for event generation.
* Occasional ENTRY → EXIT → REENTRY jitter may occur near threshold boundaries.
* Heatmap analytics are based on available zone events.
* Cross-camera re-identification is not implemented.
* Processing is batch-based rather than real-time.

---

## Dataset Notice

The CCTV footage, POS datasets, and other challenge resources are excluded from this repository due to licensing and redistribution restrictions.

To run the complete pipeline, place the provided challenge assets in the appropriate project directories before execution.

---

## Evaluation Note

Challenge datasets and CCTV footage are intentionally excluded from the repository as required by the challenge guidelines.

A pre-populated SQLite database (`events.db`) is included to allow reviewers to run:

```bash
docker compose up
```

and immediately evaluate API responses, analytics endpoints, and dashboard functionality without requiring access to the original challenge assets.

---

## Project Status

### Completed

* FastAPI Backend
* SQLite Integration
* Event Ingestion Pipeline
* YOLOv8n Detection
* ByteTrack Tracking
* Event Generation
* Analytics APIs
* Heatmap Analytics
* Anomaly Detection
* Streamlit Dashboard
* Automated Tests
* Docker Deployment
* Documentation

---

## Author

Developed as part of the Purplle Tech Challenge 2026 Round 2.
