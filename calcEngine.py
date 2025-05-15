import numpy as np
import threading
from queue import Queue
from scipy.stats import norm
from quoteEngine import QuoteEngine
from Exchanges import OptionExchange, ExchangeManager

# Simplified Option Data Structure
class Option:
    def __init__(self, spot, strike, time_to_expiry, rate, volatility, is_call):
        self.spot = spot
        self.strike = strike
        self.time_to_expiry = time_to_expiry
        self.rate = rate
        self.volatility = volatility
        self.is_call = is_call

# Black-Scholes approximation
def black_scholes_price(opt: Option):
    S, K, T, r, v = opt.spot, opt.strike, opt.time_to_expiry, opt.rate, opt.volatility
    d1 = (np.log(S / K) + (r + 0.5 * v ** 2) * T) / (v * np.sqrt(T))
    d2 = d1 - v * np.sqrt(T)

    if opt.is_call:
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)



# CalcEngine Class
class CalcEngine:
    # Simulated PSM Cache (Parameter Set Mesh) with precomputed prices
    class PSMCache:
        def __init__(self):
            self.cache = {}

        def lookup(self, key):
            return self.cache.get(key, None)

        def store(self, key, value):
            self.cache[key] = value

    def __init__(self, exchangeManager: ExchangeManager):
        self.exchangeManager = exchangeManager
        self.psm = self.PSMCache()
        self.task_queue = Queue()
        self.result_store_lock = threading.Lock()
        self.result_store = {}
        self.input_options = {}

    def worker(self):
        while not self.task_queue.empty():
            option_id, option = self.task_queue.get()
            key = (round(option.spot, 2), round(option.strike, 2),
                   round(option.time_to_expiry, 2), round(option.rate, 2),
                   round(option.volatility, 2), option.is_call)
            # Try fast approximate lookup
            price = self.psm.lookup(key)
            if price is None:
                # Compute and store if not found
                price = black_scholes_price(option)
                self.psm.store(key, price)
            self.result_store[option_id] = price
            self.input_options[option_id] = option
            self.task_queue.task_done()
    
    def get_result_store(self):
        with self.result_store_lock:
            return dict(self.result_store)

    def run(self, options_dict, num_threads=4):
        for option_id, option in options_dict.items():
            self.task_queue.put((option_id, option))
        threads = [threading.Thread(target=self.worker) for _ in range(num_threads)]
        for t in threads: t.start()
        for t in threads: t.join()
        for opt_id, price in self.result_store.items():
            print(f"Calc Engine generated: {opt_id}: {price:.2f}")
        q = QuoteEngine(self.result_store)
        quotes = q.generate_quotes()
        for opt_id, q in quotes.items():
            print(f"Quote Engine generated: {opt_id} => Bid: {q['bid']:.2f}, Ask: {q['ask']:.2f}")
            option_type = "Call" if self.input_options[opt_id].is_call else "Put"
            self.exchangeManager.publish_to_all(opt_id, self.input_options[opt_id].strike, option_type, q['bid'], q['ask']) 
        return self.result_store

# Test the CalcEngine with multiple options
def test_calc_engine():
    options = {
        f"opt{i}": Option(spot=100 + i, strike=100, time_to_expiry=1,
                          rate=0.05, volatility=0.2, is_call=(i % 2 == 0))
        for i in range(10)
    }

    engine = CalcEngine()
    results = engine.run(options)

    for opt_id, price in results.items():
        print(f"{opt_id}: {price:.2f}")
