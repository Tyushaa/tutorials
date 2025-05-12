import os
import time
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# LOAD ENV VARS 
load_dotenv()  # pip install python-dotenv
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY:
    raise EnvironmentError("API_KEY missing. Define it in your .env file.")
if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL missing. Define it in your .env file.")

# Fix for SQLAlchemy ≥1.4
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False, future=True)

# CONFIG 
TABLE_NAME        = "btc_minute_data123"
HISTORICAL_DAYS   = 7
HISTORICAL_MIN    = HISTORICAL_DAYS * 24 * 60  # total minutes to fetch initially
HISTORICAL_CHUNK  = 2000                      # max per-request limit
REALTIME_LIMIT    = 24 * 60                   # last 24h, single request
MAX_ROWS          = 2000

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histominute"
HEADERS  = {"authorization": f"Apikey {API_KEY}"}

# FETCHING UTILITIES 
def fetch_chunk(limit: int, to_ts: int = None) -> list:
    params = {"fsym": "BTC", "tsym": "USD", "limit": limit}
    if to_ts:
        params["toTs"] = to_ts

    r = requests.get(BASE_URL, params=params, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    if data.get("Response") != "Success":
        raise RuntimeError(f"API Error: {data.get('Message', 'Unknown')}")
    return data["Data"]["Data"]


def fetch_full_historical(total_minutes: int) -> pd.DataFrame:
    to_ts = int(time.time())
    left = total_minutes
    bars = []

    while left > 0:
        batch_size = min(HISTORICAL_CHUNK, left)
        chunk = fetch_chunk(batch_size, to_ts)
        if not chunk:
            break
        bars.extend(chunk)
        to_ts = chunk[0]["time"] - 1
        left -= batch_size
        time.sleep(0.2)

    df = pd.DataFrame(bars)
    df["timestamp"]  = pd.to_datetime(df["time"], unit="s")
    df["price_usd"]  = df["close"]
    df["volume_usd"] = df["volumeto"]
    df["volume_btc"] = df["volumefrom"]

    return (
        df[["timestamp", "price_usd", "volume_usd", "volume_btc"]]
        .drop_duplicates(subset="timestamp")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


def fetch_realtime_df() -> pd.DataFrame:
    bars = fetch_chunk(REALTIME_LIMIT)
    df = pd.DataFrame(bars)
    df["timestamp"]  = pd.to_datetime(df["time"], unit="s")
    df["price_usd"]  = df["close"]
    df["volume_usd"] = df["volumeto"]
    df["volume_btc"] = df["volumefrom"]
    return df[["timestamp", "price_usd", "volume_usd", "volume_btc"]]


# DATABASE UTILITIES 
def ensure_table_exists():
    insp = inspect(engine)
    if not insp.has_table(TABLE_NAME):
        print(f"Table '{TABLE_NAME}' not found—inserting initial {HISTORICAL_DAYS}-day history…")
        df0 = fetch_full_historical(HISTORICAL_MIN)
        df0.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)
        print(f"  → Inserted {len(df0)} rows into '{TABLE_NAME}'.")
    else:
        print(f"Table '{TABLE_NAME}' already exists, skipping initial load.")


def prune_old_rows(conn):
    total = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar_one()
    if total > MAX_ROWS:
        to_delete = total - MAX_ROWS
        conn.execute(text(f"""
            DELETE FROM {TABLE_NAME}
            WHERE ctid IN (
                SELECT ctid
                FROM {TABLE_NAME}
                ORDER BY timestamp ASC
                LIMIT :n
            )
        """), {"n": to_delete})
        conn.commit()
        print(f"  🔪 Pruned {to_delete} old rows; now {MAX_ROWS} rows remain.")


# MAIN LOOP 
def main():
    ensure_table_exists()

    print("⏱️  Entering realtime update loop (every 60s)…")
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] Fetching last 24h of bars…", end=" ")

        new_df = fetch_realtime_df()

        with engine.begin() as conn:
            # get latest timestamp in DB
            result = conn.execute(text(f"SELECT MAX(timestamp) FROM {TABLE_NAME}"))
            max_ts = result.scalar_one()
            if max_ts is not None:
                new_df = new_df[new_df["timestamp"] > max_ts]

            if not new_df.empty:
                new_df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
                # dedupe any overlapping timestamps
                conn.execute(text(f"""
                    DELETE FROM {TABLE_NAME} a
                    USING {TABLE_NAME} b
                    WHERE a.timestamp = b.timestamp
                      AND a.ctid < b.ctid
                """))
                prune_old_rows(conn)
                print(f"Appended {len(new_df)} new rows.")
            else:
                print("No new bars to append.")

        time.sleep(60)


if __name__ == "__main__":
    main()