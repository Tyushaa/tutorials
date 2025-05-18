try:
    from .bitcoin_analytics_utils import (
        update_minute_table,
        update_daily_table,
        load_daily_from_db,
        compute_macd,
        compute_bollinger_bands,
        compute_rsi,
        fit_sarimax,
        forecast_sarimax
    )
except ImportError:
    # Graceful fallback for cases where utils are not yet available
    pass