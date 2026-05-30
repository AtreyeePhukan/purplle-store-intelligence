import json

from app.database import SessionLocal
from app.models import Event

db = SessionLocal()

loaded = 0
skipped = 0

with open("data/events_cam3_v2.jsonl", "r") as f:

    for line in f:

        data = json.loads(line)

        existing = db.query(Event).filter(
            Event.event_id == data["event_id"]
        ).first()

        if existing:
            skipped += 1
            continue

        event = Event(
            event_id=data["event_id"],
            store_id=data["store_id"],
            camera_id=data["camera_id"],
            visitor_id=data["visitor_id"],
            event_type=data["event_type"],
            timestamp=data["timestamp"],
            zone_id=data["zone_id"],
            dwell_ms=data["dwell_ms"],
            is_staff=data["is_staff"],
            confidence=data["confidence"]
        )

        db.add(event)
        loaded += 1

db.commit()
db.close()

print(f"Loaded: {loaded}")
print(f"Skipped: {skipped}")
print("Done.")