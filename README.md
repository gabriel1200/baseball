# ⚾ MLB Batting Application

Hope you enjoy!

---

## 🚀 Data

The application depends on three CSV files, whose origins and purposes are described below:

### mlb_full.csv 
This has the full game logs of every player. I generated this via scraping the TrueMedia API for each playerID, doing a simple calculation of the rate stats using pandas, and combining all of these logs into one row. This data is used to populate all of the time series graphics and the game logs.

*(For a proper production involving decades of data, I suspect the most efficient route would be to save each game log as its own table indexed by playerid. However, given the dataset being relatively small, making one file and loading it in at the onset felt the most sensible approach.)*

### mlb_player_averages.csv  
This was derived from mlb_full.csv. It includes the per game and season total versions of all the counting stats, which is displayed, alongside the ranks in each category, in the player card at the top.

### mlb_rate_stat_averages.csv
This was derived from mlb_player_averages.csv. It's a very simple CSV with the average AVG, OBP, SLG and OPS calculations for all the players in the database. This is used in the time series graphics to create the league average line, with the goal being to provide some immediate context regarding how well/poorly a player is doing relative to their peers.

---

## 🚀 Getting Started

Follow these steps to run the app locally:

### 1. Clone the Repository

```bash
git clone https://github.com/gabriel1200/baseball.git
cd baseball
```

### 2. Install Dependencies

Make sure you have Python 3.7 or higher installed. Then, install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

To start the Flask app:

```bash
python app.py
```

This will launch the app locally, and you can access it by visiting:

```
http://localhost:5000
```

---

## 🧠 Features

- Interactive visualizations of MLB batting statistics
- Player-by-player breakdowns
- Comparisons of various rate & counting stat metrics throughout the season

---

## 📁 Project Structure

```
baseball/
│
├── app.py               # Main Flask app
├── requirements.txt     # Python dependencies
├── static/              # CSS/JS files
├── templates/           # HTML templates
└── data/                # CSVs with Player Stats
```