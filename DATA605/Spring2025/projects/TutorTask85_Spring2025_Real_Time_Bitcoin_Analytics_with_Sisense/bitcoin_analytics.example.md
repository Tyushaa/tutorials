# Bitcoin Analysis Example

This example demonstrates how to use the `bitcoin_analysis_utils` module to fetch historical and real-time Bitcoin price data, compute technical indicators, visualize the data, and save the results for further analysis.

## Prerequisites

- Python 3.x installed
- Required libraries: `pandas`, `matplotlib`, `requests`, `sqlalchemy`, `statsmodels`, `python-dotenv`
- An API key from [CryptoCompare](https://min-api.cryptocompare.com/)
- A SQL database set up with the necessary tables (optional, if using database functions from `bitcoin_analysis_utils.py`)

## Setup

Before running the example, ensure that your environment variables are set correctly. You need to have `API_KEY` and `DATABASE_URL` defined in a `.env` file or through other means.

```bash
# Example .env file
API_KEY=your_cryptocompare_api_key
DATABASE_URL=postgresql://user:password@host:port/dbname
```

Load the environment variables using `dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Fetching Historical Data

Use the `fetch_full_historical_days` function from `bitcoin_analysis_utils` to retrieve daily Bitcoin price data for the past 60 days.

```python
import pandas as pd
import bitcoin_analysis_utils as utils

# Fetch 60 days of historical daily data
btc_hist = utils.fetch_full_historical_days(total_days=60)

# Rename columns to match expected names if necessary
btc_hist = btc_hist.rename(columns={'close_usd': 'close'})
```

**Note**: The notebook uses `fetch_historical_data`, but the provided `bitcoin_analysis_utils.py` defines `fetch_full_historical_days`. This example uses the latter, assuming it provides the required OHLCV data. Adjust column names as needed based on your implementation.

## Computing Technical Indicators

Compute the following technical indicators:
- Simple Moving Averages (SMA) for 20 and 50 days
- Relative Strength Index (RSI) with a 14-day window
- Bollinger Bands (20-day SMA ± 2 standard deviations)

Since the utils file doesn't define `calculate_sma`, `calculate_rsi`, or `calculate_bollinger_bands` as used in the notebook, we'll implement simple versions here or assume they are added to the utils module. For this example, we'll use the existing `compute_rsi` and `compute_bollinger_bands` and define a basic SMA function.

```python
# Define a simple SMA function (add this to bitcoin_analysis_utils.py if not present)
def calculate_sma(series, window):
    return series.rolling(window=window).mean()

# Calculate 20-day and 50-day SMAs
btc_hist['SMA20'] = calculate_sma(btc_hist['close'], window=20)
btc_hist['SMA50'] = calculate_sma(btc_hist['close'], window=50)

# Calculate RSI (14) using the provided compute_rsi
btc_hist['RSI14'] = utils.compute_rsi(btc_hist.rename(columns={'close': 'price_usd'}), window=14)

# Calculate Bollinger Bands using the provided compute_bollinger_bands
bb = utils.compute_bollinger_bands(btc_hist.rename(columns={'close': 'price_usd'}), window=20, num_std=2)
btc_hist['BB_upper'] = bb['bb_upper']
btc_hist['BB_lower'] = bb['bb_lower']
```

**Note**: The `compute_rsi` and `compute_bollinger_bands` functions expect a column named `price_usd`, so we temporarily rename `close` to match. Update `bitcoin_analysis_utils.py` to include `calculate_sma` or adjust the column names in the existing functions for consistency.

## Plotting the Data

Use `matplotlib` to plot the closing price along with the SMAs and Bollinger Bands, and separately plot the RSI.

```python
import matplotlib.pyplot as plt

# Set plotting defaults
plt.rcParams.update({'figure.figsize': (12, 6), 'grid.linestyle': '--', 'grid.alpha': 0.6})

# Plot price with SMAs and Bollinger Bands
plt.figure()
plt.plot(btc_hist['close'], label='Close Price')
plt.plot(btc_hist['SMA20'], label='SMA 20')
plt.plot(btc_hist['SMA50'], label='SMA 50')
plt.fill_between(
    btc_hist.index,
    btc_hist['BB_lower'],
    btc_hist['BB_upper'],
    alpha=0.2,
    label='Bollinger Bands'
)
plt.title('Bitcoin Price with SMAs and Bollinger Bands')
plt.legend()
plt.tight_layout()
plt.show()

# Plot RSI
plt.figure()
plt.plot(btc_hist['RSI14'], label='RSI (14)')
plt.axhline(70, linestyle='--', label='Overbought (70)')
plt.axhline(30, linestyle='--', label='Oversold (30)')
plt.title('Relative Strength Index')
plt.legend()
plt.tight_layout()
plt.show()
```

## Streaming Real-Time Data

Demonstrate streaming of live Bitcoin price data for a short duration. Since `stream_realtime_price` is not defined in the provided utils file, we'll assume it's implemented or provide a placeholder.

```python
stream_duration = 60  # seconds
def on_update(data_point):
    timestamp, price = data_point
    print(f"{timestamp} - Price: ${price:.2f}")

# Placeholder for streaming function (implement in bitcoin_analysis_utils.py)
# utils.stream_realtime_price(
#     symbol="bitcoin",
#     duration_seconds=stream_duration,
#     callback=on_update
# )
```

**Note**: To fully implement this section, add a `stream_realtime_price` function to `bitcoin_analysis_utils.py` using the CryptoCompare API's real-time endpoints or WebSocket, if available.

## Saving Outputs

Save the historical data with computed indicators to a CSV file.

```python
output_path = "bitcoin_analytics_output.csv"
btc_hist.to_csv(output_path)
print(f"Historical data with indicators saved to {output_path}")
```

## Conclusion

This example showcases how to leverage the `bitcoin_analysis_utils` module to fetch, analyze, and visualize Bitcoin price data. By following these steps, users can integrate these utilities into their own applications or analyses. To enhance this example, implement missing functions like `stream_realtime_price` and ensure consistency between function names and column names across the notebook and utils module.
