# Bitcoin_Analysis.API.md

Introduction

This document describes the API layer built on top of the CryptoCompare API for fetching and analyzing Bitcoin (BTC/USD) price data. The software layer provides utilities for fetching historical and real-time data, storing it in a SQL database, and performing time-series forecasting and technical analysis.

---

## Native API Documentation

# The native API used is the CryptoCompare API, which provides historical and real-time data for cryptocurrencies.

### Endpoints Used

### Minute-Level Data

- **URL**: `https://min-api.cryptocompare.com/data/v2/histominute`
- **Parameters**:
  - `fsym`: From symbol (e.g., "BTC")
  - `tsym`: To symbol (e.g., "USD")
  - `limit`: Number of data points to return
  - `toTs`: Optional timestamp to return data up to
- **Response**: JSON object containing an array of minute-level data points with fields such as `time`, `close`, `volumeto`, etc.

#### Daily-Level Data

- **URL**: `https://min-api.cryptocompare.com/data/v2/histoday`
- **Parameters**:
  - `fsym`: From symbol (e.g., "BTC")
  - `tsym`: To symbol (e.g., "USD")
  - `limit`: Number of data points to return
  - `toTs`: Optional timestamp to return data up to
- **Response**: JSON object containing an array of daily data points with fields such as `time`, `open`, `high`, `low`, `close`, `volumeto`, etc.

For more details, refer to the CryptoCompare API documentation.

---

## Software Layer Documentation

The software layer is implemented in `bitcoin_analytics_utils.py` and provides utilities for data fetching, database operations, time-series forecasting, and technical indicator calculations.

### Data Fetching

- `fetch_minute_data(limit: int, to_ts: int = None) -> pd.DataFrame`\
  Fetches a chunk of minute-level BTC/USD bars.

  - **Parameters**:
    - `limit`: Number of minutes to fetch.
    - `to_ts`: Optional timestamp to fetch data up to.
  - **Returns**: A pandas DataFrame with columns `timestamp`, `price_usd`, `volume_usd`, `volume_btc`.

- `fetch_full_historical_minutes() -> pd.DataFrame`\
  Backfills historical minute data for the past `HISTORICAL_DAYS` days (default: 2 days).

  - **Returns**: A pandas DataFrame with the historical minute data.

- `fetch_realtime_minutes() -> pd.DataFrame`\
  Fetches the last `REALTIME_LIMIT` minutes of data (default: 1440 minutes).

  - **Returns**: A pandas DataFrame with the recent minute data.

- `fetch_daily_data(limit: int, to_ts: int = None) -> pd.DataFrame`\
  Fetches a chunk of daily BTC/USD bars.

  - **Parameters**:
    - `limit`: Number of days to fetch.
    - `to_ts`: Optional timestamp to fetch data up to.
  - **Returns**: A pandas DataFrame with columns `date`, `open_usd`, `high_usd`, `low_usd`, `close_usd`, `volume_usd`.

- `fetch_full_historical_days(total_days: int) -> pd.DataFrame`\
  Backfills historical daily data for the specified number of days.

  - **Parameters**:
    - `total_days`: Number of days to backfill.
  - **Returns**: A pandas DataFrame with the historical daily data.

### Database Operations

- `ensure_minute_table()`\
  Creates and backfills the minute data table (`btc_minute_data`) if it doesn't exist in the database, using `HISTORICAL_DAYS` of data.

- `update_minute_table()`\
  Fetches new minute bars, appends them to the database, and prunes old rows to keep only the most recent `MAX_ROWS` (default: 2000).

- `ensure_daily_table()`\
  Creates and backfills the daily data table (`btc_daily_data`) if it doesn't exist, defaulting to 365 days of historical data.

- `update_daily_table()`\
  Fetches the latest daily bar and appends it to the database if it's new.

### Time-Series Forecasting

- `load_daily_from_db(table: str = DAILY_TABLE) -> pd.Series`\
  Loads the daily closing prices from the specified database table.

  - **Parameters**:
    - `table`: Name of the daily data table (default: `btc_daily_data`).
  - **Returns**: A pandas Series of closing prices indexed by date.

- `fit_sarimax(endog: pd.Series, order=(1,1,1), seasonal_order=(0,0,0,0))`\
  Fits a SARIMAX model to the provided time series.

  - **Parameters**:
    - `endog`: The time series to model.
    - `order`: The (p,d,q) order of the model (default: (1,1,1)).
    - `seasonal_order`: The (P,D,Q,s) seasonal order (default: (0,0,0,0)).
  - **Returns**: A fitted SARIMAX results object.

- `forecast_sarimax(results, steps: int) -> pd.DataFrame`\
  Generates a forecast DataFrame from the fitted SARIMAX model.

  - **Parameters**:
    - `results`: The fitted SARIMAX results object.
    - `steps`: Number of steps to forecast.
  - **Returns**: A pandas DataFrame with forecast mean and confidence intervals.

### Technical Indicators

- `compute_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame`\
  Computes the MACD, signal line, and histogram.

  - **Parameters**:
    - `df`: DataFrame with `price_usd` column.
    - `fast`: Fast EMA period (default: 12).
    - `slow`: Slow EMA period (default: 26).
    - `signal`: Signal line EMA period (default: 9).
  - **Returns**: A DataFrame with `macd`, `signal`, and `histogram` columns.

- `compute_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: int = 2) -> pd.DataFrame`\
  Computes Bollinger Bands.

  - **Parameters**:
    - `df`: DataFrame with `price_usd` column.
    - `window`: Rolling window size (default: 20).
    - `num_std`: Number of standard deviations for the bands (default: 2).
  - **Returns**: A DataFrame with `bb_mean`, `bb_upper`, and `bb_lower` columns.

- `compute_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series`\
  Computes the Relative Strength Index (RSI).

  - **Parameters**:
    - `df`: DataFrame with `price_usd` column.
    - `window`: Period for RSI calculation (default: 14).
  - **Returns**: A Series with RSI values.

---

## Database Schema

The database contains two tables:

### `btc_minute_data`

- `timestamp`: TIMESTAMP (primary key)
- `price_usd`: FLOAT
- `volume_usd`: FLOAT
- `volume_btc`: FLOAT

### `btc_daily_data`

- `date`: DATE (primary key)
- `open_usd`: FLOAT
- `high_usd`: FLOAT
- `low_usd`: FLOAT
- `close_usd`: FLOAT
- `volume_usd`: FLOAT

---

## Time-Series Forecasting

The software layer provides functions to fit a SARIMAX model to the daily closing prices and generate forecasts. The `fit_sarimax` function allows specifying the model order and seasonal order, while `forecast_sarimax` generates a forecast for a specified number of steps.

---

## Technical Indicators

The software layer includes functions to compute common technical indicators:

- **MACD**: Moving Average Convergence Divergence, useful for identifying trends and momentum.
- **Bollinger Bands**: Volatility bands placed above and below a moving average, indicating overbought or overssold conditions.
- **RSI**: Relative Strength Index, a momentum oscillator that measures the speed and change of price movements.

These indicators can be computed on any DataFrame containing a `price_usd` column, typically the minute-level or daily data fetched from the API or database.

---

## Usage Examples

For detailed usage examples, refer to the accompanying Jupyter notebook `bitcoin_analytics.API.ipynb`, which demonstrates how to use these functions to fetch data, update the database, and perform analyses.
