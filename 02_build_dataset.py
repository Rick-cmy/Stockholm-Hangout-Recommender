import os
import time
import requests
import pandas as pd
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("TM_API_KEY")
assert KEY, "TM_API_KEY not found in .env"

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

CITY = "Stockholm"
COUNTRY = "SE"

# 你可以改这里：抓多少页、每页多少条（别太大，避免限流）
N_PAGES = 5        # 5页 * 100条 ≈ 500条（足够训练一个baseline）
PAGE_SIZE = 100

OUT_CSV = "data/events_stockholm.csv"


def safe_get(dct, path, default=None):
    """path like ['a', 0, 'b']"""
    cur = dct
    try:
        for p in path:
            cur = cur[p]
        return cur
    except Exception:
        return default


def hour_from_local_time(t):
    # "13:00:00" -> 13; if missing -> -1
    if not t:
        return -1
    try:
        return int(t.split(":")[0])
    except Exception:
        return -1


def segment_from_event(e):
    # Try classifications[0].segment.name, else "Unknown"
    seg = safe_get(e, ["classifications", 0, "segment", "name"], None)
    return seg if seg else "Unknown"


def label_from_event(e):
    code = safe_get(e, ["dates", "status", "code"], None)
    return 1 if code == "onsale" else 0


def fetch_page(page):
    params = {
        "apikey": KEY,
        "city": CITY,
        "countryCode": COUNTRY,
        "size": PAGE_SIZE,
        "page": page,
        # 你也可以加时间范围过滤（可选），先不加以降低出错率
        # "startDateTime": "2025-01-01T00:00:00Z"
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    os.makedirs("data", exist_ok=True)

    rows = []
    today = date.today()

    for page in range(N_PAGES):
        data = fetch_page(page)
        events = safe_get(data, ["_embedded", "events"], [])
        print(f"[page {page}] events:", len(events))

        for e in events:
            local_date = safe_get(e, ["dates", "start", "localDate"], None)
            local_time = safe_get(e, ["dates", "start", "localTime"], None)
            span_multiple_days = safe_get(e, ["dates", "spanMultipleDays"], False)

            # 有些 event 可能缺 localDate，直接跳过
            if not local_date:
                continue

            try:
                ev_date = datetime.strptime(local_date, "%Y-%m-%d").date()
                days_ahead = (ev_date - today).days
            except Exception:
                continue

            row = {
                # for debugging / UI later
                "id": e.get("id", ""),
                "name": e.get("name", ""),
                "url": e.get("url", ""),
                "localDate": local_date,
                "localTime": local_time or "",

                # features
                "days_ahead": int(days_ahead),
                "is_weekend": 1 if ev_date.weekday() >= 5 else 0,
                "hour": hour_from_local_time(local_time),
                "segment": segment_from_event(e),
                "span_multiple_days": 1 if span_multiple_days else 0,

                # label
                "y_good_hangout": label_from_event(e),

                # label source (helpful for report)
                "status_code": safe_get(e, ["dates", "status", "code"], ""),
            }
            rows.append(row)

        # 避免触发限流：每页稍微睡一下
        time.sleep(0.5)

    df = pd.DataFrame(rows)

    # 基础清洗：去重（同一个 id 可能重复出现）
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"])

    # 过滤极端值（可选）：例如只保留未来/近期活动
    # df = df[(df["days_ahead"] >= -7) & (df["days_ahead"] <= 60)]

    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print("\nSaved:", OUT_CSV)
    print("Rows:", len(df))
    print("\nLabel distribution:")
    print(df["y_good_hangout"].value_counts(dropna=False))
    print("\nSample:")
    print(df.head(3)[["name", "localDate", "segment", "status_code", "y_good_hangout"]])


if __name__ == "__main__":
    main()
