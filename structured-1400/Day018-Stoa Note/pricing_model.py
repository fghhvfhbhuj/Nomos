import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Optional
import datetime
from scipy.stats import norm

@dataclass
class StoaNoteParameters:
    """Parameters for Stoa Note derivative structure"""
    mu: float = 0.22  # Payout center (%)
    epsilon: float = 0.05  # Friction band (%)
    delta: float = 0.01  # Compression offset (%)
    alpha1: float = 12.0  # Upside payout multiplier
    alpha2: float = 8.0  # Downside payout multiplier
    lambda_anchor: float = 0.65  # Anchoring sensitivity
    tenor_days: int = 7  # Duration in days
    notional: float = 10000  # Notional amount in USD

class StoaNotePricer:
    """Pricing model for Stoa Note derivative structure"""
    
    def __init__(self, params: StoaNoteParameters = None):
        """Initialize with default or provided parameters"""
        self.params = params or StoaNoteParameters()
        
    def calculate_adjusted_fee_index(self, efi: float, anchor: float) -> float:
        """
        Calculate the adjusted fee index using the anchoring mechanism
        
        Args:
            efi: Effective Fee Index value (%)
            anchor: Anchoring variable value (%)
            
        Returns:
            Adjusted fee index f_adj (%)
        """
        return efi - self.params.lambda_anchor * anchor
    
    def calculate_payout(self, f_adj: float) -> float:
        """
        Calculate the payout based on the adjusted fee index
        
        Args:
            f_adj: Adjusted fee index (%)
            
        Returns:
            Payout as a percentage of notional
        """
        mu = self.params.mu
        epsilon = self.params.epsilon
        delta = self.params.delta
        alpha1 = self.params.alpha1
        alpha2 = self.params.alpha2
        
        # Upper threshold
        upper_threshold = mu + epsilon + delta
        # Lower threshold
        lower_threshold = mu - epsilon - delta
        
        if f_adj > upper_threshold:
            # Positive payout scenario
            return alpha1 * (f_adj - upper_threshold)
        elif f_adj < lower_threshold:
            # Negative payout scenario
            return alpha2 * (lower_threshold - f_adj)
        else:
            # No payout within the compressed zone
            return 0.0
    
    def simulate_paths(self, 
                      initial_efi: float, 
                      initial_anchor: float,
                      num_paths: int = 1000, 
                      num_steps: int = 7,
                      efi_volatility: float = 0.30, 
                      anchor_volatility: float = 0.15,
                      correlation: float = 0.60,
                      mean_reversion_efi: float = 0.3,
                      mean_reversion_anchor: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
        """
        优化路径模拟，减少冗余计算并提高代码效率。
        """
        dt = 1.0 / 365  # 每日时间步长

        # 使用Cholesky分解生成相关随机变量
        corr_matrix = np.array([[1, correlation], [correlation, 1]])
        chol = np.linalg.cholesky(corr_matrix)

        # 初始化路径
        efi_paths = np.full((num_paths, num_steps + 1), initial_efi)
        anchor_paths = np.full((num_paths, num_steps + 1), initial_anchor)

        # 长期均值（假设当前值为平衡点）
        efi_mean = initial_efi
        anchor_mean = initial_anchor

        # 使用矢量化操作模拟路径
        for i in range(num_steps):
            z = np.random.normal(0, 1, (2, num_paths))
            correlated_z = np.dot(chol, z)

            efi_paths[:, i+1] += mean_reversion_efi * (efi_mean - efi_paths[:, i]) * dt + \
                                 efi_volatility * efi_paths[:, i] * np.sqrt(dt) * correlated_z[0]

            anchor_paths[:, i+1] += mean_reversion_anchor * (anchor_mean - anchor_paths[:, i]) * dt + \
                                    anchor_volatility * anchor_paths[:, i] * np.sqrt(dt) * correlated_z[1]

            # 确保非负值
            efi_paths[:, i+1] = np.maximum(efi_paths[:, i+1], 0.01)
            anchor_paths[:, i+1] = np.maximum(anchor_paths[:, i+1], 0.01)

        return efi_paths, anchor_paths

    def price_stoa_note(self, 
                       initial_efi: float,
                       initial_anchor: float,
                       risk_free_rate: float = 0.02,
                       num_simulations: int = 10000) -> dict:
        """
        优化定价逻辑，减少冗余计算并提高代码可读性。
        """
        tenor_days = self.params.tenor_days
        notional = self.params.notional

        # 模拟路径
        efi_paths, anchor_paths = self.simulate_paths(
            initial_efi=initial_efi,
            initial_anchor=initial_anchor,
            num_paths=num_simulations,
            num_steps=tenor_days
        )

        # 矢量化计算调整后的费用指数
        f_adj_paths = efi_paths - self.params.lambda_anchor * anchor_paths

        # 计算到期时的支付
        terminal_payouts = np.where(
            f_adj_paths[:, -1] > self.params.mu + self.params.epsilon + self.params.delta,
            self.params.alpha1 * (f_adj_paths[:, -1] - (self.params.mu + self.params.epsilon + self.params.delta)),
            np.where(
                f_adj_paths[:, -1] < self.params.mu - self.params.epsilon - self.params.delta,
                self.params.alpha2 * ((self.params.mu - self.params.epsilon - self.params.delta) - f_adj_paths[:, -1]),
                0.0
            )
        )

        # 计算期望支付和现值
        expected_payout = np.mean(terminal_payouts) / 100 * notional
        discount_factor = np.exp(-risk_free_rate * tenor_days / 365)
        present_value = expected_payout * discount_factor

        return {
            "present_value": present_value,
            "expected_payout_percent": np.mean(terminal_payouts),
            "probability_of_payout": np.mean(terminal_payouts > 0),
            "var_95": np.percentile(terminal_payouts / 100 * notional, 5),
            "max_payout": np.max(terminal_payouts / 100 * notional),
            "average_f_adj": np.mean(f_adj_paths[:, -1])
        }
    
    def analyze_sensitivity(self, 
                          initial_efi: float,
                          initial_anchor: float,
                          parameter: str,
                          param_range: List[float]) -> dict:
        """
        Perform sensitivity analysis on a selected parameter
        
        Args:
            initial_efi: Current Effective Fee Index (%)
            initial_anchor: Current anchor variable (%)
            parameter: Parameter to analyze (e.g., 'mu', 'epsilon', 'lambda_anchor')
            param_range: List of values to test for the parameter
            
        Returns:
            Dictionary with sensitivity analysis results
        """
        original_value = getattr(self.params, parameter)
        results = []
        
        for value in param_range:
            # Temporarily set parameter value
            setattr(self.params, parameter, value)
            
            # Price with new parameter
            price_result = self.price_stoa_note(initial_efi, initial_anchor)
            results.append(price_result["present_value"])
            
        # Reset original value
        setattr(self.params, parameter, original_value)
        
        return {
            "parameter": parameter,
            "values": param_range,
            "present_values": results
        }
    
    def plot_payout_function(self, f_adj_range: Optional[List[float]] = None):
        """
        Plot the payout function for visualization
        
        Args:
            f_adj_range: Optional range of f_adj values to plot
        """
        if f_adj_range is None:
            # Default range around mu
            mu = self.params.mu
            f_adj_range = np.linspace(mu - 0.2, mu + 0.2, 1000)
        
        payouts = [self.calculate_payout(f_adj) for f_adj in f_adj_range]
        
        plt.figure(figsize=(10, 6))
        plt.plot(f_adj_range, payouts)
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        plt.axvline(x=self.params.mu, color='r', linestyle='--', alpha=0.3, 
                   label=f'μ = {self.params.mu}%')
        
        # Add shaded area for compression zone
        epsilon_delta = self.params.epsilon + self.params.delta
        plt.axvspan(self.params.mu - epsilon_delta, 
                   self.params.mu + epsilon_delta, 
                   alpha=0.2, color='gray', 
                   label=f'Compression Zone (ε+δ = {epsilon_delta}%)')
        
        plt.grid(True, alpha=0.3)
        plt.title('Stoa Note Payout Function')
        plt.xlabel('Adjusted Fee Index (f_adj) %')
        plt.ylabel('Payout %')
        plt.legend()
        plt.tight_layout()
        
    def simulate_scenario(self, 
                        scenario_name: str,
                        initial_efi: float,
                        initial_anchor: float,
                        efi_path: List[float],
                        anchor_path: List[float]):
        """
        Analyze a specific scenario with predefined paths
        
        Args:
            scenario_name: Name of the scenario for display
            initial_efi: Starting EFI value
            initial_anchor: Starting anchor value
            efi_path: List of EFI values for each day
            anchor_path: List of anchor values for each day
            
        Returns:
            Dictionary with scenario analysis results
        """
        # Ensure paths start with initial values
        efi_full_path = [initial_efi] + efi_path
        anchor_full_path = [initial_anchor] + anchor_path
        
        # Calculate adjusted fee index
        f_adj_path = [self.calculate_adjusted_fee_index(efi, anchor) 
                     for efi, anchor in zip(efi_full_path, anchor_full_path)]
        
        # Calculate daily payouts
        payouts = [self.calculate_payout(f_adj) for f_adj in f_adj_path]
        
        # Terminal payout
        terminal_payout = payouts[-1]
        terminal_payout_usd = terminal_payout / 100 * self.params.notional
        
        # Create dates for plotting
        start_date = datetime.datetime.now()
        dates = [start_date + datetime.timedelta(days=i) for i in range(len(efi_full_path))]
        
        # Plot results
        fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        
        # Plot EFI and Anchor
        axs[0].plot(dates, efi_full_path, 'b-', label='EFI')
        axs[0].plot(dates, anchor_full_path, 'g--', label='Anchor')
        axs[0].set_title(f'Scenario: {scenario_name}')
        axs[0].set_ylabel('Value (%)')
        axs[0].legend()
        axs[0].grid(alpha=0.3)
        
        # Plot Adjusted Fee Index
        axs[1].plot(dates, f_adj_path, 'r-', label='f_adj')
        axs[1].axhline(y=self.params.mu, color='k', linestyle='--', alpha=0.5, label='μ')
        axs[1].axhspan(self.params.mu - (self.params.epsilon + self.params.delta), 
                      self.params.mu + (self.params.epsilon + self.params.delta), 
                      alpha=0.2, color='gray', label='Compression Zone')
        axs[1].set_ylabel('f_adj (%)')
        axs[1].legend()
        axs[1].grid(alpha=0.3)
        
        # Plot Payouts
        axs[2].plot(dates, payouts, 'm-', label='Payout')
        axs[2].axhline(y=0, color='k', linestyle='--', alpha=0.5)
        axs[2].set_ylabel('Payout (%)')
        axs[2].set_xlabel('Date')
        axs[2].legend()
        axs[2].grid(alpha=0.3)
        
        plt.tight_layout()
        
        return {
            "scenario_name": scenario_name,
            "f_adj_path": f_adj_path,
            "payouts": payouts,
            "terminal_payout_percent": terminal_payout,
            "terminal_payout_usd": terminal_payout_usd
        }


# Example usage
if __name__ == "__main__":
    # Create default parameters
    params = StoaNoteParameters(
        mu=0.22,           # Payout center (%)
        epsilon=0.05,      # Friction band (%)
        delta=0.01,        # Compression offset (%)
        alpha1=12.0,       # Upside payout multiplier
        alpha2=8.0,        # Downside payout multiplier
        lambda_anchor=0.65, # Anchoring sensitivity
        tenor_days=7,      # Duration in days
        notional=10000     # Notional amount in USD
    )
    
    # Initialize pricer
    pricer = StoaNotePricer(params)
    
    # Price the note
    initial_efi = 0.20  # Initial Effective Fee Index (%)
    initial_anchor = 0.18  # Initial anchor value (%)
    
    price_result = pricer.price_stoa_note(
        initial_efi=initial_efi,
        initial_anchor=initial_anchor,
        risk_free_rate=0.02,
        num_simulations=5000
    )
    
    # Print pricing results
    print("==== Stoa Note Pricing Results ====")
    print(f"Present Value: ${price_result['present_value']:.2f}")
    print(f"Expected Payout: {price_result['expected_payout_percent']:.4f}%")
    print(f"Probability of Payout: {price_result['probability_of_payout'] * 100:.2f}%")
    print(f"95% VaR: ${price_result['var_95']:.2f}")
    print(f"Maximum Payout: ${price_result['max_payout']:.2f}")
    print(f"Average Terminal f_adj: {price_result['average_f_adj']:.4f}%")
    
    # Plot payout function
    pricer.plot_payout_function()
    
    # Analyze Scenario 1: ETH Gas Surge on NFT Minting Day (from scenario-examples.md)
    print("\n==== Scenario Analysis: ETH Gas Surge on NFT Minting Day ====")
    scenario1 = pricer.simulate_scenario(
        scenario_name="ETH Gas Surge on NFT Minting Day",
        initial_efi=0.19,
        initial_anchor=0.18,
        efi_path=[0.21, 0.25, 0.30, 0.42, 0.38, 0.29, 0.22],  # Simulated daily EFI values
        anchor_path=[0.18, 0.19, 0.20, 0.22, 0.21, 0.20, 0.19]  # Simulated daily anchor values
    )
    print(f"Terminal Payout: {scenario1['terminal_payout_percent']:.4f}%")
    print(f"Terminal Payout (USD): ${scenario1['terminal_payout_usd']:.2f}")
    
    # Sensitivity analysis on lambda_anchor
    lambda_range = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    sensitivity = pricer.analyze_sensitivity(
        initial_efi=initial_efi,
        initial_anchor=initial_anchor,
        parameter="lambda_anchor",
        param_range=lambda_range
    )
    
    # Plot sensitivity analysis
    plt.figure(figsize=(10, 6))
    plt.plot(sensitivity["values"], sensitivity["present_values"], 'bo-')
    plt.grid(True, alpha=0.3)
    plt.title('Sensitivity to Anchoring Parameter (λ)')
    plt.xlabel('Lambda Value')
    plt.ylabel('Present Value ($)')
    plt.tight_layout()
    
    plt.show()