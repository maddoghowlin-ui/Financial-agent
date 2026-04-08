import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from config import *
from data_fetcher import DataFetcher
from market_analyzer import MarketAnalyzer
from portfolio_manager import PortfolioManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinancialAgent:
    """Main Financial Investment Agent"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher(lookback_days=LOOKBACK_PERIOD)
        self.market_analyzer = MarketAnalyzer(momentum_threshold=MOMENTUM_THRESHOLD)
        self.portfolio = PortfolioManager(
            initial_capital=INITIAL_CAPITAL,
            stop_loss_percent=STOP_LOSS_PERCENT,
            take_profit_percent=TAKE_PROFIT_PERCENT
        )
        self.scheduler = BackgroundScheduler()
        self.run_count = 0
    
    def analyze_and_invest(self):
        """Main logic: analyze market and invest in highest gainers"""
        try:
            self.run_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"🤖 FINANCIAL AGENT - RUN #{self.run_count}")
            logger.info(f"{'='*60}\n")
            
            # Step 1: Check existing positions for stop loss/take profit
            logger.info("📊 STEP 1: Monitoring existing positions...")
            self._monitor_positions()
            
            # Step 2: Fetch and analyze top gainers
            logger.info("\n📈 STEP 2: Analyzing market for top gainers...")
            top_opportunities = self._analyze_opportunities()
            
            # Step 3: Invest in best opportunities
            if top_opportunities:
                logger.info(f"\n💰 STEP 3: Executing investments in top {len(top_opportunities[:3])} opportunities...")
                self._execute_investments(top_opportunities)
            else:
                logger.warning("⚠ No investment opportunities found")
            
            # Step 4: Display portfolio summary
            self._display_portfolio_summary()
            
        except Exception as e:
            logger.error(f"❌ Error in analyze_and_invest: {str(e)}", exc_info=True)
    
    def _monitor_positions(self):
        """Check existing positions for stop loss/take profit"""
        if not self.portfolio.positions:
            logger.info("  No open positions to monitor")
            return
        
        current_prices = {}
        for ticker in list(self.portfolio.positions.keys()):
            data = self.data_fetcher.fetch_stock_data(ticker)
            if data:
                current_prices[ticker] = data['current_price']
                current_price = data['current_price']
                
                # Check stop loss
                if self.portfolio.check_stop_loss(ticker, current_price):
                    self.portfolio.close_position(ticker, current_price, reason="stop_loss")
                
                # Check take profit
                elif self.portfolio.check_take_profit(ticker, current_price):
                    self.portfolio.close_position(ticker, current_price, reason="take_profit")
    
    def _analyze_opportunities(self):
        """Analyze market and find investment opportunities"""
        top_gainers = self.data_fetcher.fetch_top_gainers()
        
        if not top_gainers:
            logger.warning("  Could not fetch top gainers")
            return []
        
        logger.info(f"  📊 Analyzing {len(top_gainers)} top gainers...")
        
        stocks_analysis = []
        for gainer in top_gainers:
            ticker = gainer['ticker']
            
            # Skip if already in portfolio
            if ticker in self.portfolio.positions:
                logger.info(f"  ⏭ {ticker}: Already in portfolio, skipping")
                continue
            
            # Fetch full data for analysis
            data = self.data_fetcher.fetch_stock_data(ticker)
            if not data or data['history'].empty:
                continue
            
            # Analyze
            analysis = self.market_analyzer.analyze_stock(ticker, data['history'])
            if analysis:
                analysis['volume'] = gainer['volume']
                stocks_analysis.append(analysis)
        
        # Rank opportunities
        ranked = self.market_analyzer.rank_opportunities(stocks_analysis)
        
        logger.info(f"  ✓ Ranked {len(ranked)} opportunities")
        for i, stock in enumerate(ranked[:5], 1):
            logger.info(f"    {i}. {stock['ticker']}: +{stock['gain_today']:.2f}% (Score: {stock['strength_score']:.0f})")
        
        return ranked
    
    def _execute_investments(self, opportunities):
        """Execute investments in top opportunities"""
        max_investments = max(1, int(INITIAL_CAPITAL / (INITIAL_CAPITAL * MAX_POSITION_SIZE)))
        investments_count = 0
        
        for opportunity in opportunities:
            if investments_count >= max_investments:
                break
            
            ticker = opportunity['ticker']
            current_price = opportunity['current_price']
            
            # Calculate position size
            max_investment = INITIAL_CAPITAL * MAX_POSITION_SIZE
            shares = int(max_investment / current_price)
            
            if shares <= 0:
                logger.warning(f"  ⚠ {ticker}: Insufficient capital for position")
                continue
            
            # Execute buy
            if self.portfolio.add_position(ticker, shares, current_price):
                investments_count += 1
    
    def _display_portfolio_summary(self):
        """Display current portfolio status"""
        current_prices = {}
        for ticker in self.portfolio.positions:
            data = self.data_fetcher.fetch_stock_data(ticker)
            if data:
                current_prices[ticker] = data['current_price']
        
        summary = self.portfolio.get_portfolio_summary(current_prices)
        
        logger.info(f"\n{'='*60}")
        logger.info("📋 PORTFOLIO SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Value:        ${summary['total_value']:.2f}")
        logger.info(f"Available Cash:     ${summary['cash']:.2f}")
        logger.info(f"Position Value:     ${summary['position_value']:.2f}")
        logger.info(f"Open Positions:     {summary['open_positions']}")
        logger.info(f"Total Return:       ${summary['total_return']:.2f} ({summary['total_return_percent']:.2f}%)")
        
        if summary['positions']:
            logger.info(f"\n{'Position Details:':60}")
            for pos in summary['positions']:
                logger.info(f"  {pos['ticker']:6} | Shares: {pos['shares']:5} | Entry: {pos['entry_price']:>8} | Current: {pos['current_price']:>8} | P&L: {pos['unrealized_pl']:>10} ({pos['unrealized_pl_percent']})")
        
        logger.info(f"{'='*60}\n")
    
    def start_scheduler(self, interval_minutes=UPDATE_INTERVAL_MINUTES):
        """Start the background scheduler"""
        logger.info(f"⏰ Starting scheduler - Update every {interval_minutes} minutes")
        
        self.scheduler.add_job(
            self.analyze_and_invest,
            'interval',
            minutes=interval_minutes,
            id='financial_agent_job'
        )
        
        self.scheduler.start()
    
    def run_once(self):
        """Run the agent once"""
        self.analyze_and_invest()
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✓ Scheduler stopped")


def main():
    """Main entry point"""
    agent = FinancialAgent()
    
    logger.info("""
    ╔═══════════════════════════════════════════╗
    ║   🤖 FINANCIAL INVESTMENT AGENT 🤖       ║
    ║   Automated Portfolio Management          ║
    ╚═══════════════════════════════════════════╝
    """)
    
    logger.info(f"Initial Capital:     ${INITIAL_CAPITAL:.2f}")
    logger.info(f"Max Position Size:   {MAX_POSITION_SIZE*100:.0f}%")
    logger.info(f"Stop Loss:           {STOP_LOSS_PERCENT:.1f}%")
    logger.info(f"Take Profit:         {TAKE_PROFIT_PERCENT:.1f}%")
    logger.info(f"Lookback Period:     {LOOKBACK_PERIOD} days")
    
    # Run once immediately
    agent.run_once()
    
    # Start scheduler for continuous monitoring
    # Uncomment to enable scheduled runs
    # agent.start_scheduler(UPDATE_INTERVAL_MINUTES)
    # try:
    #     while True:
    #         import time
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     agent.stop()
    #     logger.info("Agent stopped by user")


if __name__ == "__main__":
    main()
