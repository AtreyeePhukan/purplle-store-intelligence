from ultralytics import YOLO
from datetime import datetime, timedelta
import json
import uuid
import cv2
import os

VIDEO_START_TIME = datetime(2026, 4, 10, 20, 0, 0)

STORE_ID = "ST1008"
CAMERA_ID = "CAM_3"
ZONE_ID = "ENTRY_EXIT"

FPS = 15

ENTRY_LINE_RATIO = 0.60


track_history = {}
track_entered = {}
track_exited = {}

events = []


def get_timestamp(frame_number):
    return (
        VIDEO_START_TIME +
        timedelta(seconds=frame_number / FPS)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_event(
    event_type,
    visitor_id,
    timestamp,
    confidence=0.90
):
    return {
        "event_id": str(uuid.uuid4()),
        "store_id": STORE_ID,
        "camera_id": CAMERA_ID,
        "visitor_id": f"VIS_{visitor_id}",
        "event_type": event_type,
        "timestamp": timestamp,
        "zone_id": ZONE_ID,
        "dwell_ms": 0,
        "is_staff": False,
        "confidence": round(confidence, 2),
        "metadata": {
            "queue_depth": None,
            "sku_zone": None,
            "session_seq": 1
        }
    }


def emit_event(
    event_type,
    track_id,
    timestamp,
    confidence
):
    event = make_event(
        event_type,
        track_id,
        timestamp,
        confidence
    )

    events.append(event)

    print(
        f"[{timestamp}] "
        f"{event_type} "
        f"VIS_{track_id}"
    )


def process_frame(
    track_id,
    center_y,
    frame_number,
    confidence,
    entry_line_y
):

    timestamp = get_timestamp(frame_number)

    prev_y = track_history.get(track_id)

    track_history[track_id] = center_y

    if prev_y is None:

        emit_event(
            "VISITOR_DETECTED",
            track_id,
            timestamp,
            confidence
        )

        return

    # ENTRY

    if (
        prev_y < entry_line_y
        and center_y >= entry_line_y
    ):

        if track_id not in track_entered:

            track_entered[track_id] = True

            event_type = (
                "REENTRY"
                if track_id in track_exited
                else "ENTRY"
            )

            emit_event(
                event_type,
                track_id,
                timestamp,
                confidence
            )

    # EXIT

    elif (
        prev_y >= entry_line_y
        and center_y < entry_line_y
    ):

        if track_id in track_entered:

            track_exited[track_id] = True

            del track_entered[track_id]

            emit_event(
                "EXIT",
                track_id,
                timestamp,
                confidence
            )


video_path = r"CCTV Footage\CAM 3.mp4"

cap = cv2.VideoCapture(video_path)

frame_height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

cap.release()

ENTRY_LINE_Y = int(
    frame_height * ENTRY_LINE_RATIO
)

print(
    f"Frame Height={frame_height} "
    f"Entry Line={ENTRY_LINE_Y}"
)


model = YOLO("yolov8n.pt")

results = model.track(
    source=video_path,
    classes=[0],
    persist=True,
    stream=True,
    save=False,
    verbose=False
)


frame_count = 0

for r in results:

    frame_count += 1

    # Reduced logging
    if frame_count % 100 == 0:
        print(f"Frame {frame_count}")

    if r.boxes.id is None:
        continue

    ids = r.boxes.id.cpu().numpy().astype(int)
    boxes = r.boxes.xyxy.cpu().numpy()
    confs = r.boxes.conf.cpu().numpy()

    for track_id, box, conf in zip(
        ids,
        boxes,
        confs
    ):

        x1, y1, x2, y2 = box

        center_y = int(
            (y1 + y2) / 2
        )

        process_frame(
            track_id,
            center_y,
            frame_count,
            float(conf),
            ENTRY_LINE_Y
        )

os.makedirs("data", exist_ok=True)

# output_path = "data/events_cam3.jsonl"
output_path = "data/events_cam3_v2.jsonl"

with open(output_path, "w") as f:

    for event in events:

        f.write(
            json.dumps(event)
            + "\n"
        )

print("PROCESSING COMPLETE")


print(f"Events: {len(events)}")

print(
    f"ENTRY: "
    f"{sum(1 for e in events if e['event_type']=='ENTRY')}"
)

print(
    f"EXIT: "
    f"{sum(1 for e in events if e['event_type']=='EXIT')}"
)

print(
    f"REENTRY: "
    f"{sum(1 for e in events if e['event_type']=='REENTRY')}"
)

print(
    f"VISITOR_DETECTED: "
    f"{sum(1 for e in events if e['event_type']=='VISITOR_DETECTED')}"
)

print(f"Saved: {output_path}")


