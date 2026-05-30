from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models
from .schemas import EventCreate
from .analytics import get_store_analytics
from .analytics import get_heatmap
from .analytics import get_anomalies

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"status": "working"}


@app.post("/events/ingest")
def ingest_event(event: EventCreate, db: Session = Depends(get_db)):

    existing = db.query(models.Event).filter(
        models.Event.event_id == event.event_id
    ).first()

    if existing:
        return {"message": "event already exists"}

    db_event = models.Event(
        event_id=event.event_id,
        store_id=event.store_id,
        camera_id=event.camera_id,
        visitor_id=event.visitor_id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        zone_id=event.zone_id,
        dwell_ms=event.dwell_ms,
        is_staff=event.is_staff,
        confidence=event.confidence
    )

    db.add(db_event)
    db.commit()

    return {"message": "event stored"}


@app.get("/events")
def get_events(db: Session = Depends(get_db)):

    events = db.query(models.Event).all()

    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "visitor_id": e.visitor_id,
            "timestamp": e.timestamp
        }
        for e in events
    ]


@app.get("/stores/{store_id}/metrics")
def get_metrics(store_id: str, db: Session = Depends(get_db)):

    events = db.query(models.Event).filter(
        models.Event.store_id == store_id
    ).all()

    unique_visitors = len(
        set(
            e.visitor_id
            for e in events
            if not e.is_staff
        )
    )

    entries = sum(
        1
        for e in events
        if e.event_type == "ENTRY"
    )

    exits = sum(
        1
        for e in events
        if e.event_type == "EXIT"
    )

    reentries = sum(
        1
        for e in events
        if e.event_type == "REENTRY"
    )

    return {
        "store_id": store_id,
        "unique_visitors": unique_visitors,
        "total_events": len(events),
        "entries": entries,
        "exits": exits,
        "reentries": reentries
    }
    
    
@app.get("/stores/{store_id}/funnel")
def get_funnel(store_id: str, db: Session = Depends(get_db)):

    events = db.query(models.Event).filter(
        models.Event.store_id == store_id
    ).all()

    unique_visitors = len(
        set(
            e.visitor_id
            for e in events
            if not e.is_staff
        )
    )

    entries = sum(
        1
        for e in events
        if e.event_type == "ENTRY"
    )

    analytics = get_store_analytics(
        unique_visitors
    )

    return {
        "store_id": store_id,
        "visitors": unique_visitors,
        "entries": entries,
        "orders": analytics["orders"],
        "conversion_rate": analytics["conversion_rate"]
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
    
    
@app.get("/stores/{store_id}/analytics")
def analytics(store_id: str, db: Session = Depends(get_db)):

    events = db.query(models.Event).filter(
        models.Event.store_id == store_id
    ).all()

    unique_visitors = len(
        set(
            e.visitor_id
            for e in events
            if not e.is_staff
        )
    )

    analytics = get_store_analytics(
        unique_visitors
    )

    return {
        "store_id": store_id,
        "unique_visitors": unique_visitors,
        **analytics
    }
    
    
@app.get("/stores/{store_id}/heatmap")
def heatmap(store_id: str, db: Session = Depends(get_db)):
    return get_heatmap(db, store_id)

@app.get("/stores/{store_id}/anomalies")
def anomalies(store_id: str, db: Session = Depends(get_db)):

    events = db.query(models.Event).filter(
        models.Event.store_id == store_id
    ).all()

    unique_visitors = len(
        set(
            e.visitor_id
            for e in events
            if not e.is_staff
        )
    )

    entries = sum(
        1
        for e in events
        if e.event_type == "ENTRY"
    )

    exits = sum(
        1
        for e in events
        if e.event_type == "EXIT"
    )

    return get_anomalies(
        store_id,
        unique_visitors,
        entries,
        exits
    )