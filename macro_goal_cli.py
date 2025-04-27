#!/usr/bin/env python3
"""
macro_goal_cli.py – Minimal command‑line tool for capturing a user’s macro‑goal
selection and supplementary inputs during early Steve MVP testing.

Usage (all flags optional; will fall back to interactive prompts):
---------------------------------------------------------------
$ python macro_goal_cli.py --macro-goal sleep \
                           --frequency 4 \
                           --exercise-type cardio \
                           --fasting \
                           --avg-sleep 23:00 \
                           --avg-wake 07:00

Run with -h/--help to see all options. If you omit any option the script will
ask you for it in the terminal.

The collected data are printed as JSON to stdout and exit code 0. You can pipe
or redirect the output to a file or another process:

$ python macro_goal_cli.py > user_goal.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import TypedDict

TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class MacroGoalData(TypedDict):
    macro_goal: str  # "sleep" | "recovery" | "cardio"
    frequency: int   # 1–14 (sessions / week)
    exercise_type: str  # "cardio" | "strength" | "mixed"
    fasting: bool
    avg_sleep: str  # HH:MM 24‑hour
    avg_wake: str   # HH:MM 24‑hour


def _valid_time(value: str) -> str:
    if not TIME_PATTERN.match(value):
        raise argparse.ArgumentTypeError(
            f"Time must be in 24‑h HH:MM format (got '{value}')"
        )
    return value


def _positive_int(value: str) -> int:
    ivalue = int(value)
    if ivalue < 1 or ivalue > 14:
        raise argparse.ArgumentTypeError("Frequency must be 1–14 sessions per week")
    return ivalue


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Capture macro‑goal selection and lifestyle inputs.")

    p.add_argument(
        "--macro-goal",
        choices=["sleep", "recovery", "cardio"],
        help="Primary macro goal",
    )
    p.add_argument(
        "--frequency",
        type=_positive_int,
        help="Training frequency (sessions per week, 1‑14)",
    )
    p.add_argument(
        "--exercise-type",
        choices=["cardio", "strength", "mixed"],
        help="Typical exercise focus",
    )
    p.add_argument(
        "--fasting",
        action="store_true",
        help="Enable if the user practices intermittent fasting",
    )
    p.add_argument("--avg-sleep", type=_valid_time, help="Average sleep time, HH:MM 24‑h")
    p.add_argument("--avg-wake", type=_valid_time, help="Average wake time, HH:MM 24‑h")
    return p


def interactive_fill(args: argparse.Namespace):
    """Prompt for missing values via stdin."""
    if args.macro_goal is None:
        choices = {"1": "sleep", "2": "recovery", "3": "cardio"}
        while args.macro_goal is None:
            print("Select primary macro goal:")
            print("  1) Improve Sleep\n  2) Improve Recovery\n  3) Improve Cardiovascular Fitness")
            choice = input("Enter 1‑3: ").strip()
            args.macro_goal = choices.get(choice)

    if args.frequency is None:
        while args.frequency is None:
            value = input("Exercise sessions per week (1‑14): ").strip()
            try:
                args.frequency = _positive_int(value)
            except Exception as e:
                print(e)

    if args.exercise_type is None:
        etype_map = {"1": "cardio", "2": "strength", "3": "mixed"}
        while args.exercise_type is None:
            print("Exercise type:\n  1) Cardio\n  2) Strength\n  3) Mixed")
            choice = input("Enter 1‑3: ").strip()
            args.exercise_type = etype_map.get(choice)

    if not args.fasting:
        resp = input("Intermittent fasting? [y/n]: ").strip().lower()
        args.fasting = resp.startswith("y")

    if args.avg_sleep is None:
        while args.avg_sleep is None:
            value = input("Average sleep time (HH:MM): ").strip()
            try:
                args.avg_sleep = _valid_time(value)
            except Exception as e:
                print(e)
    if args.avg_wake is None:
        while args.avg_wake is None:
            value = input("Average wake time (HH:MM): ").strip()
            try:
                args.avg_wake = _valid_time(value)
            except Exception as e:
                print(e)


def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # Fill missing interactively
    interactive_fill(args)

    data: MacroGoalData = {
        "macro_goal": args.macro_goal,  # type: ignore
        "frequency": args.frequency,    # type: ignore
        "exercise_type": args.exercise_type,  # type: ignore
        "fasting": args.fasting,
        "avg_sleep": args.avg_sleep,    # type: ignore
        "avg_wake": args.avg_wake,      # type: ignore
    }

    os.makedirs("clean_whoop", exist_ok=True)
    with open("clean_whoop/user_goal.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Data saved to user_goal.json")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
