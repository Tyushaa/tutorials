# Real-Time Bitcoin Analytics with Sisense

This project implements a real-time data ingestion and analytics system for Bitcoin using Sisense. It fetches live and historical Bitcoin data from the CryptoCompare API, processes it with Python, stores it in PostgreSQL, and visualizes it through interactive Sisense dashboards to deliver actionable insights, including price trends and forecasts.

## Technologies Used

- **Sisense**: Business intelligence platform for data visualization and analytics.
- **Python**: Core language for data ingestion, processing, and analysis.
- **PostgreSQL**: Database for storing Bitcoin data.
- **CryptoCompare API**: Source for real-time and historical Bitcoin price data.
- **Pandas**: Library for data manipulation and structuring.
- **Statsmodels**: Library for time series analysis and forecasting.
- **SQLAlchemy**: For database interactions in Python.
- **Requests**: For API calls to fetch Bitcoin data.
- **python-dotenv**: For managing environment variables.

## Project Structure

- **`bitcoin_analysis_utils.py`**: Utility module with functions for fetching data from the CryptoCompare API, managing the PostgreSQL database, performing time series forecasting (SARIMAX), and calculating technical indicators (MACD, Bollinger Bands, RSI).
- **`bitcoin_analysis_API.ipynb`**: Jupyter notebook demonstrating how to fetch and process Bitcoin data using the utility functions.
- **`bitcoin_analysis_examples.ipynb`**: Jupyter notebook showcasing examples of data analysis, forecasting, and visualization preparation.

## Data Ingestion

- **Source**: CryptoCompare API provides minute-level and daily-level Bitcoin price data (BTC/USD).
- **Historical Data**: Fetched in chunks (e.g., 2 days of minute data or 365 days of daily data) and stored in PostgreSQL.
- **Real-Time Data**: Periodically fetched (e.g., last 24 hours of minute data) and appended to the database to keep it current.

## Data Processing and Analysis

- **Cleaning and Structuring**: Raw data is processed using Pandas for consistency and usability.
- **Time Series Forecasting**: SARIMAX models from Statsmodels forecast future Bitcoin prices based on historical daily data.
- **Technical Indicators**: Computed indicators include:
  - **MACD**: Moving Average Convergence Divergence for trend analysis.
  - **Bollinger Bands**: Volatility bands around a moving average.
  - **RSI**: Relative Strength Index for momentum insights.

## Visualization in Sisense

- **Dashboards**: Display real-time Bitcoin prices, historical trends, and forecasted prices.
- **Interactivity**: Users can filter by date ranges and compare forecasts with historical data.
- **Data Flow**: Processed data from PostgreSQL is integrated into Sisense for visualization.

## Setup and Installation

1. **Install Dependencies**:

   - Ensure Python 3.8+ is installed.
   - Install required libraries:
     ```
     pip install requests pandas statsmodels sqlalchemy python-dotenv
     ```

2. **Set Up Environment Variables**:

   - Create a `.env` file in the project root with:
     ```
     API_KEY=your_cryptocompare_api_key
     DATABASE_URL=your_postgresql_database_url
     ```
   - Obtain a free API key from [CryptoCompare](https://min-api.cryptocompare.com/).
   - Use a PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/dbname`).

3. **Run the Project**:
   - Start your PostgreSQL database.
   - Open and run `bitcoin_analysis_API.ipynb` to fetch and store data.
   - Use `bitcoin_analysis_examples.ipynb` to analyze data and prepare it for Sisense.
   - Import the processed data into Sisense for dashboard creation.

## Prerequisites

- A CryptoCompare API key (free tier available).
- A running PostgreSQL database instance.
- Basic familiarity with Python, SQL, Jupyter notebooks, and Sisense.

## Useful Resources

- [Sisense Documentation](https://documentation.sisense.com/)
- [CryptoCompare API Documentation](https://min-api.cryptocompare.com/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Statsmodels Documentation](https://www.statsmodels.org/stable/index.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)

## Notes

- **Sisense Licensing**: Sisense offers a free trial, but a paid subscription may be required for full functionality. Check for academic or educational discounts.
