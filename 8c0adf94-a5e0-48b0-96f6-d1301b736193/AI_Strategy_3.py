from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import Slope, Momentum
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # List of 50 tickers you're tracking
        self.tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA", "BRK.B", "JNJ", "V", "WMT",
                        "PG", "JPM", "UNH", "MA", "DIS", "NVDA", "HD", "PYPL", "VZ", "ADBE", 
                        "CMCSA", "NFLX", "INTC", "PFE", "KO", "T", "PEP", "BAC", "MRK", "XOM", 
                        "ABBV", "ABT", "CSCO", "AVGO", "ACN", "QCOM", "COST", "CVX", "LLY", "MDT",
                        "TXN", "DHR", "HON", "LMT", "UNP", "AMGN", "IBM", "MMM", "UPS", "BA"]
        self.maximum_allocation_per_stock = 0.20  # Maximum of 20% allocated to any stock
        self.investment_increment = 0.05  # Allocation increment based on positive acceleration

    @property
    def interval(self):
        return "5min"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        # Initialize allocation dictionary with 0 for each stock
        allocation_dict = {ticker: 0 for ticker in self.tickers}

        # Calculate acceleration (second derivative of price) for each stock
        accelerations = {}
        for ticker in self.tickers:
            # Calculate momentum (first derivative of price)
            momentum_values = Momentum(ticker, data["ohlcv"], length=5)
            if momentum_values:
                # Calculate the slope of the momentum to get acceleration
                accelerations[ticker] = Slope(ticker, [{"close": v} for v in momentum_values], length=3)[-1]

        # Rank stocks by acceleration and normalize allocation
        ranked_stocks = sorted(accelerations, key=accelerations.get, reverse=True)
        for i, ticker in enumerate(ranked_stocks):
            # Allocate dynamically based on rank and ensure no more than maximum_allocation_per_stock
            allocation = min(self.maximum_allocation_per_stock, self.investment_increment * (len(self.tickers) - i))
            allocation_dict[ticker] = allocation

        # Liquidate quickly if the acceleration turns negative
        for ticker, acceleration in accelerations.items():
            if acceleration < 0:
                allocation_dict[ticker] = 0  # Liquidate position
            
        return TargetAllocation(allocation_dict)