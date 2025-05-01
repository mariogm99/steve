#!/usr/bin/env python3
'''fetch_whoop_data.py – download your WHOOP data to local CSV/JSON files

Every single line is annotated so you can see exactly what is happening.
You already ran `onetime.py` to create the refresh token; this script re‑uses it
and pulls the cycles, sleep, recovery and workout collections + your profile.
'''

# ---------------------------------------------------------------------------
# Standard‑library imports
# ---------------------------------------------------------------------------
from __future__ import annotations            # Enables forward references in type hints

import argparse                               # Command‑line argument parsing
import json                                   # Reading/writing JSON files
from datetime import date                     # Handy date object (no time‑of‑day)
from pathlib import Path                      # OO wrapper around file paths
from typing import Callable, Dict             # Type‑hint shorthands for mappings/callables

# ---------------------------------------------------------------------------
# Third‑party imports
# ---------------------------------------------------------------------------
import pandas as pd                           # DataFrame powerhouse used for CSV export
from dateutil import parser as dateparser     # Robust ISO‑8601 → datetime converter
from tqdm import tqdm                         # Pretty progress bars in the terminal
from whoopy import WhoopClient                # Lightweight Python wrapper around WHOOP API v1

# ---------------------------------------------------------------------------
# Constants – tweak if your folder layout is different
# ---------------------------------------------------------------------------
CONF_PATH = Path('config.json')               # Holds client_id / client_secret / redirect_uri
TOKEN_PATH = Path('.tokens/token.json')       # Refresh + access token cache created by onetime.py

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def iso_date(value: str) -> str:
    '''argparse type‑checker that guarantees YYYY‑MM‑DD strings.'''
    try:
        # • dateparser.isoparse returns a full datetime – we only want the date part
        # • .date() strips any time‑of‑day component (should be midnight anyway)
        # • .isoformat() gives the canonical 'YYYY‑MM‑DD' text we pass to the API
        return dateparser.isoparse(value).date().isoformat()
    except Exception as exc:                  # Any parsing failure ends up here
        # argparse expects an ArgumentTypeError to signal invalid custom types
        raise argparse.ArgumentTypeError(f'Not a valid YYYY‑MM‑DD date: {value}') from exc


def get_client() -> WhoopClient:
    '''Instantiate an authenticated WhoopClient from the stored token.'''
    # --- 1) Load the OAuth client credentials --------------------------------
    conf = json.loads(CONF_PATH.read_text())  # Reads the whole JSON file

    # --- 2) Build a WhoopClient tied to that token ---------------------------
    client = WhoopClient.from_token(
        TOKEN_PATH,                           # Where the access + refresh tokens live
        conf['client_id'],                    # > pulled from config.json
        conf['client_secret'],                # > pulled from config.json
    )

    # --- 3) Silently refresh if the access token is near expiry -------------
    try:
        client.refresh()                      # No‑op if token is still valid
        client.store_token(TOKEN_PATH)        # Persist new access/refresh pair if rotated
    except Exception:                         # No refresh permission or still valid
        pass                                  # Either way we can keep using *client*

    return client


def export_dataframe(df: pd.DataFrame, path: Path) -> None:
    '''Write *df* to *path* as CSV and log what happened.'''
    path.parent.mkdir(parents=True, exist_ok=True)  # Make sure output folder exists
    df.to_csv(path, index=False)                    # Dump DataFrame → disk, no index column

    # Log the number of rows and a tidy relative path (fallback to absolute)
    try:
        rel = path.relative_to(Path.cwd())          # Only works if *path* is under CWD
    except ValueError:
        rel = path                                  # Otherwise show the full path
    print(f'Wrote {len(df):,} rows ➜ {rel}')        # Comma‑separated row count for clarity


# ---------------------------------------------------------------------------
# Script entry‑point
# ---------------------------------------------------------------------------

def main() -> None:  # noqa: C901 (it is a tad long, but splitting would harm readability)
    # --- 1) Parse CLI arguments ---------------------------------------------
    parser = argparse.ArgumentParser(
        description='Download WHOOP cycles, sleep, recovery, workout data',
    )
    parser.add_argument('--start', type=iso_date, help='Start date (YYYY‑MM‑DD)')
    parser.add_argument('--end',   type=iso_date, help='End date (YYYY‑MM‑DD)')
    parser.add_argument('--outdir', default='whoop_exports',
                        help='Output directory (default: %(default)s)')
    args = parser.parse_args()                 # Actually read sys.argv

    # --- 2) Resolve date window and output dir ------------------------------
    start_date = args.start or date.today().replace(day=1).isoformat()  # 1st of current month
    end_date   = args.end   or date.today().isoformat()                 # Today
    outdir     = Path(args.outdir).expanduser()                         # Handle ~/ shortcuts

    # --- 3) Get authenticated API client -----------------------------------
    client = get_client()

    # --- 4) Inform the user what is about to happen -------------------------
    print(f'Fetching WHOOP data {start_date} – {end_date} …')

    # --- 5) Build a mapping of endpoint name → callable that returns DataFrame
    calls: Dict[str, Callable[[], pd.DataFrame]] = {
        # Each lambda immediately calls the corresponding WhoopClient collection helper
        'cycles':   lambda: client.cycle.collection_df(start=start_date, end=end_date)[0],
        'sleep':    lambda: client.sleep.collection_df(start=start_date, end=end_date)[0],
        'recovery': lambda: client.recovery.collection_df(start=start_date, end=end_date)[0],
        'workout':  lambda: client.workout.collection_df(start=start_date, end=end_date)[0],
    }

    # --- 6) Iterate over all endpoints with a progress bar ------------------
    for name, fn in tqdm(calls.items(), total=len(calls), unit='endpoint'):
        df = fn()                               # Hit the API + convert to pandas
        if df.empty:                           # No rows returned → nothing to save
            print(f'No {name} data in range – skipping')
            continue
        export_dataframe(df,                   # Persist to CSV
                          outdir / f'{name}_{start_date}_to_{end_date}.csv')

    # --- 7) Dump profile (not date‑scoped) ----------------------------------
    raw_profile = client.user.profile()         # Might return Pydantic / dataclass etc.

    def _to_jsonable(obj):                     # Local helper: recurse → pure JSON types
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj                         # Already JSON‑serialisable
        if isinstance(obj, (list, tuple, set)):
            return [_to_jsonable(i) for i in obj]
        if isinstance(obj, dict):
            return {k: _to_jsonable(v) for k, v in obj.items()}
        for attr in ('dict', 'model_dump', 'to_dict'):
            if hasattr(obj, attr):             # Handle dataclass/Pydantic nicely
                return _to_jsonable(getattr(obj, attr)())
        if hasattr(obj, '__dict__'):
            return _to_jsonable(vars(obj))     # Generic Python object fallback
        return str(obj)                        # Last resort – string repr

    # Write the cleaned‑up profile JSON
    (outdir / 'profile.json').write_text(
        json.dumps(_to_jsonable(raw_profile), indent=2, ensure_ascii=False)
    )
    print('Saved profile.json')

    # --- 8) All done! -------------------------------------------------------
    print('🎉 All done!')


# Python convention: run main() only if executed directly, not when imported
if __name__ == '__main__':
    main()
