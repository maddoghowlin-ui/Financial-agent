import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch market data from multiple sources"""
    
    def __init__(self, lookback_days=30):
        self.lookback_days = lookback_days
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=lookback_days)
    
    def fetch_stock_data(self, ticker):
        """Fetch historical data for a stock"""
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(start=self.start_date, end=self.end_date)
            info = stock.info
            
            return {
                'ticker': ticker,
                'history': history,
                'current_price': info.get('currentPrice', history['Close'].iloc[-1] if len(history) > 0 else 0),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
            }
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def fetch_top_gainers(self):
        """Fetch top gaining stocks for the day"""
        try:
            # Using yfinance to get market data
            ticker_list = self.get_popular_tickers()
            gainers = []
            
            for ticker in ticker_list:
                data = self.fetch_stock_data(ticker)
                if data and len(data['history']) > 1:
                    today_close = data['history']['Close'].iloc[-1]
                    prev_close = data['history']['Close'].iloc[-2]
                    gain_percent = ((today_close - prev_close) / prev_close) * 100
                    
                    gainers.append({
                        'ticker': ticker,
                        'gain_percent': gain_percent,
                        'current_price': today_close,
                        'volume': data['volume'],
                    })
            
            # Sort by gain percentage
            gainers = sorted(gainers, key=lambda x: x['gain_percent'], reverse=True)
            return gainers[:10]  # Top 10 gainers
        
        except Exception as e:
            logger.error(f"Error fetching top gainers: {str(e)}")
            return []
    
    def get_popular_tickers(self):
        """Get a list of popular stocks to monitor"""
        # You can expand this list or fetch from a data source
        popular_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'META', 'NVDA', 'JPM', 'JNJ', 'V',
            'WMT', 'PG', 'MA', 'UNH', 'HD',
            'INTC', 'AMD', 'NFLX', 'PYPL', 'ADBE'
        ]
        return popular_tickers
