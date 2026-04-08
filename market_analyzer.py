import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, MACD
from ta.trend import SMAIndicator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyze market trends and detect opportunities"""
    
    def __init__(self, momentum_threshold=2.0):
        self.momentum_threshold = momentum_threshold
    
    def calculate_technical_indicators(self, df):
        """Calculate technical indicators for a stock"""
        try:
            df = df.copy()
            
            # RSI (Relative Strength Index)
            rsi = RSIIndicator(close=df['Close'], window=14)
            df['RSI'] = rsi.rsi()
            
            # MACD (Moving Average Convergence Divergence)
            macd = MACD(close=df['Close'])
            df['MACD'] = macd.macd()
            df['Signal'] = macd.macd_signal()
            df['MACD_Histogram'] = macd.macd_diff()
            
            # SMA (Simple Moving Average)
            sma_20 = SMAIndicator(close=df['Close'], window=20)
            sma_50 = SMAIndicator(close=df['Close'], window=50)
            df['SMA_20'] = sma_20.sma_indicator()
            df['SMA_50'] = sma_50.sma_indicator()
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # Momentum
            df['Momentum'] = df['Close'].diff(periods=1)
            df['Momentum_Percent'] = df['Close'].pct_change() * 100
            
            return df
        
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            return df
    
    def analyze_stock(self, ticker, history_df):
        """Analyze a stock and return signals"""
        try:
            df = self.calculate_technical_indicators(history_df)
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Calculate gain for today
            gain_percent = df['Momentum_Percent'].iloc[-1] if len(df) > 0 else 0
            
            # Generate signals
            signals = {
                'ticker': ticker,
                'current_price': latest['Close'],
                'gain_today': gain_percent,
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'signal_line': latest['Signal'],
                'sma_20': latest['SMA_20'],
                'sma_50': latest['SMA_50'],
                'momentum': latest['Momentum'],
                'buy_signal': self._generate_buy_signal(latest, prev),
                'strength_score': self._calculate_strength_score(latest, prev),
            }
            
            return signals
        
        except Exception as e:
            logger.error(f"Error analyzing stock {ticker}: {str(e)}")
            return None
    
    def _generate_buy_signal(self, latest, prev):
        """Generate buy signal based on multiple indicators"""
        signals = 0
        
        # RSI signal (oversold < 30, or recovering)
        if latest['RSI'] < 30:
            signals += 2
        elif latest['RSI'] < 40:
            signals += 1
        
        # MACD signal (positive crossover)
        if latest['MACD'] > latest['Signal'] and prev['MACD'] <= prev['Signal']:
            signals += 2
        elif latest['MACD'] > latest['Signal']:
            signals += 1
        
        # Price above SMA
        if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
            signals += 1
        
        # Momentum positive
        if latest['Momentum'] > 0:
            signals += 1
        
        return signals >= 3  # Buy if at least 3 signals align
    
    def _calculate_strength_score(self, latest, prev):
        """Calculate overall strength score (0-100)"""
        score = 0
        
        # RSI component (0-30)
        if latest['RSI'] < 30:
            score += 30
        elif latest['RSI'] < 40:
            score += 20
        elif latest['RSI'] > 70:
            score -= 10
        
        # MACD component (0-30)
        if latest['MACD'] > latest['Signal']:
            score += 20
        if latest['MACD_Histogram'] > 0:
            score += 10
        
        # Trend component (0-40)
        if latest['Close'] > latest['SMA_20']:
            score += 15
        if latest['SMA_20'] > latest['SMA_50']:
            score += 15
        if latest['Momentum'] > 0:
            score += 10
        
        return max(0, min(100, score))
    
    def rank_opportunities(self, stocks_analysis):
        """Rank stocks by investment opportunity"""
        valid_stocks = [s for s in stocks_analysis if s is not None]
        
        # Sort by gain percentage (highest gainers first)
        ranked = sorted(
            valid_stocks,
            key=lambda x: (x['gain_today'], x['strength_score']),
            reverse=True
        )
        
        return ranked
