import numpy as np
import matplotlib.pyplot as plt

# Constants for payout function
EPSILON_V = 0.1  # 10% threshold for volatility change
EPSILON_P = 0.02  # 2% threshold for Nikkei change
C = 100  # Fixed payout for both conditions met
B = 50   # Payout for Nikkei condition met
A = 30   # Payout for volatility condition met

# Simulate BOJ event and market response
def simulate_boj_event(pre_volatility, post_volatility, pre_nikkei, post_nikkei):
    delta_v = abs(post_volatility - pre_volatility)
    delta_p = abs(post_nikkei - pre_nikkei)

    if delta_v < EPSILON_V and delta_p < EPSILON_P:
        return C
    elif delta_p < EPSILON_P:
        return B
    elif delta_v < EPSILON_V:
        return A
    else:
        return 0

# Add behavior-window clause
def behavior_window_payout(pre_volatility, post_volatility, pre_nikkei, post_nikkei):
    """
    Calculate enhanced payout based on market behavior within T+3.

    Returns:
        float: Enhanced payout if market reacts inconsistently.
    """
    delta_v = abs(post_volatility - pre_volatility)
    delta_p = abs(post_nikkei - pre_nikkei)

    if delta_v > EPSILON_V and delta_p < EPSILON_P:
        return C * 1.5  # Enhanced payout for inconsistent behavior
    return simulate_boj_event(pre_volatility, post_volatility, pre_nikkei, post_nikkei)

# Generate simulation data
np.random.seed(42)  # For reproducibility
pre_volatility = np.random.uniform(0.1, 0.3, 100)
post_volatility = np.random.uniform(0.1, 0.3, 100)
pre_nikkei = np.random.uniform(20000, 30000, 100)
post_nikkei = np.random.uniform(20000, 30000, 100)

payouts = [simulate_boj_event(v1, v2, n1, n2) for v1, v2, n1, n2 in zip(pre_volatility, post_volatility, pre_nikkei, post_nikkei)]

# Ensure simulate_market_misinterpretation is defined before usage
def simulate_market_misinterpretation():
    """
    Simulate probability of market misinterpretation.

    Returns:
        float: Probability value between 0 and 1.
    """
    return np.random.uniform(0.5, 1.0)  # Example: 50% to 100% probability

# Enhanced payout calculation with misinterpretation probability
payouts_with_misinterpretation = [
    behavior_window_payout(v1, v2, n1, n2) * simulate_market_misinterpretation()
    for v1, v2, n1, n2 in zip(pre_volatility, post_volatility, pre_nikkei, post_nikkei)
]

# Visualize payout surface
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(pre_volatility, pre_nikkei, payouts, c=payouts, cmap='viridis', marker='o')
ax.set_xlabel('Pre-event Volatility')
ax.set_ylabel('Pre-event Nikkei')
ax.set_zlabel('Payout')
plt.title('Payout Surface')
plt.savefig('simulation_charts/payout_surface.png')
plt.show()

# Visualize enhanced payout surface
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_trisurf(pre_volatility, pre_nikkei, payouts_with_misinterpretation, cmap='viridis', alpha=0.8)
ax.set_xlabel('Pre-event Volatility')
ax.set_ylabel('Pre-event Nikkei')
ax.set_zlabel('Enhanced Payout')
plt.title('Enhanced Payout Surface with Misinterpretation Probability')
plt.savefig('simulation_charts/enhanced_payout_surface.png')
plt.show()

# Visualize volatility spread
plt.figure(figsize=(10, 6))
plt.hist(post_volatility - pre_volatility, bins=20, color='blue', alpha=0.7, label='Volatility Spread')
plt.axvline(EPSILON_V, color='red', linestyle='--', label='Threshold')
plt.xlabel('Volatility Change')
plt.ylabel('Frequency')
plt.title('Volatility Spread Distribution')
plt.legend()
plt.savefig('simulation_charts/volatility_spread.png')
plt.show()

# Visualize gamma P&L (simplified example)
gamma_pnl = np.random.normal(0, 1, 100)  # Simulated gamma P&L
plt.figure(figsize=(10, 6))
plt.plot(gamma_pnl, color='green', label='Gamma P&L')
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Simulation Index')
plt.ylabel('Gamma P&L')
plt.title('Gamma P&L Over Simulations')
plt.legend()
plt.savefig('simulation_charts/gamma_pnl.png')
plt.show()

# Simulate structural replication cost
def simulate_structural_replication_cost():
    """
    Measure cost for hedge fund to replicate note via vanilla instruments.

    Returns:
        float: Estimated replication cost.
    """
    return np.random.uniform(10, 50)  # Example: cost in basis points

# Simulate replication cost visualization
replication_costs = [simulate_structural_replication_cost() for _ in range(100)]
plt.figure(figsize=(10, 6))
plt.hist(replication_costs, bins=20, color='cyan', alpha=0.7, label='Replication Costs')
plt.xlabel('Cost (Basis Points)')
plt.ylabel('Frequency')
plt.title('Structural Replication Cost Distribution')
plt.legend()
plt.savefig('simulation_charts/replication_cost_distribution.png')
plt.show()

# Ensure reverse_mizuchi_payout is defined before usage
def reverse_mizuchi_payout(pre_volatility, post_volatility, pre_nikkei, post_nikkei):
    """
    Calculate payout for reverse Mizuchi structure.

    Returns:
        float: Payout if market reacts efficiently.
    """
    delta_v = abs(post_volatility - pre_volatility)
    delta_p = abs(post_nikkei - pre_nikkei)

    if delta_v > EPSILON_V and delta_p > EPSILON_P:
        return C * 2  # Higher payout for efficient market reaction
    return 0

reverse_payouts = [
    reverse_mizuchi_payout(v1, v2, n1, n2)
    for v1, v2, n1, n2 in zip(pre_volatility, post_volatility, pre_nikkei, post_nikkei)
]

# Visualize reverse Mizuchi payout
plt.figure(figsize=(10, 6))
plt.plot(reverse_payouts, color='magenta', label='Reverse Mizuchi Payouts')
plt.xlabel('Simulation Index')
plt.ylabel('Payout')
plt.title('Reverse Mizuchi Structure Payouts')
plt.legend()
plt.savefig('simulation_charts/reverse_mizuchi_payouts.png')
plt.show()

# Advanced visualization: Combined analysis
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# Payout histogram
axs[0, 0].hist(payouts, bins=10, color='purple', alpha=0.7, label='Payout Distribution')
axs[0, 0].set_title('Payout Distribution')
axs[0, 0].set_xlabel('Payout')
axs[0, 0].set_ylabel('Frequency')
axs[0, 0].legend()

# Volatility vs Payout
axs[0, 1].scatter(pre_volatility, payouts, c=payouts, cmap='plasma', marker='x')
axs[0, 1].set_title('Volatility vs Payout')
axs[0, 1].set_xlabel('Pre-event Volatility')
axs[0, 1].set_ylabel('Payout')

# Nikkei vs Payout
axs[1, 0].scatter(pre_nikkei, payouts, c=payouts, cmap='coolwarm', marker='^')
axs[1, 0].set_title('Nikkei vs Payout')
axs[1, 0].set_xlabel('Pre-event Nikkei')
axs[1, 0].set_ylabel('Payout')

# Combined volatility and Nikkei analysis
axs[1, 1].scatter(pre_volatility, pre_nikkei, c=payouts, cmap='viridis', marker='o')
axs[1, 1].set_title('Volatility and Nikkei Combined')
axs[1, 1].set_xlabel('Pre-event Volatility')
axs[1, 1].set_ylabel('Pre-event Nikkei')

plt.tight_layout()
plt.savefig('simulation_charts/combined_analysis.png')
plt.show()

# Pricing function for the structured note
def calculate_note_price(pre_volatility, post_volatility, pre_nikkei, post_nikkei, risk_free_rate=0.01, maturity=0.5):
    """
    Calculate the price of the structured note based on market conditions.

    Parameters:
        pre_volatility (float): Pre-event implied volatility.
        post_volatility (float): Post-event implied volatility.
        pre_nikkei (float): Pre-event Nikkei index value.
        post_nikkei (float): Post-event Nikkei index value.
        risk_free_rate (float): Risk-free interest rate (default: 1%).
        maturity (float): Maturity of the note in years (default: 6 months).

    Returns:
        float: Estimated price of the structured note.
    """
    delta_v = abs(post_volatility - pre_volatility)
    delta_p = abs(post_nikkei - pre_nikkei)

    # Base price calculation
    base_price = 100  # Assume a nominal value of 100

    # Adjustments based on market conditions
    volatility_adjustment = max(0, (EPSILON_V - delta_v) * 10)
    nikkei_adjustment = max(0, (EPSILON_P - delta_p) * 5)

    # Time value adjustment
    time_value = base_price * np.exp(-risk_free_rate * maturity)

    # Final price
    final_price = time_value + volatility_adjustment + nikkei_adjustment
    return final_price

# Adjusted pricing function for the structured note
def calculate_note_price(pre_volatility, post_volatility, pre_nikkei, post_nikkei, risk_free_rate=0.01, maturity=0.5):
    """
    Adjusted pricing function to lower the price while shifting advantage to the issuer.

    Parameters:
        pre_volatility (float): Pre-event implied volatility.
        post_volatility (float): Post-event implied volatility.
        pre_nikkei (float): Pre-event Nikkei index value.
        post_nikkei (float): Post-event Nikkei index value.
        risk_free_rate (float): Risk-free interest rate (default: 1%).
        maturity (float): Maturity of the note in years (default: 6 months).

    Returns:
        float: Adjusted price of the structured note.
    """
    delta_v = abs(post_volatility - pre_volatility)
    delta_p = abs(post_nikkei - pre_nikkei)

    # Base price calculation
    base_price = 90  # Lower nominal value to make the note appear cheaper

    # Adjustments based on market conditions
    volatility_adjustment = max(0, (EPSILON_V - delta_v) * 5)  # Reduced adjustment for volatility
    nikkei_adjustment = max(0, (EPSILON_P - delta_p) * 3)  # Reduced adjustment for Nikkei

    # Time value adjustment
    time_value = base_price * np.exp(-risk_free_rate * maturity)

    # Hidden issuer advantage: Add a fixed issuer fee
    issuer_fee = 10  # Fixed fee benefiting the issuer

    # Final price
    final_price = time_value + volatility_adjustment + nikkei_adjustment - issuer_fee
    return final_price

# Example usage
note_prices = [
    calculate_note_price(v1, v2, n1, n2)
    for v1, v2, n1, n2 in zip(pre_volatility, post_volatility, pre_nikkei, post_nikkei)
]

# Visualize adjusted note pricing
plt.figure(figsize=(10, 6))
plt.plot(note_prices, color='red', label='Adjusted Structured Note Prices')
plt.xlabel('Simulation Index')
plt.ylabel('Price')
plt.title('Adjusted Structured Note Pricing')
plt.legend()
plt.savefig('simulation_charts/adjusted_note_pricing.png')
plt.show()

# Define allocation strategy for diversified investments
def design_investment_strategy():
    """
    Design a diversified investment strategy to balance issuer advantage and customer appeal.

    Returns:
        dict: Allocation percentages for each asset.
    """
    # Define asset classes and their weights
    asset_classes = {
        "Nikkei 225": 0.4,  # 40% allocation
        "USD/JPY": 0.3,    # 30% allocation
        "Brent Crude": 0.2, # 20% allocation
        "VIX Index": 0.1    # 10% allocation
    }

    # Strategy logic: Adjust weights dynamically based on market conditions
    # For simplicity, we use fixed weights here, but dynamic adjustments can be implemented
    return asset_classes

# Example usage of investment strategy
investment_strategy = design_investment_strategy()

# Visualize investment strategy
plt.figure(figsize=(8, 6))
plt.bar(investment_strategy.keys(), investment_strategy.values(), color=['blue', 'green', 'orange', 'red'])
plt.xlabel('Asset Classes')
plt.ylabel('Allocation Percentage')
plt.title('Diversified Investment Strategy')
plt.savefig('simulation_charts/investment_strategy.png')
plt.show()