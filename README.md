# Steve – Intelligent Routine Generator from WHOOP Data

Steve is a data-driven, AI-powered system that generates personalized weekly habit routines using biometric data from the WHOOP wearable, user-defined goals, and GPT-4. It integrates a lightweight data pipeline, prompt engineering, and a clean web-based frontend for routine tracking and weekly adherence reporting.

---

## 🚀 Overview

Steve bridges the gap between raw fitness data and actionable behavior change. By connecting to a user's WHOOP account, it automatically fetches and cleans physiological metrics (like HRV, strain, and recovery), captures personal goals via a simple interface, and uses GPT-4 to generate a custom 7-day routine focused on recovery, sleep, or cardio training.

The result is a structured, JSON-formatted weekly plan that is delivered to a web interface where users can track daily habits, view progress, and reflect with weekly reports.

---

## Core Features

-  **WHOOP API Integration** – Authenticates user and pulls workout, sleep, and recovery data.
-  **Data Cleaning & Summarization** – Processes and aggregates time-series data into key metrics.
-  **Macro-Goal Selection** – User selects goal (e.g., "sleep", "recovery", or "cardio") via CLI or form.
-  **GPT-4 Routine Generation** – Builds weekly checklist of habits and fitness sessions based on personalized prompt.
-  **Web App Interface** – Visualizes the routine, tracks daily habit completion, and exports adherence reports.

---

## 📁 Project Structure

```bash
.
├── onetime.py                  # Run once to setup user authentication for Whoop API access
├── fetch_whoop_data.py         # Pulls WHOOP data using access token
├── whoop_clean_pipeline.ipynb  # Cleans and summarizes biometric data
├── macro_goal_cli.py           # CLI for capturing user macro goal + habits
├── generate_routine.py         # Builds prompt and queries OpenAI API
├── routine_output.json         # GPT-generated weekly routine
├── clean_daily.csv             # Cleaned daily biometric data
├── clean_workout.csv           # Cleaned workout log
├── user_goal.json              # User-defined profile
├── frontend/                   # React-based frontend interface (hosted via Vercel)
│   ├── [UI code & components]
│   └── ...
└── .tokens/                    # Stores WHOOP access & refresh tokens securely
```

---

## Usage

> ⚠️ **Note**: You must have a WHOOP Developer API client ID and secret. Currently supports single-user workflows.

### 1. Set Up Environment
```bash
pip install -r requirements.txt
```

### 2. Authenticate with WHOOP API
Run the one-time setup to authenticate:
```bash
python onetime.py
```

This will save your tokens securely to `.tokens/token.json`.

### 3. Fetch WHOOP Data
```bash
python fetch_whoop_data.py --start YYYY-MM-DD --end YYYY-MM-DD
```

Generates raw exports for:
- `workouts`
- `cycles`
- `sleep`
- `recovery`

### 4. Clean and Summarize Data
Use the included Jupyter notebook:
```bash
whoop_clean_pipeline.ipynb
```

Outputs:
- `clean_daily.csv`
- `clean_workout.csv`

### 5. Set Macro Goal and Preferences
```bash
python macro_goal_cli.py
```

Creates `user_goal.json` with fields like:
```json
{
  "macro_goal": "sleep",
  "frequency": 4,
  "exercise_type": "cardio",
  "fasting": true,
  "avg_sleep": "23:00",
  "avg_wake": "07:00"
}
```

### 6. Generate Routine via GPT
```bash
python generate_routine.py \
  --profile clean_whoop/user_goal.json \
  --daily   clean_whoop/clean_daily.csv \
  --workout clean_whoop/clean_workout.csv \
  --out     routine_output.json
```

This uses OpenAI's GPT API to create a personalized 7-day routine and saves it to `routine_output.json`.

---

## Frontend UI

The frontend is hosted separately (e.g. via Vercel) and allows users to:

https://v0-weekly-habit-tracker-report.vercel.app/

- Upload `routine_output.json`
- View and check off daily habits
- Download weekly adherence reports
- Visual progress tracking

Repo for frontend lives under `frontend/` or can be decoupled into a standalone app.

---

## 🔮 Next Steps (Planned Features)

-  Weekly feedback loop using GPT for routine evaluation
-  Calendar view for better habit visualization
-  Mobile app version (React Native)
-  Habit reminders and check-in notifications
-  Behavioral feedback learning: adapt habits based on user input and bio-data

---

## Technologies

- Python (data pipeline & OpenAI integration)
- OpenAI GPT-4
- WHOOP API
- React (Frontend UI)
- Vercel (deployment)
- CSV + JSON (lightweight data handling)

---

## 📄 License

This project is for educational and prototyping purposes. Not affiliated with WHOOP or OpenAI. Please consult legal terms before public deployment or commercial use.

---

## 🙌 Acknowledgements

- WHOOP Developer API Team  
- OpenAI GPT team  
- User testers and feedback contributors  
