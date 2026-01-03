import os, json, requests
import pandas as pd
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import joblib

load_dotenv()
KEY = os.getenv("TM_API_KEY")
assert KEY, "TM_API_KEY not found"

MODEL_PATH = "scoring_model.pkl"
OUT_JSON = "top10.json"

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

def safe_get(dct, path, default=None):
    cur = dct
    try:
        for p in path:
            cur = cur[p]
        return cur
    except Exception:
        return default

def hour_from_local_time(t):
    if not t:
        return -1
    try:
        return int(t.split(":")[0])
    except Exception:
        return -1

def segment_from_event(e):
    seg = safe_get(e, ["classifications", 0, "segment", "name"], None)
    return seg if seg else "Unknown"

def fetch_events():
    params = {
        "apikey": KEY,
        "city": "Stockholm",
        "countryCode": "SE",
        "size": 200
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return safe_get(data, ["_embedded", "events"], [])

def main():
    model = joblib.load(MODEL_PATH)

    events = fetch_events()
    today = date.today()

    rows = []
    for e in events:
        local_date = safe_get(e, ["dates", "start", "localDate"], None)
        local_time = safe_get(e, ["dates", "start", "localTime"], None)
        span_multiple_days = bool(safe_get(e, ["dates", "spanMultipleDays"], False))

        if not local_date:
            continue
        try:
            ev_date = datetime.strptime(local_date, "%Y-%m-%d").date()
        except Exception:
            continue

        days_ahead = (ev_date - today).days
        # 只推荐未来 0~14 天
        if days_ahead < 0 or days_ahead > 14:
            continue

        hour = hour_from_local_time(local_time)
        seg = segment_from_event(e)
        is_weekend = 1 if ev_date.weekday() >= 5 else 0

        rows.append({
            "id": e.get("id", ""),
            "name": e.get("name", ""),
            "url": e.get("url", ""),
            "localDate": local_date,
            "localTime": local_time or "",
            "days_ahead": int(days_ahead),
            "is_weekend": int(is_weekend),
            "hour": int(hour),
            "span_multiple_days": 1 if span_multiple_days else 0,
            "segment": seg,
        })

    df = pd.DataFrame(rows)
    if len(df) == 0:
        raise RuntimeError("No events found for the next 14 days.")

    X = df[["days_ahead", "is_weekend", "hour", "span_multiple_days", "segment"]]
    df["score"] = model.predict(X)

    top = df.sort_values("score", ascending=False).head(10)

    out = []
    for _, r in top.iterrows():
        out.append({
            "name": r["name"],
            "date": r["localDate"],
            "time": r["localTime"],
            "category": r["segment"],
            "score": float(r["score"]),
            "url": r["url"],
        })

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Wrote", OUT_JSON)
    print(top[["name", "localDate", "segment", "score"]].head(10))

if __name__ == "__main__":
    main()
