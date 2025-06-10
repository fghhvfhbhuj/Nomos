import numpy as np
import matplotlib.pyplot as plt

# Constants
BASELINE_RETURN = 0.12  # 12% p.a.
# Original Enhanced Return and Early Redemption constants (can be used as defaults)
ORIGINAL_ENHANCED_RETURN_MIN = 0.18  # 18% p.a.
ORIGINAL_ENHANCED_RETURN_MAX = 0.28  # 28% p.a.
ORIGINAL_EARLY_REDEMPTION_RETURN = 0.10  # 10% accrued
TENOR_MONTHS = 18
NOTIONAL = 1_000_000  # USD

# NEW: Default parameters for the model, can be overridden for "optimization"
DEFAULT_VOLATILITY_DRIFT = 0.0
DEFAULT_VOLATILITY_STD_DEV = 0.02
DEFAULT_TRIGGER_PERCENTILE = 90.0
DEFAULT_ENHANCED_RETURN_MIN = ORIGINAL_ENHANCED_RETURN_MIN
DEFAULT_ENHANCED_RETURN_MAX = ORIGINAL_ENHANCED_RETURN_MAX
DEFAULT_EARLY_REDEMPTION_RETURN = ORIGINAL_EARLY_REDEMPTION_RETURN

# Modified simulate_volatility_index
def simulate_volatility_index(months, drift=DEFAULT_VOLATILITY_DRIFT, std_dev=DEFAULT_VOLATILITY_STD_DEV, seed=None):
    if seed is not None:
        np.random.seed(seed)
    # Simulate volatility changes with potential drift and configurable std_dev
    return np.cumsum(np.random.normal(drift, std_dev, months))

# Modified calculate_return
def calculate_return(volatility_index, trigger_percentile=DEFAULT_TRIGGER_PERCENTILE, enhanced_min=DEFAULT_ENHANCED_RETURN_MIN, enhanced_max=DEFAULT_ENHANCED_RETURN_MAX):
    trigger_threshold = np.percentile(volatility_index, trigger_percentile)
    if not volatility_index.size: # Handle empty volatility_index if it occurs
        return BASELINE_RETURN
    if volatility_index[-1] > trigger_threshold:
        return np.random.uniform(enhanced_min, enhanced_max)
    return BASELINE_RETURN

# Modified check_early_redemption
def check_early_redemption(volatility_index, trigger_percentile=DEFAULT_TRIGGER_PERCENTILE):
    if not volatility_index.size: # Handle empty volatility_index
        return False
    trigger_threshold = np.percentile(volatility_index, trigger_percentile)
    if volatility_index[-1] > trigger_threshold:
        return True
    return False

# Modified pricing_model
def pricing_model(
    vol_drift=DEFAULT_VOLATILITY_DRIFT,
    vol_std_dev=DEFAULT_VOLATILITY_STD_DEV,
    trig_percentile=DEFAULT_TRIGGER_PERCENTILE,
    enh_min=DEFAULT_ENHANCED_RETURN_MIN,
    enh_max=DEFAULT_ENHANCED_RETURN_MAX,
    early_red_return=DEFAULT_EARLY_REDEMPTION_RETURN,
    seed_val=None # Use a specific seed for this run if provided
):
    volatility_index = simulate_volatility_index(TENOR_MONTHS, drift=vol_drift, std_dev=vol_std_dev, seed=seed_val)

    if check_early_redemption(volatility_index, trigger_percentile=trig_percentile):
        return NOTIONAL * (1 + early_red_return)
    else:
        annualized_return = calculate_return(volatility_index, trigger_percentile=trig_percentile, enhanced_min=enh_min, enhanced_max=enh_max)
        return NOTIONAL * (1 + annualized_return * (TENOR_MONTHS / 12))

# Modified Visualization
def visualize_results():
    simulations = 1000
    
    # Scenario 1: "Standard" Parameters (mimicking original intent but with proper simulation variance)
    standard_results = []
    for i in range(simulations):
        # Pass a unique seed for each simulation run to get a distribution
        standard_results.append(pricing_model(seed_val=(42 + i)))

    # Scenario 2: "SPV Optimized" Parameters (example of SPV tuning for its benefit)
    optimized_results = []
    spv_vol_drift = -0.005          # Suppress volatility slightly
    spv_trig_percentile = 95.0     # Make trigger harder to achieve
    spv_enh_min = DEFAULT_ENHANCED_RETURN_MIN 
    spv_enh_max = DEFAULT_ENHANCED_RETURN_MIN + 0.02 # Narrow enhanced range to lower side
    # spv_early_red_return could also be a parameter, kept default here

    for i in range(simulations):
        # Pass a unique seed, different from the standard set
        optimized_results.append(pricing_model(
            vol_drift=spv_vol_drift,
            trig_percentile=spv_trig_percentile,
            enh_min=spv_enh_min,
            enh_max=spv_enh_max,
            seed_val=(42 + i + simulations) 
        ))

    plt.figure(figsize=(12, 7))
    
    # Determine common bins for fair comparison
    all_results = standard_results + optimized_results
    min_val = min(all_results)
    max_val = max(all_results)
    bins = np.linspace(min_val, max_val, 35)

    plt.hist(standard_results, bins=bins, alpha=0.7, label='Standard Parameters', color='skyblue', edgecolor='black')
    plt.hist(optimized_results, bins=bins, alpha=0.7, label='SPV "Optimized" Parameters', color='salmon', edgecolor='black')
    
    avg_standard = np.mean(standard_results)
    avg_optimized = np.mean(optimized_results)
    
    plt.axvline(avg_standard, color='blue', linestyle='dashed', linewidth=1, label=f'Avg Standard: ${avg_standard:,.0f}')
    plt.axvline(avg_optimized, color='red', linestyle='dashed', linewidth=1, label=f'Avg Optimized: ${avg_optimized:,.0f}')
    
    plt.title('Distribution of Returns: Standard vs. SPV "Optimized" ({} Simulations)'.format(simulations))
    plt.xlabel('Final Payout (USD)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(axis='y', alpha=0.75)
    
    plt.savefig('simulation_charts/return_distribution_comparison.png')
    # plt.show() # Avoid showing plot in automated environment if it blocks
    print("Comparison chart saved to simulation_charts/return_distribution_comparison.png")

if __name__ == "__main__":
    visualize_results()