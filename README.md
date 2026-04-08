# 🤖 Financial Investment Agent

An intelligent Python-based financial agent that automatically analyzes market trends, detects top-gaining stocks, and manages an investment portfolio with built-in risk management features.

## Features

✨ **Market Analysis**
- Real-time market data fetching from multiple sources
- Technical indicator calculations (RSI, MACD, Bollinger Bands, SMA)
- Top gainer detection based on daily gains
- Strength scoring for investment opportunities

💰 **Portfolio Management**
- Automatic position tracking
- Stop-loss execution (prevents losses beyond threshold)
- Take-profit execution (locks in gains)
- Position rebalancing
- Cash management

🎯 **Investment Strategy**
- Invests in highest-gaining stocks of the day
- Multi-indicator buy signal generation
- Risk-adjusted position sizing
- Automated reinvestment of profits

📊 **Monitoring & Reporting**
- Real-time portfolio valuation
- Performance tracking
- Transaction history
- Summary reports

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/financial-agent.git
cd financial-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
