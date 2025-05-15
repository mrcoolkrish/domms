import time
import random
from threading import Thread
from quoteEngine import QuoteEngine
import datetime

class OptionExchange:
    def __init__(self, name):
        self.name = name
        self.quotes = []

    def publish_quote(self, symbol, strike_price, option_type, bid, ask):
        quote = {
            "symbol": symbol,
            "strike_price": strike_price,
            "option_type": option_type,
            "bid": bid,
            "ask": ask,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.quotes.append(quote)
        print(f"[{self.name}] Published quote: {quote}")

    def get_quotes(self):
        return self.quotes


class ExchangeManager:
    def __init__(self):
        self.exchanges = []

    def add_exchange(self, exchange):
        self.exchanges.append(exchange)

    def publish_to_all(self, symbol, strike_price, option_type, bid, ask):
        for exchange in self.exchanges:
            exchange.publish_quote(symbol, strike_price, option_type, bid, ask)

def test_exchange_manager():
    # Create exchanges
    exchange1 = OptionExchange("Exchange A")
    exchange2 = OptionExchange("Exchange B")

    # Create manager and add exchanges
    manager = ExchangeManager()
    manager.add_exchange(exchange1)
    manager.add_exchange(exchange2)

    # Publish quotes to all exchanges
    manager.publish_to_all("AAPL", 150.00, "call", 5.00, 5.50)
    manager.publish_to_all("GOOGL", 2800.00, "put", 10.00, 10.50)

    # Print quotes from each exchange
    for exchange in manager.exchanges:
        print(f"Quotes from {exchange.name}: {exchange.get_quotes()}")

# Example usage
if __name__ == "__main__":
    test_exchange_manager()
    time.sleep(1)  # Simulate delay