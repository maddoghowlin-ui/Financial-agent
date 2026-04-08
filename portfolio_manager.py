import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioManager:
    """Manage portfolio, track positions, and execute rebalancing"""
    
    def __init__(self, initial_capital, stop_loss_percent, take_profit_percent):
        self.initial_capital = initial_capital
        self.available_cash = initial_capital
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.positions = {}  # {ticker: {'shares': X, 'entry_price': Y, 'entry_date': Z, 'status': 'open'}}
        self.closed_positions = []
        self.transaction_history = []
    
    def add_position(self, ticker, shares, entry_price):
        """Add a new position to the portfolio"""
        try:
            cost = shares * entry_price
            
            if cost > self.available_cash:
                logger.warning(f"Insufficient cash to buy {shares} shares of {ticker}")
                return False
            
            self.positions[ticker] = {
                'shares': shares,
                'entry_price': entry_price,
                'entry_date': datetime.now(),
                'status': 'open',
                'highest_price': entry_price,  # For trailing stop loss
            }
            
            self.available_cash -= cost
            
            self.transaction_history.append({
                'type': 'BUY',
                'ticker': ticker,
                'shares': shares,
                'price': entry_price,
                'cost': cost,
                'date': datetime.now(),
            })
            
            logger.info(f"✓ BUY: {shares} shares of {ticker} @ ${entry_price:.2f}")
            return True
        
        except Exception as e:
            logger.error(f"Error adding position: {str(e)}")
            return False
    
    def check_stop_loss(self, ticker, current_price):
        """Check if position should be closed due to stop loss"""
        if ticker not in self.positions:
            return False
        
        position = self.positions[ticker]
        entry_price = position['entry_price']
        loss_percent = ((current_price - entry_price) / entry_price) * 100
        
        if loss_percent <= -self.stop_loss_percent:
            logger.warning(f"⚠ STOP LOSS triggered for {ticker}: {loss_percent:.2f}%")
            return True
        
        return False
    
    def check_take_profit(self, ticker, current_price):
        """Check if position should be closed due to take profit"""
        if ticker not in self.positions:
            return False
        
        position = self.positions[ticker]
        entry_price = position['entry_price']
        gain_percent = ((current_price - entry_price) / entry_price) * 100
        
        if gain_percent >= self.take_profit_percent:
            logger.info(f"✓ TAKE PROFIT triggered for {ticker}: {gain_percent:.2f}%")
            return True
        
        return False
    
    def close_position(self, ticker, current_price, reason="manual"):
        """Close a position and return cash to portfolio"""
        try:
            if ticker not in self.positions:
                return False
            
            position = self.positions[ticker]
            shares = position['shares']
            entry_price = position['entry_price']
            
            revenue = shares * current_price
            profit_loss = revenue - (shares * entry_price)
            profit_loss_percent = (profit_loss / (shares * entry_price)) * 100
            
            # Update position
            position['status'] = 'closed'
            position['exit_price'] = current_price
            position['exit_date'] = datetime.now()
            position['profit_loss'] = profit_loss
            position['profit_loss_percent'] = profit_loss_percent
            
            # Record closed position
            self.closed_positions.append(position)
            
            # Return cash
            self.available_cash += revenue
            
            # Record transaction
            self.transaction_history.append({
                'type': 'SELL',
                'ticker': ticker,
                'shares': shares,
                'price': current_price,
                'revenue': revenue,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'reason': reason,
                'date': datetime.now(),
            })
            
            logger.info(f"✓ SELL: {shares} shares of {ticker} @ ${current_price:.2f} | P&L: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)")
            
            # Remove from active positions
            del self.positions[ticker]
            
            return True
        
        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            return False
    
    def get_portfolio_value(self, current_prices):
        """Calculate total portfolio value"""
        position_value = 0
        
        for ticker, position in self.positions.items():
            if ticker in current_prices and position['status'] == 'open':
                position_value += position['shares'] * current_prices[ticker]
        
        total_value = self.available_cash + position_value
        return total_value
    
    def get_portfolio_summary(self, current_prices):
        """Get detailed portfolio summary"""
        position_value = 0
        open_positions = 0
        
        position_details = []
        
        for ticker, position in self.positions.items():
            if position['status'] == 'open' and ticker in current_prices:
                current_price = current_prices[ticker]
                entry_price = position['entry_price']
                shares = position['shares']
                
                position_value_ticker = shares * current_price
                unrealized_pl = position_value_ticker - (shares * entry_price)
                unrealized_pl_percent = (unrealized_pl / (shares * entry_price)) * 100
                
                position_value += position_value_ticker
                open_positions += 1
                
                position_details.append({
                    'ticker': ticker,
                    'shares': shares,
                    'entry_price': f"${entry_price:.2f}",
                    'current_price': f"${current_price:.2f}",
                    'position_value': f"${position_value_ticker:.2f}",
                    'unrealized_pl': f"${unrealized_pl:.2f}",
                    'unrealized_pl_percent': f"{unrealized_pl_percent:.2f}%",
                })
        
        total_value = self.available_cash + position_value
        total_return = total_value - self.initial_capital
        total_return_percent = (total_return / self.initial_capital) * 100
        
        return {
            'total_value': total_value,
            'cash': self.available_cash,
            'position_value': position_value,
            'open_positions': open_positions,
            'total_return': total_return,
            'total_return_percent': total_return_percent,
            'positions': position_details,
        }
