# Real-Time Bitcoin Analytics with Sisense

This project implements a real-time data ingestion and analytics system for Bitcoin using Sisense. It fetches live and historical Bitcoin data from the CryptoCompare API, processes it with Python, stores it in PostgreSQL, and visualizes it through interactive Sisense dashboards to deliver actionable insights, including price trends, forecasts, and technical indicators.

## Project Overview

The system combines data ingestion, processing, time series forecasting, and visualization to provide a robust analytics pipeline for Bitcoin (BTC/USD) data. It uses Docker for consistent deployment, Python for data manipulation, and Sisense for interactive dashboards, making it modular and extensible.

## Technologies Used

- **Sisense**: Business intelligence platform for data visualization and analytics.
- **Python**: Core language for data ingestion, processing, and analysis (3.8+ recommended).
- **PostgreSQL**: Relational database for storing Bitcoin data.
- **CryptoCompare API**: Source for real-time and historical Bitcoin price data.
- **Pandas**: Library for data manipulation and structuring.
- **Statsmodels**: Library for time series forecasting (e.g., SARIMAX).
- **SQLAlchemy**: ORM and SQL toolkit for database interactions.
- **Requests**: HTTP library for API calls.
- **python-dotenv**: For managing environment variables securely.
- **Docker**: Containerization for consistent deployment and execution.

## Project Structure

- **`bitcoin_analysis_utils.py`**: Utility module with functions for:
  - Fetching data from the CryptoCompare API.
  - Managing PostgreSQL database connections.
  - Performing SARIMAX forecasting.
  - Calculating technical indicators (MACD, Bollinger Bands, RSI).
- **`bitcoin_analysis_API.ipynb`**: Jupyter notebook demonstrating data fetching and processing using utility functions, including SARIMAX forecasting.
- **`bitcoin_analysis_examples.ipynb`**: Jupyter notebook with examples of data analysis, forecasting, and preparation for Sisense visualization.
- **`indicators.ipynb`**: Jupyter notebook for calculating and storing technical indicators in PostgreSQL:
  - **MACD**: 12-day and 26-day EMAs with a 9-day signal line, stored in `bitcoin_macd`.
  - **RSI**: 14-day window, stored in `bitcoin_rsi`.
  - **Bollinger Bands**: 20-day moving average with 2 standard deviations, stored in `bitcoin_bb`.
- **`docker_data605_style/`**: Directory with Docker-related files:
  - `Dockerfile`: Defines the Docker image.
  - `bashrc`: Custom bash configuration for the container.
  - `docker_bash.sh`: Launches a container with an interactive shell, mounting the project directory at `/data` and exposing port 8888.
  - `docker_build.sh`: Builds the `umd_data605_template` image using Docker BuildKit.
  - `docker_build.version.log`: Logs build versions.
  - `docker_clean.sh`: Cleans up containers and images.
  - `docker_exec.sh`: Executes commands in a running container.
  - `docker_jupyter.sh`: Runs a Jupyter notebook server in the container.
  - `docker_name.sh`: Manages container naming.
  - `docker_push.sh`: Pushes the image to a repository.
  - `etc_sudoers`: Configures sudo privileges in the container.
  - `install_jupyter_extensions.sh`: Installs Jupyter extensions.
  - `run_jupyter.sh`: Starts the Jupyter server.
  - `version.sh`: Manages version information.
- **`.gitignore`**: Excludes unnecessary files (e.g., `__pycache__`, checkpoints).
- **`.ipynb_checkpoints/`**: Contains Jupyter notebook checkpoints.
- **`__pycache__/`**: Contains Python bytecode files.
- **`docker_build.log`**: Logs Docker build processes.

## Data Ingestion

- **Source**: CryptoCompare API provides minute-level and daily-level Bitcoin price data.
- **Historical Data**: Fetched in chunks (e.g., 2 days of minute data or 365 days of daily data) and stored in PostgreSQL.
- **Real-Time Data**: Fetched periodically (e.g., last 24 hours of minute data) or live per minute and appended to the database.

## Data Processing and Analysis

- **Cleaning and Structuring**: Raw data is processed with Pandas for consistency.
- **Time Series Forecasting**: SARIMAX models from Statsmodels forecast Bitcoin prices using historical daily data.
- **Technical Indicators**: Calculated in `indicators.ipynb` and stored in PostgreSQL:
  - **MACD**: Tracks trend direction and momentum.
  - **RSI**: Measures price momentum.
  - **Bollinger Bands**: Indicates volatility.

## Visualization in Sisense

- **Dashboards**: Show real-time prices, historical trends, forecasts, and technical indicators.
- **Interactivity**: Users can filter by date ranges and compare data.
- **Data Flow**: Processed data from PostgreSQL is imported into Sisense.

## Setup and Installation

### Prerequisites

- CryptoCompare API key (free tier at [CryptoCompare](https://min-api.cryptocompare.com/)).
- Running PostgreSQL database instance.
- Python 3.8+.
- Docker installed.
- Basic knowledge of Python, SQL, Jupyter, Sisense, and Docker.

### Install Dependencies

1. Install Python libraries:
   ```
   pip install requests pandas statsmodels sqlalchemy python-dotenv
   ```

2. Set up environment variables:
   - Create a `.env` file in the project root:
     ```
     API_KEY=your_cryptocompare_api_key
     DATABASE_URL=your_postgresql_database_url
     ```
   - Use a PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/dbname`).

### Run the Project

1. Start your PostgreSQL database.
2. Build the Docker image:
   ```
   ./docker_data605_style/docker_build.sh
   ```
3. Launch a container:
   ```
   ./docker_data605_style/docker_bash.sh
   ```
4. Inside the container, run the Jupyter notebooks:
   - `bitcoin_analysis_API.ipynb`: Fetch and store data.
   - `bitcoin_analysis_examples.ipynb`: Analyze and prepare data for Sisense.
   - `indicators.ipynb`: Calculate and store technical indicators.
5. Import PostgreSQL data into Sisense for visualization.

## Docker Usage

- **Build Image**: `./docker_build.sh` creates `umd_data605_template`.
- **Run Container**: `./docker_bash.sh` starts a container with the project mounted at `/data`.
- **Jupyter Server**: `./docker_jupyter.sh` runs a notebook server.
- **Clean Up**: `./docker_clean.sh` removes unused containers/images.

## Useful Resources

- [Sisense Documentation](https://documentation.sisense.com/)
- [CryptoCompare API Documentation](https://min-api.cryptocompare.com/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Statsmodels Documentation](https://www.statsmodels.org/stable/index.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)
- [Docker Documentation](https://docs.docker.com/)

## Notes

- **Sisense Licensing**: Free trial available; full features may require a subscription.
- **Recent Updates**: Live minute fetch and technical indicator calculations added recently.

