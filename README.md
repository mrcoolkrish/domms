The provided code defines a `MarketDataDistributor` system that aggregates market data from multiple sources and distributes it to subscribers.

To run use `python MarketDataDistributor.py`

### Key Components:
- **`MockDataSource`**:
  - Simulates market data feeds (e.g., Reuters, Bloomberg).
  - Generates random option data and pushes it to the `MarketDataDistributor`.

- **`MarketDataDistributor`**:
  - Aggregates data from multiple sources and broadcasts it to subscribers.
  - Uses a `Queue` to receive data from sources and distribute it to subscribers.

- **`CalcEngine`**:
  - A subscriber that processes the options and prices it using Black Scholes pricer 
  - It uses a cache (PSM) for quicker processing of preexisting options.

- **`QuoteEngine`**:
  - QuoteEngine processes all the options results from the CalcEngine

- **`ExchangeManager`**:
  - The quotes from QuoteEngine is distributed to Exchanges registered with an Exchange manager

  The solution accommodates multiple datasources, CalcEngine, QuoteEngine and Exchanges