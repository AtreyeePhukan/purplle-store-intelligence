# Purplle Retail Intelligence Platform

## Overview

Purplle Retail Intelligence Platform is a computer vision and analytics solution designed to generate actionable retail insights from CCTV footage and Point-of-Sale (POS) data.

The system uses YOLOv8 and ByteTrack to detect and track visitors in retail stores, generates visitor events such as ENTRY, EXIT, and REENTRY, stores events in SQLite, exposes analytics through FastAPI APIs, and visualizes business metrics using a Streamlit dashboard.

---

## Key Features

### Computer Vision Pipeline

* YOLOv8-based person detection
* ByteTrack multi-object tracking
* Visitor identification and tracking
* Entry, Exit, and Reentry event generation

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
- CCTV Footage (CAM1–CAM5)
- POS Transaction Dataset

### Computer Vision Layer
- YOLOv8 Person Detection
- ByteTrack Multi-Object Tracking

### Event Processing Layer
- Visitor Identification
- Entry Detection
- Exit Detection
- Reentry Detection
- Event Generation

### Data Storage Layer
- JSONL Event Store
- SQLite Database

### Analytics Layer
- Visitor Metrics
- Conversion Funnel Analytics
- Revenue Analytics
- Heatmap Analytics
- Anomaly Detection

### API Layer
- FastAPI REST Endpoints

### Presentation Layer
- Streamlit Dashboard

---

## Store Configuration

Store ID:

```text
ST1008
```

Store:

```text
Brigade Bangalore
```

Camera Layout:

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

* YOLOv8
* ByteTrack
* OpenCV

### Analytics

* Pandas

### Dashboard

* Streamlit

### Testing

* Pytest

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
* Conversion rate
* Average order value

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

---

### Start Streamlit Dashboard

```bash
streamlit run dashboard/dashboard.py
```

Dashboard URL:

```text
http://localhost:8501
```

---

## Running Tests

```bash
pytest
```

Current Test Coverage:

* Health endpoint
* Root endpoint
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
* Occasional ENTRY → EXIT → REENTRY jitter may occur near boundary thresholds.
* Future improvements may include debounce and cooldown logic.
* Heatmap analytics are currently based on available zone events.

---

## Dataset Notice

The CCTV footage, POS datasets, and other challenge resources are excluded from this repository due to licensing and redistribution restrictions.

To run the complete pipeline, place the provided challenge assets in the appropriate project directories before execution.

---

## Project Status

### Completed

* FastAPI Backend
* SQLite Integration
* Event Ingestion Pipeline
* YOLOv8 Detection
* ByteTrack Tracking
* Event Generation
* Analytics APIs
* Heatmap Analytics
* Anomaly Detection
* Streamlit Dashboard
* Automated Tests
* Documentation

---

## Author

Developed as part of the Purplle Tech Challenge 2026 Round 2.
