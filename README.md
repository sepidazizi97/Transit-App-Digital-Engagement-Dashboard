# BFT Transit Engagement Intelligence Dashboard

A Streamlit dashboard analyzing rider interactions with Transit App services across routes and over time, including:

- Nearby Views
- Nearby Taps
- Routing Suggestions
- GO Trips

The dashboard supports transit planning through:

- Route-level analytics
- Monthly trend analysis
- Weekday/weekend patterns
- Seasonal analysis
- Engagement and conversion metrics

## Dashboard Features

### Overview Metrics
- Total nearby views
- Total taps
- Total routing suggestions
- Total GO trips
- Tap rate
- Routing rate
- Trip conversion rate

### Route Ranking
- Top-performing routes
- Route comparison metrics
- Engagement analysis

### Temporal Analysis
- Monthly trends
- Weekday patterns
- Seasonal changes

### Raw Data Export
- Download filtered datasets

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly

## Data Source

Transit App route interaction datasets exported from the BFT Transit App analytics backend.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
