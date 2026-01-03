# Stockholm Hangout Recommender (ML Scoring Project)

## 0. Project Name and Group Members
**Project name:** Stockholm Hangout Recommender  
**Group members:** Mingyang Chen (individual project)

---

## 1. Dynamic Data Sources
This project uses **dynamic, real-time event data** from the **Ticketmaster Discovery API**.

- Data source: Ticketmaster Discovery API
- Location: Stockholm, Sweden
- Data type: Upcoming public events (music, theatre, sports, etc.)
- Data is fetched live via API calls and changes over time (not a static dataset)

This satisfies the course requirement of using a **non-static, continuously updated data source**.

---

## 2. Prediction / Ranking Problem
The goal of this project is to help users decide **which upcoming events are good candidates for social hangouts**.

Instead of a traditional binary classification, we formulate the problem as a **ranking / scoring task**:

> Given upcoming events in Stockholm, predict a **relative score** indicating how suitable each event is as a hangout, and recommend the Top-K events.

### Why ranking instead of classification?
At the beginning, I tried to treat this project as a classification problem. However, in real-world event platforms, almost all upcoming events are marked as *on sale*, which leads to extremely imbalanced labels if treated as a binary classification problem.  
To handle this realistic constraint, we model the problem as a **scoring task**, where the model learns to rank events rather than make hard yes/no decisions.

---

## 3. Machine Learning Approach
We train a **supervised scoring model** that learns a continuous score from event metadata and time-related features.

- Model: **Ridge Regression**
- Learning objective: Learn a scoring function  
  \[
  f(\text{event features}) \rightarrow \text{hangout score}
  \]
- The output score is used to rank events, and the top-ranked events are recommended.

Although the target score is a proxy (constructed from time-related preferences), the model **learns feature weights from real data**, fulfilling the ML requirement of the course.

---

## 4. Features Used
The following features are extracted from the Ticketmaster API:

| Feature | Description |
|------|------------|
| `days_ahead` | Number of days until the event |
| `is_weekend` | Whether the event is on a weekend |
| `hour` | Hour of the event start time |
| `segment` | Event category (Music, Arts & Theatre, Sports, etc.) |
| `span_multiple_days` | Whether the event spans multiple days |

These features are chosen for interpretability and relevance to social hangout planning.

---

## 5. Output and User Interface
The system outputs a ranked list of recommended events:

- Output file: `top10.json`
- Each entry contains: event name, date, category, score, and Ticketmaster link

A simple **Streamlit web interface** is provided to display the recommendations interactively, allowing users to:
- View top recommended events
- See event details
- Click through to the official Ticketmaster page

---

## 6. Project Structure
```text
stockholm-hangout-ml/
│
├── 02_build_dataset.py      # Fetches dynamic data and builds dataset
├── 03_train_scoring.py      # Trains ML scoring model
├── 04_infer_top10.py        # Generates Top-10 recommendations
├── app.py                   # Streamlit UI
├── data/
│   └── events_stockholm.csv
├── top10.json               # Model output
├── scoring_model.pkl        # Trained ML model
├── requirements.txt
├── README.md
└── .gitignore
```
---
## 7. How to Run the Project

Follow the steps below to run the project end-to-end.

### Step 1: Install Dependencies
Install all required Python packages using the provided requirements file:

```bash
pip install -r requirements.txt
```

### Step 2: Build the Dataset

Fetch dynamic event data from the Ticketmaster Discovery API and construct the dataset:

```bash
python 02_build_dataset.py
```

This step generates the dataset file:

data/events_stockholm.csv

### Step 3: Train the Machine Learning Scoring Model

Train the supervised machine learning model that learns a continuous scoring function for events:

```bash
python 03_train_scoring.py
```

This step outputs the trained model:

scoring_model.pkl

### Step 4: Generate Event Recommendations

Run inference on upcoming events and generate the top-ranked recommendations:

```bash
python 04_infer_top10.py
```

This step produces:

top10.json

### Step 5: Launch the User Interface

Start the Streamlit web application to view the recommendations:

```bash
streamlit run app.py
```
---
## 8. Summary

This project implements a complete **end-to-end machine learning pipeline** for event recommendation using dynamic real-world data.

The system:
- Continuously ingests live event data from an external API
- Performs feature extraction and preprocessing
- Trains a supervised machine learning model
- Produces ranked event recommendations
- Presents results through an interactive user interface

By formulating the problem as a **scoring and ranking task**, the project reflects realistic constraints of real-world event platforms and demonstrates practical machine learning system design.
---
## 9. Future Work

Several directions can be explored to further improve this project:

1. **Richer User Preference Modeling**  
   Currently, the scoring function is based on general time and category features. Future work could incorporate personalized preferences, such as preferred event categories, typical availability times, or historical user interactions, to provide more tailored recommendations.

2. **Improved Proxy Labels and Feedback Signals**  
   Due to the lack of explicit user feedback, the current model relies on heuristic proxy scores. In the future, additional signals such as ticket price changes, popularity trends, or user click-through data could be used to construct more informative supervision signals.

3. **Advanced Ranking Models**  
   While Ridge regression provides a stable and interpretable baseline, more advanced ranking-oriented models (e.g., learning-to-rank approaches or gradient-based models) could be explored to better capture non-linear feature interactions.

4. **Temporal and Trend-Aware Modeling**  
   Event popularity and suitability can change over time. Future extensions could incorporate temporal dynamics, such as recent demand trends or seasonal patterns, to make the recommendations more adaptive.
