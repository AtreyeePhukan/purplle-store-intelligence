# CHOICES.md — Key Design Decisions

## Decision 1: Detection Model — YOLOv8n

### Options Considered

| Model | Pros | Cons |
|-------|------|------|
| YOLOv8n (nano) | Fast on CPU, easy install via `ultralytics`, ByteTrack bundled | Lower accuracy than larger variants |
| YOLOv8m (medium) | Better accuracy, handles occlusion better | 3–4x slower, requires stronger hardware |
| RT-DETR | Transformer-based, strong on crowded scenes | Complex setup, slower inference |
| MediaPipe | Very fast, runs on mobile | Poor on overhead/wide-angle CCTV angles |

### What AI Suggested
I asked Claude to compare these models for a retail CCTV use case running on a laptop CPU without a dedicated GPU. It recommended YOLOv8n as the starting point, noting that the nano model achieves ~45 FPS on CPU which is more than sufficient for 15fps CCTV footage. It also noted that ByteTrack being bundled directly into the Ultralytics package eliminates a separate dependency.

### What I Chose and Why
**YOLOv8n with ByteTrack.**

The footage is 15fps at 1080p. YOLOv8n handles this comfortably without GPU acceleration. The more important factor was that the `ultralytics` package bundles both YOLO and ByteTrack together — `model.track(source, tracker="bytetrack.yaml")` is a single line. Given the time constraint, reducing integration complexity was the right trade-off.

For a production deployment with 40 stores I would move to YOLOv8m or YOLOv8l and run inference on GPU instances. The nano model is an explicit time-constraint decision, not a permanent one.

### VLM Usage
I considered using a Vision Language Model (Claude Vision or GPT-4V) for zone classification — specifically, asking the model "which zone is this person standing in?" per frame. I decided against it for two reasons: (1) latency — a VLM API call per frame is not feasible at 15fps, and (2) zone assignment is deterministic given the camera layout. Since each camera covers exactly one zone, zone classification reduces to "which camera produced this frame", which requires no model at all.

---

## Decision 2: Event Schema Design

### Options Considered

**Option A — Flat table, all fields as columns**
Every field in the event schema becomes a database column. Simple queries, no JSON parsing.

**Option B — Core fields as columns, extras in a JSON metadata blob**
Store `event_id`, `visitor_id`, `event_type`, `timestamp`, `zone_id`, `is_staff`, `confidence` as columns. Put `queue_depth`, `session_seq`, `sku_zone` in a JSON `metadata` column.

**Option C — Event log only, compute everything on read**
Store raw events with minimal schema. Compute all analytics at query time.

### What AI Suggested
Claude suggested Option B — keep the schema lean with a metadata blob for extensibility. The argument was that fields like `queue_depth` only matter for a subset of event types, so making them top-level columns wastes space and adds NULLs everywhere.

### What I Chose and Why
**Hybrid of A and B.**

I agreed with Claude on `session_seq` and `sku_zone` going into metadata — they are never queried directly. I disagreed on `queue_depth`. The anomaly detection endpoint queries `queue_depth > 5` directly in SQL. Putting it in a JSON blob would require SQLite's `json_extract()` function, which adds complexity and makes the query harder to read and test. For a field that is directly queried, a column is the right choice.

This is a case where I took AI advice selectively rather than wholesale — the general principle (lean schema with metadata blob) is sound, but the specific application needed adjustment based on the actual query patterns.

### Schema Timestamp Decision
All timestamps are stored as ISO-8601 UTC strings (`2026-04-10T20:11:07Z`) derived from the CCTV footage timestamp overlay visible in the top-right corner of each frame. This avoids timezone conversion bugs when footage and server are in different regions.

---

## Decision 3: API Architecture — FastAPI + SQLite vs Alternatives

### Options Considered

| Stack | Pros | Cons |
|-------|------|------|
| FastAPI + SQLite | Zero setup, single file DB, docker compose trivial | Not horizontally scalable |
| FastAPI + PostgreSQL | Production-grade, concurrent writes | Requires separate DB container, more compose config |
| FastAPI + Redis | Fast reads, good for real-time metrics | Data volatility, no persistence by default |
| Flask + SQLite | Simple | No automatic OpenAPI docs, slower to build endpoints |

### What AI Suggested
Claude suggested FastAPI + PostgreSQL for production-readiness scoring, noting that the challenge rubric mentions "production-aware" API design. It argued that running Postgres in a second docker-compose service is minimal extra effort and signals production awareness to scorers.

### What I Chose and Why
**FastAPI + SQLite.**

I disagreed with Claude here for a specific reason: the acceptance gate is `docker compose up` on a clean machine. Every additional service is another failure point during evaluation. SQLite requires zero configuration, zero environment variables, and zero separate container. The database is a file — it works identically in development and in Docker.

The production-readiness points are better earned through structured logging, idempotent ingest, graceful error handling, and a working health endpoint — not through database choice. A well-structured SQLite deployment is more production-aware than a poorly configured Postgres setup.

I documented this trade-off explicitly: SQLite is the right choice for this submission. PostgreSQL would be the right choice at 40 live stores with concurrent writes from multiple detection pipelines.

---

## What I Would Change With More Time

1. **Cross-camera Re-ID** — Use OSNet (torchreid) to match appearance embeddings across cameras. Currently the same customer can be counted in CAM 1 and CAM 2 as separate zone visits, which is correct, but if they exit and re-enter they may not be matched as a re-entry if the track is lost between cameras.

2. **Real-time streaming** — Replace the batch detection pipeline with a frame-by-frame stream feeding events directly into the API as the video plays. The current architecture processes the full clip and then ingests — functional but not truly real-time.

3. **Staff detection model** — Replace the HSV colour heuristic with a proper uniform classifier trained on the visible black-uniform staff in the footage. The heuristic works for this store but would fail at stores with different uniform colours.