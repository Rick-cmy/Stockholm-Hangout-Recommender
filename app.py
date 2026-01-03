import json
import streamlit as st

st.set_page_config(page_title="Stockholm Hangout Recommender")

st.title("🎉 Stockholm Hangout Recommender")
st.write("Top 10 recommended upcoming events in Stockholm (ML scoring model)")

with open("top10.json", "r", encoding="utf-8") as f:
    events = json.load(f)

for i, e in enumerate(events, start=1):
    st.subheader(f"{i}. {e['name']}")
    st.write(f"📅 {e['date']}  ⏰ {e.get('time','')}  |  🏷️ {e['category']}")
    st.write(f"⭐ Score: {e['score']:.2f}")
    st.markdown(f"[Open on Ticketmaster]({e['url']})")
    st.divider()
