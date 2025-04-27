#!/usr/bin/env python3
"""
fetch_whoop_data.py – pull your WHOOP data to local CSV/JSON files

Usage examples:
    python fetch_whoop_data.py                      # current‑month‑to‑today
    python fetch_whoop_data.py --start 2025-03-25 --end 2025-04-25
    python fetch_whoop_data.py --outdir my_whoop_dump

Requirements:
    pip install whoopy pandas python-dateutil tqdm

Folder structure assumed:
    project/
      config.json          # client_id/client_secret/redirect_uri
      .tokens/token.json   # created by onetime.py
      fetch_whoop_data.py

The script creates <outdir>/ with CSVs for cycles, sleep, recovery, workouts
and a profile.json containing your basic account info.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Callable, Dict

import pandas as pd
from dateutil import parser as dateparser
from tqdm import tqdm
from whoopy import WhoopClient

CONF_PATH = Path("config.json")
TOKEN_PATH = Path(".tokens/token.json")


def iso_date(value: str) -> str:
    """Validate an input string is ISO‑8601 (YYYY‑MM‑DD) and return canonical form."""
    try:
        return dateparser.isoparse(value).date().isoformat()
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError(f"Not a valid YYYY‑MM‑DD date: {value}") from exc


def get_client() -> WhoopClient:
    """Load the persisted token and return an authenticated WhoopClient."""
    conf = json.loads(CONF_PATH.read_text())
    client = WhoopClient.from_token(
        TOKEN_PATH,
        conf["client_id"],
        conf["client_secret"],
    )

    # Attempt a silent refresh – if the access token is still valid the call is a no‑op.
    try:
        client.refresh()
        client.store_token(TOKEN_PATH)
    except Exception:  # noqa: BLE001  (token still good or refresh scope missing)
        pass

    return client


def export_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Save *df* to *path* and print a friendly message."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

    # Try to print the path relative to CWD; fall back to absolute if not possible.
    try:
        rel = path.relative_to(Path.cwd())
    except ValueError:
        rel = path
    print(f"Wrote {len(df):,} rows ➜ {rel}")


def main() -> None:  # noqa: C901  (slightly long but readable)
    parser = argparse.ArgumentParser(description="Download WHOOP cycles, sleep, recovery, and workout data")
    parser.add_argument("--start", type=iso_date, help="Start date (YYYY‑MM‑DD)")
    parser.add_argument("--end", type=iso_date, help="End date (YYYY‑MM‑DD)")
    parser.add_argument("--outdir", default="whoop_exports", help="Output directory (default: %(default)s)")
    args = parser.parse_args()

    start_date = args.start or date.today().replace(day=1).isoformat()
    end_date = args.end or date.today().isoformat()
    outdir = Path(args.outdir).expanduser()

    client = get_client()

    print(f"Fetching WHOOP data {start_date} – {end_date} …")

    # Friendly name → function that returns a DataFrame
    calls: Dict[str, Callable[[], pd.DataFrame]] = {
        "cycles":   lambda: client.cycle.collection_df(start=start_date, end=end_date)[0],
        "sleep":    lambda: client.sleep.collection_df(start=start_date, end=end_date)[0],
        "recovery": lambda: client.recovery.collection_df(start=start_date, end=end_date)[0],
        "workout":  lambda: client.workout.collection_df(start=start_date, end=end_date)[0],
    }

    for name, fn in tqdm(calls.items(), total=len(calls), unit="endpoint"):
        df = fn()
        if df.empty:
            print(f"No {name} data in range – skipping")
            continue
        export_dataframe(df, outdir / f"{name}_{start_date}_to_{end_date}.csv")

    # profile endpoint is not time‑bound → JSON dump
    # --- Serialize profile object (may be Pydantic, dataclass, or plain dict) ---
    raw_profile = client.user.profile()

    def _to_jsonable(obj):
        """Recursively turn *obj* into something that ``json.dumps`` accepts."""
        # Primitive types are fine
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        # Containers
        if isinstance(obj, (list, tuple, set)):
            return [_to_jsonable(i) for i in obj]
        if isinstance(obj, dict):
            return {k: _to_jsonable(v) for k, v in obj.items()}
        # Dataclass / Pydantic / attrs / anything with .dict() or .model_dump()
        for attr in ("dict", "model_dump", "to_dict"):
            if hasattr(obj, attr):
                return _to_jsonable(getattr(obj, attr)())
        # Fallback to __dict__ if available
        if hasattr(obj, "__dict__"):
            return _to_jsonable(vars(obj))
        # Last resort: string representation
        return str(obj)

    (outdir / "profile.json").write_text(
        json.dumps(_to_jsonable(raw_profile), indent=2, ensure_ascii=False)
    )
    print("Saved profile.json")

    print("🎉 All done!")


if __name__ == "__main__":
    main()
