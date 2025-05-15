class QuoteEngine:
    def __init__(self, calc_results, inventory_levels=None):
        """
        calc_results: dict from CalcEngine {option_id: theoretical_price}
        inventory_levels: dict {option_id: int}, where positive = long, negative = short
        """
        self.calc_results = calc_results
        self.inventory_levels = inventory_levels or {}
        self.quotes = {}

    def generate_quotes(self, spread=0.05, risk_adjustment=0.01):
        """
        Generate two-way quotes by applying:
        - base spread
        - inventory-based skew adjustment
        """
        for option_id, theo_price in self.calc_results.items():
            inv = self.inventory_levels.get(option_id, 0)
            # Adjust spread based on inventory
            # More long -> lower bid, higher ask to discourage more buying
            # More short -> higher bid, lower ask to encourage closing
            skew = inv * risk_adjustment

            bid = max(theo_price - (spread + skew), 0.01)
            ask = max(theo_price + (spread - skew), bid + 0.01)  # Ensure ask > bid

            self.quotes[option_id] = {"bid": round(bid, 2), "ask": round(ask, 2)}

        return self.quotes

# Example usage
def test_quote_engine():
    # Simulated CalcEngine output
    calc_results = {
        'opt0': 2.10,
        'opt1': 3.25,
        'opt2': 5.60,
    }

    # Simulated inventory levels
    inventory = {
        'opt0': 10,   # Long position
        'opt1': -5,   # Short position
        'opt2': 0     # Neutral
    }

    quote_engine = QuoteEngine(calc_results, inventory)
    quotes = quote_engine.generate_quotes()

    for opt_id, q in quotes.items():
        print(f"{opt_id} => Bid: {q['bid']:.2f}, Ask: {q['ask']:.2f}")

if __name__ == "__main__":
    test_quote_engine()