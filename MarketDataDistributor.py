import threading
import random
import time
from queue import Queue
from typing import List, Dict
import numpy as np
from scipy.stats import norm
from calcEngine import CalcEngine
from Exchanges import OptionExchange, ExchangeManager

# Simplified Option Data Structure
class Option:
    def __init__(self, symbol, strike, time_to_expiry, is_call, spot, rate, volatility, timestamp, source):
        self.symbol = symbol
        self.strike = strike
        self.time_to_expiry = time_to_expiry
        self.is_call = is_call
        self.timestamp = timestamp
        self.source = source
        self.spot = spot
        self.rate = rate
        self.volatility = volatility

    def __str__(self):
        return (f"{self.symbol} @ {self.timestamp:.1f} [{self.source}] => "
                f"Strike: {self.strike:.3f} Time to Expiry: {self.time_to_expiry}, IsCall: {self.is_call}"
                f"Spot: {self.spot:.2f}, Vol: {self.volatility:.2f}, Rate: {self.rate:.3f}")


# MockDataSource simulates a real market feed
class MockDataSource(threading.Thread):
    def __init__(self, name: str, symbols: List[str], out_queue: Queue, interval=1.0):
        super().__init__(daemon=True)
        self.name = name
        self.symbols = symbols
        self.out_queue = out_queue
        self.interval = interval
        self.running = True

    def generate_tick(self, symbol) -> Option:
        return Option(
            symbol=symbol,
            strike=100 + random.uniform(-20, 20),
            time_to_expiry=random.choice([365*i for i in range(1, 10)]),
            is_call=random.choice([True, False]),
            spot=100 + random.uniform(-2, 2),
            volatility=0.2 + random.uniform(-0.015, 0.015),
            rate=0.01 + random.uniform(-0.001, 0.001),
            timestamp=time.time(),
            source=self.name
        )

    def run(self):
        while self.running:
            for symbol in self.symbols:
                tick = self.generate_tick(symbol)
                print(f"[{self.name}] Generated Option: {tick}")
                self.out_queue.put(tick)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

# MarketDataDistributor aggregates feeds and pushes canonical data to subscribers
class MarketDataDistributor:
    def __init__(self):
        self.subscribers: List[Queue] = []
        self.source_queue = Queue()
        self.sources: List[MockDataSource] = []

    def add_data_source(self, data_source: MockDataSource):
        self.sources.append(data_source)

    def register(self, subscriber_queue: Queue):
        self.subscribers.append(subscriber_queue)

    def broadcast(self, opt: Option):
        for sub in self.subscribers:
            sub.put(opt)

    def run(self):
        for src in self.sources:
            src.start()

        print("[MDDS] Running Market Data Distributor...")
        try:
            while True:
                update = self.source_queue.get()
                # In real life, you might normalize or de-duplicate here
                self.broadcast(update)
                self.source_queue.task_done()
        except KeyboardInterrupt:
            print("[MDDS] Stopping...")
            for src in self.sources:
                src.stop()

# Example Subscriber
def mddsubscriber(engine, q: Queue):
    mddsubscriber.id +=1
    while True:
        update = q.get()
        engine.run({update.symbol : update})
        q.task_done()
mddsubscriber.id = 0

# Demo Execution
if __name__ == "__main__":
    symbols_A = ["WTI", "NBP", "XNM", "CNE"]
    symbols_B = ["SRP", "CRA", "DBJ", "UMA"]

    distributor = MarketDataDistributor()

    # Create two mock data sources (Reuters, Bloomberg)
    source1 = MockDataSource("Reuters", symbols_A, distributor.source_queue, interval=10.0)
    source2 = MockDataSource("Bloomberg", symbols_B, distributor.source_queue, interval=5.5)

    distributor.add_data_source(source1)
    distributor.add_data_source(source2)

    # Subscribers
    CalcEnginequeue = Queue()
    distributor.register(CalcEnginequeue)

    # Create exchanges
    exchange1 = OptionExchange("ICE")
    exchange2 = OptionExchange("CBOE")

    # Create manager and add exchanges
    ExchManager = ExchangeManager()
    ExchManager.add_exchange(exchange1)
    ExchManager.add_exchange(exchange2)

    Cengine = CalcEngine(ExchManager)

    threading.Thread(target=mddsubscriber, args=(Cengine, CalcEnginequeue), daemon=True).start()
    #threading.Thread(target=mddsubscriber, args=("QuoteEngine", QuoteEnginequeue), daemon=True).start()

    # Run distributor loop
    distributor.run()
