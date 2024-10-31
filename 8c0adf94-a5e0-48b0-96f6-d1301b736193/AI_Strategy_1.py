from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, Slope
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker of the stock you want to trade.
        self.ticker = "AAPL"  # Example ticker, replace it with the stock you're interested in

    @property
    def assets(self):
        # List the assets this strategy will handle.
        return [self.ticker]

    @property
    def interval(self):
        # Define the interval for data collection; here we use daily data.
        return "1day"

    def run(self, data):
        # Initialize a variable to hold the stock stake allocation.
        ticker_stake = 0

        # Check if there is enough data to compute the indicators.
        if len(data["ohlcv"]) > 50:
            # Calculate the 50-day Simple Moving Average (SMA) for the stock.
            sma_50 = SMA(self.ticker, data["ohlcv"], length=50)

            # Calculate the price slope for the stock over the last 5 days.
            # Slope uses the closing price for its calculations.
            price_slope = Slope(self.ticker, data["ohlcv"], length=5)

            # Get the latest closing price for the stock.
            last_price = data["ohlcv"][-1][self.ticker]["close"]

            # Decide to buy if the last price is above the SMA but the slope is descending,
            # indicating a recent downturn in a generally upward trend.
            if last_price > sma_50[-1] and price_slope[-1] < 0:
                ticker_stake = 0.5  # Allocate 50% to buying the stock.

            # Sell if the last price is below the SMA and slope is positive,
            # indicating a potential end to a rising streak.
            elif last_price < sma_50[-1] and price_slope[-1] > 0:
                ticker_stake = -0.5  # Allocate -50% to indicate selling (shorting).

        # Since the strategy base class requires a TargetAllocation object to be returned,
        # we map the tickers to their respective stake allocations.
        return TargetAllocation({self.ticker: ticker_stake})