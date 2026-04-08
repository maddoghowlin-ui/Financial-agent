import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
IEX_API_KEY = os.getenv("IEX_API_KEY", "")

# Portfolio Configuration
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "10000"))
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.1"))  # 10% per stock
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "5"))  # 5% loss
TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "15"))  # 15% gain

# Trading Configuration
MIN_VOLUME_THRESHOLD = int(os.getenv("MIN_VOLUME_THRESHOLD", "1000000"))
MIN_PRICE = float(os.getenv("MIN_PRICE", "5"))  # Avoid penny stocks
MAX_PRICE = float(os.getenv("MAX_PRICE", "500"))

# Data Sources
DATA_SOURCES = {
    "yfinance": True,
    "alpha_vantage": False,  # Set to True if you have API key
    "iex": False,  # Set to True if you have API key
}

# Market Analysis
LOOKBACK_PERIOD = int(os.getenv("LOOKBACK_PERIOD", "30"))  # days
MOMENTUM_THRESHOLD = float(os.getenv("MOMENTUM_THRESHOLD", "2.0"))  # standard deviations

# Scheduler
UPDATE_INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", "60"))
