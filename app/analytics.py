import pandas as pd
from sqlalchemy import func
from .models import Event

CSV_PATH = r"resources\Brigade_Bangalore_10_April_26 (1)bc6219c.csv"

def get_store_analytics(unique_visitors):

    df = pd.read_csv(CSV_PATH)

    orders = df["order_id"].nunique()

    revenue = float(df["total_amount"].sum())

    conversion_rate = (
        (orders / unique_visitors) * 100
        if unique_visitors > 0
        else 0
    )

    avg_order_value = (
        revenue / orders
        if orders > 0
        else 0
    )

    return {
        "orders": orders,
        "revenue": round(revenue, 2),
        "conversion_rate": round(conversion_rate, 2),
        "average_order_value": round(avg_order_value, 2)
    }
    
    
def get_heatmap(db, store_id):

    rows = (
        db.query(
            Event.zone_id,
            func.count(Event.event_id)
        )
        .filter(Event.store_id == store_id)
        .group_by(Event.zone_id)
        .all()
    )

    return {
        "store_id": store_id,
        "zones": [
            {
                "zone_id": zone,
                "event_count": count
            }
            for zone, count in rows
        ]
    }
    
def get_anomalies(store_id, unique_visitors, entries, exits):

    analytics = get_store_analytics(unique_visitors)

    anomalies = []

    if analytics["conversion_rate"] < 20:
        anomalies.append({
            "type": "LOW_CONVERSION",
            "message": "Low visitor-to-order conversion"
        })

    if exits > entries:
        anomalies.append({
            "type": "EXIT_SPIKE",
            "message": "Exit count exceeds entries"
        })

    return {
        "store_id": store_id,
        "anomalies": anomalies
    }