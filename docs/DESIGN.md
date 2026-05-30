# DESIGN.md

## What This System Does

Apex Retail has no visibility into what happens inside their physical stores. This system fixes that by processing CCTV footage and turning it into the same kind of behavioural analytics their online channel already has — visitors, dwell time, conversion rate, drop-off points.

The north star metric is offline conversion rate: unique visitors who completed a purchase divided by total unique visitors in a session window. Every design decision in this system either improves the accuracy of that number or makes it more actionable.

---

## How It Works

The system has four parts that run in sequence.

**Detection pipeline** reads the video files frame by frame, runs YOLOv8n to find people, and uses ByteTrack to maintain a consistent identity for each person across frames. When someone crosses the entry threshold in CAM 3, the pipeline emits an ENTRY event with a new visitor_id. As they move through the store, ZONE_ENTER and ZONE_DWELL events follow. When they leave, EXIT closes the session. All of this goes into a .jsonl file.

**Event ingestion** takes that .jsonl file and POSTs it to the API in batches. The ingest endpoint validates each event against the Pydantic schema, deduplicates by event_id, and writes to SQLite. This step is idempotent — running it twice produces the same database state.

**Analytics API** is a FastAPI app that computes metrics on demand from the stored events. Nothing is pre-cached. Every GET request runs a SQL query against the events table. This means metrics are always current, and there is no cache invalidation problem.

**Dashboard** is a Streamlit app that polls /metrics every 5 seconds and displays visitor count, conversion rate, and queue depth. It is intentionally simple — the goal is to prove the pipeline and API are connected, not to build a product UI.

---

## Camera Layout

I watched all five clips before writing any code. The layout is:

- **CAM 1** — Skincare section. Overhead angle, good zone coverage.
- **CAM 2** — Makeup section. Wide angle, multiple customers visible simultaneously.
- **CAM 3** — Store entrance. This is the primary entry/exit camera. The threshold line is drawn at the bottom quarter of the frame where foot traffic crosses.
- **CAM 4** — Backroom and inventory area. No customers here. Every detection from this camera is flagged is_staff: true and excluded from all customer metrics.
- **CAM 5** — Billing counter. Used for queue depth tracking and POS correlation.

---

## Database

Single SQLite file. One table: events.

The main columns are event_id (primary key for deduplication), visitor_id, event_type, timestamp, zone_id, is_staff, confidence, and queue_depth. I kept queue_depth as a top-level column rather than burying it in a metadata blob because the anomaly detection query filters on it directly — json_extract() in SQLite works but makes the query harder to read and test.

Two indexes: one on (store_id, timestamp) for the metrics queries that filter by time window, and one on visitor_id for the funnel queries that reconstruct session histories.

---

## API Endpoints

**POST /events/ingest** accepts batches up to 500 events. Deduplication is on event_id at the database level (INSERT OR IGNORE). Malformed events in a batch return a partial success response — valid events are stored, invalid ones are listed in the errors field.

**GET /stores/{id}/metrics** returns unique visitors (ENTRY events with is_staff=false), conversion rate (visitors in BILLING zone within 5 minutes before a POS transaction), average dwell per zone, current queue depth, and abandonment rate.

**GET /stores/{id}/funnel** reconstructs the session-level conversion funnel. The unit is a session, not a raw event count. A visitor who enters, leaves, and re-enters counts as one session for funnel purposes. The stages are Entry → Zone Visit → Billing Queue → Purchase.

**GET /stores/{id}/heatmap** groups events by zone_id, computes average dwell_ms, and normalises to 0–100. If fewer than 20 sessions contributed to a zone's data, data_confidence is set to false.

**GET /stores/{id}/anomalies** runs three checks: queue depth above 5 (WARN), conversion rate below 70% of the 7-day average (WARN or CRITICAL depending on magnitude), and no zone visits in any zone for 30+ minutes (INFO). Each anomaly includes a suggested_action string.

**GET /health** returns the last event timestamp per store. If the most recent event is more than 10 minutes old, the response includes a STALE_FEED warning. This is the endpoint an on-call engineer would check first.

---

## AI-Assisted Decisions

**Event schema structure** — I asked Claude whether queue_depth should be a top-level column or part of a JSON metadata blob. It recommended the metadata blob for schema flexibility. I partially disagreed: session_seq and sku_zone went into metadata because they are never queried directly, but queue_depth stayed as a column because it appears in WHERE clauses. I took the general principle and applied it selectively based on the actual query patterns.

**Staff detection approach** — Claude suggested using a full Re-ID model with uniform classification for staff detection. I pushed back on this because it would require a separate model download and significantly more inference time. We settled on a hybrid: CAM 4 detections are always staff (rule-based, 100% reliable for the backroom), and detections in other cameras use HSV colour thresholding to flag probable all-black-uniform staff. The confidence score reflects the colour match, so low-confidence staff flags are visible rather than hidden.

**Database choice** — Claude recommended FastAPI + PostgreSQL arguing it would score better on production-readiness. I chose SQLite instead. My reasoning: the acceptance gate is docker compose up on a clean machine, and every additional service is another failure point. Production-readiness points come from structured logging, idempotent ingest, and graceful error handling — not from database choice. I documented this disagreement explicitly because I think it is the right call for this specific submission, not because I think SQLite is production-grade at 40 stores.

---

## Known Limitations

These are real gaps, not oversights. I am listing them because pretending they do not exist would be worse.

**Cross-camera deduplication is not implemented.** The same customer appearing in CAM 1 and CAM 2 will generate zone events in both, which is correct behaviour. But if the same person's track is lost and reacquired between cameras, the Re-ID system may not connect them. A production system would use appearance embeddings (OSNet) to match across cameras.

**Staff detection is heuristic-based.** The HSV colour threshold works for this store's black uniforms. It would fail at a store with different uniform colours without retuning.

**Detection runs in batch, not real-time.** The pipeline processes a full video file and emits all events at the end. The dashboard simulates real-time by replaying events with original timestamps. A production deployment would process frames as they arrive from a live RTSP stream.