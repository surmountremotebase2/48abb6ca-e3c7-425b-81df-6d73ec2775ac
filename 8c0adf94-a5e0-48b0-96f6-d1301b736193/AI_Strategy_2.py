from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the list of tickers you want to watch for volatility
        self.tickers = ["AAPL", "MSFT", "GOOG", "AMZN"]
    
    @property
    def interval(self):
        # Using daily data to calculate ATR
        return "1day"
    
    @property
    def assets(self):
        # Assets being monitored by the strategy
        return self.tickers
    
    def run(self, data):
        # Initialize a dictionary to hold the target allocations
        allocation_dict = {}
        
        # Threshold for detecting a spike in volatility, defined as a percentage increase
        volatility_spike_threshold = 1.20 # 20% increase
        
        for ticker in self.tickers:
            # Calculate two ATRs for each ticker: a short-term (e.g., 14 days) and a long-term (e.g., 50 days) to gauge volatility change
            short_term_atr = ATR(ticker, data["ohlcv"], 14)[-1] # Most recent short-term ATR
            long_term_atr = ATR(ticker, data["ohlcv"], 50)[-1] # Most recent long-term ATR
            
            if short_term_atr is None or long_term_atr is None:
                allocation_dict[ticker] = 0
                continue
                
            # Check if the short-term ATR is significantly higher than the long-term ATR, indicating increased volatility
            if short_term_atr > long_term_atr * volatility_spike_threshold:
                # If so, allocate a portion of the portfolio to this stock, considering it volatile and thus, of interest
                allocation_dict[ticker] = 1.0 / len(self.tickers) # Even distribution among identified volatile tickers
            else:
                # Otherwise, set allocation for this ticker to 0
                allocation_dict[ticker] = 0
        
        return TargetAllocation(allocation_dict)