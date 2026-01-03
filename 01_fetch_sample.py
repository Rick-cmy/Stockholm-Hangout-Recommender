import os, requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("TM_API_KEY")
assert KEY, "TM_API_KEY not found"

url = "https://app.ticketmaster.com/discovery/v2/events.json"
params = {
    "apikey": KEY,
    "city": "Stockholm",
    "countryCode": "SE",
    "size": 3
}

r = requests.get(url, params=params, timeout=30)
r.raise_for_status()
data = r.json()

events = data.get("_embedded", {}).get("events", [])
print("n_events:", len(events))

e0 = events[0]
print("name:", e0.get("name"))
print("dates:", e0.get("dates"))
print("sales:", e0.get("sales"))
print("url:", e0.get("url"))
