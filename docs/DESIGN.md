# DESIGN.md

# Purplle Retail Intelligence Platform

## Problem Statement

Physical retail stores generate large amounts of customer activity data, but unlike e-commerce platforms, much of this information remains invisible. Store operators often know how many purchases occurred but have limited visibility into visitor traffic, customer movement, dwell behavior, and conversion performance.

This system bridges that gap by processing CCTV footage and Point-of-Sale (POS) data to generate actionable retail intelligence.

The primary business objective is to measure and improve **offline conversion rate**:

> Conversion Rate = Orders ÷ Unique Visitors

The system provides the data pipeline required to compute this metric and expose it through APIs and dashboards.

---

# System Overview

The platform consists of five major components:

1. Computer Vision Pipeline
2. Event Generation
3. Event Storage
4. Analytics API
5. Dashboard

Each component is intentionally lightweight to ensure reliable execution on commodity hardware and simple deployment using Docker.

---

# Architecture

## Data Sources

### CCTV Footage

Five cameras are available:

| Camera | Location                  |
| ------ | ------------------------- |
| CAM 1  | Skincare Section          |
| CAM 2  | Makeup Section            |
| CAM 3  | Store Entrance / Exit     |
| CAM 4  | Backroom / Inventory Area |
| CAM 5  | Billing Counter           |

### POS Dataset

The POS dataset provides:

* Order IDs
* Transaction amounts
* Revenue information

This data is used to compute business metrics such as revenue, average order value, and conversion rate.

---

# Computer Vision Pipeline

## Detection

The system uses **YOLOv8n** for person detection.

Reasons for selecting YOLOv8n:

* Fast CPU inference
* Small model size
* Easy deployment
* Direct integration with ByteTrack through the Ultralytics package

The model processes CCTV footage frame-by-frame and identifies people present in the scene.

---

## Tracking

The system uses **ByteTrack** for multi-object tracking.

Tracking allows detections from consecutive frames to be associated with the same visitor.

This produces stable visitor IDs throughout a customer's movement in the scene.

---

## Current Camera Usage

The current implementation uses **CAM 3 (Store Entrance / Exit)**.

CAM 3 provides the clearest signal for visitor counting and store traffic analytics.

Future versions can extend the same pipeline to the remaining cameras for richer in-store journey analytics.

---

# Event Generation

The detection pipeline converts tracking results into structured business events.

Generated event types include:

* VISITOR_DETECTED
* ENTRY
* EXIT
* REENTRY

Each event contains:

* Event ID
* Store ID
* Camera ID
* Visitor ID
* Timestamp
* Zone ID
* Dwell Time
* Staff Flag
* Confidence Score

Events are exported to a JSONL file before ingestion into the database.

Example:

```json
{
  "event_id": "evt_001",
  "visitor_id": "visitor_12",
  "event_type": "ENTRY",
  "camera_id": "CAM_3"
}
```

---

# Data Storage

## Database

The platform uses SQLite.

SQLite was selected because:

* Zero configuration
* Single-file deployment
* Works consistently across local and Docker environments
* Simplifies reviewer setup

Database file:

```text
events.db
```

---

## Event Schema

The events table stores:

* event_id
* store_id
* camera_id
* visitor_id
* event_type
* timestamp
* zone_id
* dwell_ms
* is_staff
* confidence

The event_id field serves as the primary key and prevents duplicate event ingestion.

---

# Event Ingestion

The ingestion pipeline loads generated JSONL events into SQLite.

The process:

1. Read JSONL events
2. Validate event structure
3. Check for duplicate event IDs
4. Insert valid events into SQLite

The process is idempotent.

Running ingestion multiple times produces the same database state.

---

# Analytics Layer

The analytics layer computes business metrics from stored events and POS data.

## Visitor Metrics

Calculated metrics include:

* Unique Visitors
* Total Events
* Entries
* Exits
* Reentries

Example endpoint:

```http
GET /stores/{store_id}/metrics
```

---

## Business Analytics

Calculated metrics include:

* Orders
* Revenue
* Conversion Rate
* Average Order Value

Example endpoint:

```http
GET /stores/{store_id}/analytics
```

---

## Conversion Funnel

The funnel endpoint combines visitor activity with POS outcomes.

Stages include:

1. Visitor
2. Entry
3. Purchase

Example endpoint:

```http
GET /stores/{store_id}/funnel
```

---

## Heatmap Analytics

Heatmap analytics aggregate event counts by zone.

This helps identify areas receiving the most visitor activity.

Example endpoint:

```http
GET /stores/{store_id}/heatmap
```

---

## Anomaly Detection

The anomaly endpoint identifies unusual patterns in store activity.

Examples include:

* Unexpected traffic drops
* Missing visitor activity
* Other rule-based operational anomalies

Example endpoint:

```http
GET /stores/{store_id}/anomalies
```

---

# API Layer

The backend is implemented using FastAPI.

Available endpoints:

| Method | Endpoint                     |
| ------ | ---------------------------- |
| GET    | /                            |
| GET    | /health                      |
| POST   | /events/ingest               |
| GET    | /events                      |
| GET    | /stores/{store_id}/metrics   |
| GET    | /stores/{store_id}/analytics |
| GET    | /stores/{store_id}/funnel    |
| GET    | /stores/{store_id}/heatmap   |
| GET    | /stores/{store_id}/anomalies |

FastAPI automatically provides OpenAPI documentation through:

```text
http://localhost:8000/docs
```

---

# Dashboard

The frontend dashboard is implemented using Streamlit.

The dashboard consumes FastAPI endpoints and displays:

* Visitor Metrics
* Revenue Metrics
* Conversion Rate
* Funnel Analytics
* Heatmap Analytics
* Anomaly Analytics

The dashboard serves as a lightweight visualization layer for operational monitoring.

---

# Testing

Automated tests were implemented using Pytest.

Coverage includes:

* Root Endpoint
* Health Endpoint
* Metrics Endpoint

These tests validate basic API functionality and deployment readiness.

---

# Deployment

The system is containerized using Docker.

Services:

* FastAPI Backend
* Streamlit Dashboard

Deployment command:

```bash
docker compose up --build
```

The repository includes a pre-populated SQLite database (`events.db`) to allow reviewers to immediately evaluate the system without requiring access to the original challenge datasets.

---

# AI-Assisted Decisions

AI tools were used during development to:

* Compare detection models
* Evaluate database design choices
* Review deployment strategies
* Discuss trade-offs between simplicity and scalability

Final architectural decisions were made based on implementation requirements, challenge constraints, and deployment reliability.

---

# Known Limitations

## Single-Camera Analytics

The current implementation uses CAM 3 for visitor analytics.

Multi-camera customer journey reconstruction is not yet implemented.

---

## Cross-Camera Re-Identification

Visitors cannot currently be matched across different camera views.

A production deployment would use appearance-based re-identification models.

---

## Batch Processing

The current pipeline processes recorded footage and generates events after processing is complete.

A production deployment would process live video streams in real time.

---

## Staff Detection

Staff detection is currently rule-based and camera-dependent.

A dedicated staff classification model would improve robustness across different store layouts and uniform types.

---

# Future Improvements

* Cross-camera Re-ID using OSNet
* Real-time RTSP stream processing
* Advanced dwell-time analytics
* Queue monitoring at billing counters
* Customer journey reconstruction
* Multi-store deployment support
* PostgreSQL backend for large-scale deployments

---

# Conclusion

The system demonstrates an end-to-end retail intelligence pipeline that converts CCTV footage and POS data into actionable business insights. It combines computer vision, event processing, analytics, APIs, and dashboard visualization into a deployable solution that can be evaluated through a single Docker command.
