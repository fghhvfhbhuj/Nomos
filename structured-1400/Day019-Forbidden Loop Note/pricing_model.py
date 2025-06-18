import math

class ForbiddenLoopNotePricing:
    def __init__(self, equity_index, volatility, barrier_level, vol_trigger, participation_rate):
        self.equity_index = equity_index  # Current equity index level
        self.volatility = volatility  # Current market volatility
        self.barrier_level = barrier_level  # Price barrier level (K1)
        self.vol_trigger = vol_trigger  # Volatility trigger (θ)
        self.participation_rate = participation_rate  # Participation rate (e.g., 150%)

    def lookback_call_payoff(self, path_minimum):
        """
        Calculate the payoff for a Lookback Call option based on the path minimum.
        """
        return max(self.equity_index - path_minimum, 0) * self.participation_rate

    def calculate_payoff(self, path_minimum):
        """
        Calculate the payoff of the Forbidden Loop Note based on triggers and conditions.
        """
        price_trigger = self.equity_index > self.barrier_level
        vol_trigger = self.volatility > self.vol_trigger

        if price_trigger and vol_trigger:
            # Both triggers met: Lookback Call payoff
            return self.lookback_call_payoff(path_minimum)
        elif price_trigger or vol_trigger:
            # One trigger met: Fixed coupon (e.g., 5%)
            return 0.05 * self.equity_index
        else:
            # Neither trigger met: Zero or partial capital return
            return 0.8 * self.equity_index  # Example: 80% capital return

# Example usage
if __name__ == "__main__":
    # Initialize the pricing model with example parameters
    pricing_model = ForbiddenLoopNotePricing(
        equity_index=3500,  # Example equity index level
        volatility=0.25,  # Example market volatility
        barrier_level=3400,  # Example barrier level (K1)
        vol_trigger=0.2,  # Example volatility trigger (θ)
        participation_rate=1.5  # Example participation rate (150%)
    )

    # Example path minimum for Lookback Call
    path_minimum = 3300

    # Calculate the payoff
    payoff = pricing_model.calculate_payoff(path_minimum)
    print(f"Calculated Payoff: {payoff}")