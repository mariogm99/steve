"""
generate_routine.py – v4.1.4 (27 Apr 2025)
==========================================

Incremental change from v4.1.3 → hard-codes the caffeine rule to
*10 hours before avg_sleep* for the Sleep goal.

Everything else (median workout time, cardio rules, JSON schema, etc.) is
unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from dateutil import tz
from openai import OpenAI

# ---------------------------------------------------------------------------
# Goal-specific habit catalogue (caffeine rule updated)
# ---------------------------------------------------------------------------
GOAL_HABITS: Dict[str, List[str]] = {
    "sleep": [
        "Morning sunlight (10-15 min within 60 min of wake)",
        "No caffeine within 10 h of avg_sleep",
        "30-min walk in daylight",
        "Limit blue-light exposure 1 h before bed",
        "10-min evening meditation or breath-work",
    ],
    "recovery": [
        "5-min morning mobility routine",
        "Post-workout protein within 30 min",
        "Ice bath / cold plunge (2-3× week)",
        "Sauna session (15-20 min, 2-3× week)",
        "Evening foam-rolling (10 min)",
    ],
    "cardio": [
        "Zone-2 cardio session (45-60 min)",
        "10-min dynamic warm-up before exercise",
        "Track steps – 10 000+ daily target",
        "Post-workout stretch (10 min)",
        "Weekly long slow distance (LSD) session (≥ 75 min)",
    ],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce", utc=True).dt.tz_convert(None)

def load_daily(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["created_at"] = _to_dt(df["created_at"])
    if {"start", "end"}.issubset(df.columns):
        df["start"] = _to_dt(df["start"])
        df["end"] = _to_dt(df["end"])
    return df

def load_workout(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["start"] = _to_dt(df["start"])
    df["end"] = _to_dt(df["end"])
    return df

def summarise_daily(df: pd.DataFrame, days: int = 7) -> Dict[str, float]:
    if df.empty:
        return {}
    recent = df[df["created_at"] >= df["created_at"].max() - pd.Timedelta(days=days)]
    out = {
        "days": len(recent),
        "avg_strain": recent["strain"].mean(),
        "avg_recovery_score": recent.get("recovery_score", pd.Series(dtype=float)).mean(),
        "avg_hrv_ms": recent.get("hrv_ms", pd.Series(dtype=float)).mean(),
    }
    if {"start", "end"}.issubset(recent.columns):
        out["avg_sleep_hours"] = (
            (recent["end"] - recent["start"]).dt.total_seconds() / 3600
        ).mean()
    return {k: round(v, 2) for k, v in out.items() if pd.notna(v)}

def _localise(series: pd.Series, offset: str | None) -> pd.Series:
    if offset:
        off = tz.tzoffset(None, int(offset[:3]) * 3600)
        return series.dt.tz_localize(tz.UTC).dt.tz_convert(off).dt.tz_localize(None)
    return series

def summarise_workouts(df: pd.DataFrame, days: int = 7, tz_offset: str | None = None) -> Dict[str, Any]:
    if df.empty:
        return {}
    recent = df[df["start"] >= df["start"].max() - pd.Timedelta(days=days)].copy()
    recent["local_start"] = _localise(recent["start"], tz_offset)
    typical_start = None
    if not recent["local_start"].empty:
        median_ts = recent["local_start"].median()
        minute = int(round(median_ts.minute / 5) * 5) % 60
        typical_start = median_ts.replace(minute=minute, second=0, microsecond=0).strftime("%H:%M")
    durations = (recent["end"] - recent["start"]).dt.total_seconds() / 60
    out: Dict[str, Any] = {
        "workouts": len(recent),
        "workouts_per_week": round(len(recent) * 7 / days, 2),
        "avg_session_minutes": durations.mean(),
        "avg_session_strain": recent["strain"].mean(),
    }
    if typical_start:
        out["typical_start_time"] = typical_start
    if "sport" in recent.columns:
        out["top_sports"] = recent["sport"].value_counts().head(3).to_dict()
    return {k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in out.items()}

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
def build_prompt(profile: Dict[str, Any], daily: Dict[str, Any], workout: Dict[str, Any]) -> List[Dict[str, str]]:
    goal = profile.get("macro_goal", "sleep")
    habits = GOAL_HABITS[goal]
    typical = workout.get("typical_start_time", "18:00")
    top = workout.get("top_sports", {})
    if top:
        # pick the sport with the highest count; if tied, fall back to exercise_type
        most_common_sport = max(top, key=top.get)
        # if every sport only appears once, use user preference instead
        if top[most_common_sport] == 1:
            most_common_sport = profile.get("exercise_type", "mixed")
    else:
        most_common_sport = profile.get("exercise_type", "mixed")
    cardio_note = (
          "For cardio: exactly ONE LSD, 2-3 Zone-2, ONE tempo/interval; max two identical types. "
          if goal == "cardio" else ""
    )

    recovery_note = (
        "For recovery: schedule sauna **and** ice-bath on exactly three days this week "
        "(e.g. Tue-Thu-Sat); other habits stay daily. "
        if goal == "recovery" else ""
    )

    system = (
        "You are Steve – an intelligent, data-driven recovery assistant. "
        "Create a Monday-Sunday checklist titled 'Your Next Week Routine'. "
        "Choose 3-5 habits from the goal catalogue. "
        "Habits are identical daily **except** any sauna/ice-bath items (place them on 3 days only). "
        "Time habits between avg_wake and avg_sleep-1 h, respecting fasting. "
        "Set caffeine cut-off exactly 10 h before avg_sleep. "
        f"Set fitness_session.type to '{most_common_sport}' unless macro_goal is cardio. "
        f"Schedule sessions near {typical}; warm-up 10 min before and stretch 5 min after. "
        f"{cardio_note}{recovery_note}"
        "Return STRICT JSON only – no commentary."
    )
    schema = '{"week_title":"Your Next Week Routine","daily_plan":[{"day":"Monday","checklist":[{"habit":"Example","time":"08:30"}],"fitness_session":{"type":"Zone-2","duration_min":30,"start_time":"18:00"}}]}'
    user = (
        f"Profile:\n{json.dumps(profile, indent=2)}\n\n"
        f"Daily summary:\n{json.dumps(daily, indent=2)}\n\n"
        f"Workout summary:\n{json.dumps(workout, indent=2)}\n\n"
        f"Habits for {goal}:\n{json.dumps(habits, indent=2)}\n\n"
        f"Schema (do NOT copy content):\n{schema}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]

# ---------------------------------------------------------------------------
# OpenAI call
# ---------------------------------------------------------------------------
def call_openai(msgs: List[Dict[str, str]], model: str, temp: float) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not client.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    resp = client.chat.completions.create(model=model, messages=msgs, temperature=temp)
    return resp.choices[0].message.content.strip()

# ---------------------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(description="Generate 1-week routine")
    p.add_argument("--profile", required=True)
    p.add_argument("--daily", required=True)
    p.add_argument("--workout", required=True)
    p.add_argument("--window", type=int, default=7)
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--out")
    args = p.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    daily_df = load_daily(args.daily)
    workout_df = load_workout(args.workout)
    tz_off = (
        daily_df["timezone_offset"].mode().iloc[0]
        if "timezone_offset" in daily_df.columns and daily_df["timezone_offset"].notna().any()
        else None
    )
    daily_sum = summarise_daily(daily_df, args.window)
    workout_sum = summarise_workouts(workout_df, args.window, tz_off)

    prompt = build_prompt(profile, daily_sum, workout_sum)
    routine_json = call_openai(prompt, args.model, args.temperature)

    print(routine_json)
    if args.out:
        Path(args.out).write_text(routine_json, encoding="utf-8")
        print(f"Saved to {args.out}")

if __name__ == "__main__":
    main()
