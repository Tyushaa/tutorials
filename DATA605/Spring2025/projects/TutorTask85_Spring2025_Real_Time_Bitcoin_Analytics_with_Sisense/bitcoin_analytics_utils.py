# bitcoin_analysis_utils.py

import os
import time
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from statsmodels.tsa.statespace.sarimax import SARIMAX

#  LOAD ENVIRONMENT VARIABLES 
load_dotenv()
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY:
    raise EnvironmentError("API_KEY missing.")
if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL missing.")

# SQLAlchemy needs the new prefix
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False, future=True)

# CONFIGURATION 
# Minute‑level data
MINUTE_TABLE = "btc_minute_data_new_1"
HISTORICAL_DAYS = 2
HISTORICAL_MINUTES = HISTORICAL_DAYS * 24 * 60
HISTORICAL_CHUNK = 2000
REALTIME_LIMIT = 24 * 60
MAX_ROWS = 2000
MINUTE_URL = "https://min-api.cryptocompare.com/data/v2/histominute"

# Daily‑level data
DAILY_TABLE = os.getenv("BTC_DAILY_TABLE", "btc_daily_data")
HISTORICAL_DAY_CHUNK = int(os.getenv("BTC_HISTORICAL_DAY_CHUNK", 2000))
DAILY_URL = "https://min-api.cryptocompare.com/data/v2/histoday"

HEADERS = {"authorization": f"Apikey {API_KEY}"}


# FETCHING HELPERS 
def _fetch_chunk(endpoint: str, params: dict) -> list:
    """Internal helper to fetch one chunk from CryptoCompare."""
    resp = requests.get(endpoint, params=params, headers=HEADERS)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("Response") != "Success":
        raise RuntimeError(f"API Error: {payload.get('Message', 'Unknown')}")
    return payload["Data"]["Data"]


# Minute data
def fetch_minute_data(limit: int, to_ts: int = None) -> pd.DataFrame:
    """Fetch a chunk of minute‑level BTC/USD bars."""
    params = {"fsym": "BTC", "tsym": "USD", "limit": limit}
    if to_ts:
        params["toTs"] = to_ts
    raw = _fetch_chunk(MINUTE_URL, params)
    df = pd.DataFrame(raw).rename(
        columns={
            "time": "timestamp_sec",
            "close": "price_usd",
            "volumeto": "volume_usd",
            "volumefrom": "volume_btc",
        }
    )
    df["timestamp"] = pd.to_datetime(df["timestamp_sec"], unit="s")
    return df[["timestamp", "price_usd", "volume_usd", "volume_btc"]]


def fetch_full_historical_minutes() -> pd.DataFrame:
    """Backfill HISTORICAL_DAYS of minute data in batches."""
    to_ts = int(time.time())
    remaining = HISTORICAL_MINUTES
    chunks = []

    while remaining > 0:
        batch = min(HISTORICAL_CHUNK, remaining)
        chunk = fetch_minute_data(batch, to_ts)
        if chunk.empty:
            break
        chunks.append(chunk)
        # use the earliest timestamp of this chunk
        to_ts = int(chunk["timestamp"].iloc[0].timestamp()) - 1
        remaining -= batch
        time.sleep(0.2)

    df = pd.concat(chunks, ignore_index=True)
    df = df.drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    return df


def fetch_realtime_minutes() -> pd.DataFrame:
    """Fetch the last REALTIME_LIMIT minutes of data."""
    return fetch_minute_data(REALTIME_LIMIT)


# Daily data
def fetch_daily_data(limit: int, to_ts: int = None) -> pd.DataFrame:
    """Fetch a chunk of daily BTC/USD bars."""
    params = {"fsym": "BTC", "tsym": "USD", "limit": max(limit - 1, 1)}
    if to_ts:
        params["toTs"] = to_ts
    raw = _fetch_chunk(DAILY_URL, params)
    df = pd.DataFrame(raw).rename(
        columns={
            "time": "timestamp_sec",
            "open": "open_usd",
            "high": "high_usd",
            "low": "low_usd",
            "close": "close_usd",
            "volumeto": "volume_usd",
        }
    )
    df["date"] = pd.to_datetime(df["timestamp_sec"], unit="s").dt.date
    return df[["date", "open_usd", "high_usd", "low_usd", "close_usd", "volume_usd"]]


def fetch_full_historical_days(total_days: int) -> pd.DataFrame:
    """Backfill total_days of daily data in batches."""
    to_ts = int(time.time())
    days_left = total_days
    chunks = []

    while days_left > 0:
        batch = min(HISTORICAL_DAY_CHUNK, days_left)
        chunk = fetch_daily_data(batch, to_ts)
        if chunk.empty:
            break
        chunks.append(chunk)
        # use the earliest date of this chunk
        earliest = chunk["date"].iloc[0]
        to_ts = int(pd.Timestamp(earliest).timestamp()) - 1
        days_left -= batch
        time.sleep(0.2)

    df = pd.concat(chunks, ignore_index=True)
    df = df.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    return df


# ── DATABASE HELPERS 
def ensure_minute_table():
    """Create and backfill the minute table if it doesn’t exist."""
    insp = inspect(engine)
    if not insp.has_table(MINUTE_TABLE):
        df = fetch_full_historical_minutes()
        df.to_sql(MINUTE_TABLE, engine, if_exists="replace", index=False)


def update_minute_table():
    """Fetch new minute bars and append them to the DB, then prune."""
    ensure_minute_table()
    new_df = fetch_realtime_minutes()
    with engine.begin() as conn:
        max_ts = conn.execute(
            text(f"SELECT MAX(timestamp) FROM {MINUTE_TABLE}")
        ).scalar_one()
        if max_ts:
            new_df = new_df[new_df["timestamp"] > max_ts]
        if not new_df.empty:
            new_df.to_sql(MINUTE_TABLE, conn, if_exists="append", index=False)
            # dedupe overlapping rows
            conn.execute(
                text(
                    f"""
                DELETE FROM {MINUTE_TABLE} a
                USING {MINUTE_TABLE} b
                WHERE a.timestamp = b.timestamp
                  AND a.ctid < b.ctid
            """
                )
            )
            # prune to MAX_ROWS
            total = conn.execute(
                text(f"SELECT COUNT(*) FROM {MINUTE_TABLE}")
            ).scalar_one()
            if total > MAX_ROWS:
                n = total - MAX_ROWS
                conn.execute(
                    text(
                        f"""
                    DELETE FROM {MINUTE_TABLE}
                    WHERE ctid IN (
                        SELECT ctid FROM {MINUTE_TABLE} ORDER BY timestamp ASC LIMIT :n
                    )
                """
                    ),
                    {"n": n},
                )


def ensure_daily_table():
    """Create and backfill the daily table if it doesn’t exist."""
    insp = inspect(engine)
    if not insp.has_table(DAILY_TABLE):
        # default to 365 days if you like, or require caller to specify.
        df = fetch_full_historical_days(total_days=365)
        df.to_sql(DAILY_TABLE, engine, if_exists="replace", index=False)


def update_daily_table():
    """Fetch the latest daily bar and append if new."""
    ensure_daily_table()
    # get just the most recent day
    last_row = fetch_daily_data(1)
    with engine.begin() as conn:
        max_date = conn.execute(
            text(f"SELECT MAX(date) FROM {DAILY_TABLE}")
        ).scalar_one()
        if pd.to_datetime(last_row["date"].iloc[-1]).date() > max_date:
            last_row.to_sql(DAILY_TABLE, conn, if_exists="append", index=False)


#  TIME‑SERIES FORECASTING 
def load_daily_from_db(table: str = DAILY_TABLE) -> pd.Series:
    """Load daily close_usd series from your DB."""
    df = pd.read_sql(
        text(f"SELECT date, close_usd FROM {table} ORDER BY date"),
        engine,
        parse_dates=["date"],
    )
    df.set_index("date", inplace=True)
    return df["close_usd"]


def fit_sarimax(endog: pd.Series, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0)):
    """Fit and return a SARIMAX results object."""
    model = SARIMAX(
        endog,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    results = model.fit(disp=False)
    return results


# def forecast_sarimax(results, steps: int) -> pd.DataFrame:
#     """Produce a forecast DataFrame (mean, ci_lower, ci_upper, etc.)."""
#     fc = results.get_forecast(steps=steps)
#     df = fc.summary_frame(alpha=0.05)
#     last_date      = results.data.endog.index.max()
#     future_index   = pd.date_range(start=last_date + pd.Timedelta(days=1),
#                                    periods=steps, freq="D")
#     df.index       = future_index
#     return df


def forecast_sarimax(results, steps: int) -> pd.DataFrame:
    """Produce a forecast DataFrame (mean, ci_lower, ci_upper, etc.)."""
    # 0) make sure pandas is available locally
    import pandas as pd

    # 1) get the forecast object & summary frame
    fc = results.get_forecast(steps=steps)
    df = fc.summary_frame(alpha=0.05)

    # 2) pull last observed date, with a fallback for older statsmodels
    try:
        # modern statsmodels
        last_date = results.model.data.dates.max()
    except AttributeError:
        # older statsmodels (<0.14) keep dates in `results.data.row_labels`
        last_date = pd.to_datetime(results.data.row_labels).max()

    # 3) build a future date index, one‑day frequency
    future_index = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=steps,
        freq="D"
    )

    # 4) assign it and return
    df.index = future_index
    return df


