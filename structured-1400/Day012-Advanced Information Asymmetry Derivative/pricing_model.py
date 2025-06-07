import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from scipy.stats import norm
import warnings
import os
warnings.filterwarnings('ignore')

class InformationAsymmetryDerivative:
    """
    Advanced Information Asymmetry Derivative Pricing Model
    """
    
    def __init__(self):
        self.risk_free_rate = 0.05
        self.market_volatility = 0.2
        
    def calculate_information_curvature(self, transparency_factor, user_level, time_to_maturity=1.0):
        """Calculate curvature based on information asymmetry"""
        gaussian_curvature = np.exp(-2 * transparency_factor) / (user_level ** 0.5)
        time_decay = np.exp(-0.1 * time_to_maturity)
        total_curvature = gaussian_curvature * time_decay
        return total_curvature
    
    def black_scholes_base_price(self, S, K, T, r, sigma):
        """Calculate Black-Scholes option price"""
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        call_price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        return call_price
    
    def calculate_compound_option_price(self, term_sheet, user_info):
        """Calculate compound option price with information asymmetry adjustment"""
        # Extract parameters
        underlying_price = term_sheet.get("underlying_price", 100)
        strike_price = term_sheet.get("strike_price", 100)
        time_to_maturity = term_sheet.get("time_to_maturity", 1.0)
        volatility = term_sheet.get("volatility", self.market_volatility)
        
        transparency_factor = user_info.get("transparency_factor", 0.5)
        user_level = user_info.get("user_level", 1.0)
        risk_tolerance = user_info.get("risk_tolerance", 0.5)
        
        # Calculate base option price
        base_price = self.black_scholes_base_price(
            underlying_price, strike_price, time_to_maturity, 
            self.risk_free_rate, volatility
        )
        
        # Calculate information asymmetry curvature
        curvature = self.calculate_information_curvature(
            transparency_factor, user_level, time_to_maturity
        )
        
        # Information asymmetry premium/discount
        asymmetry_adjustment = curvature * (1 - transparency_factor) * base_price
        
        # Risk tolerance adjustment
        risk_adjustment = (1 - risk_tolerance) * 0.1 * base_price
        
        # Final compound option price
        compound_option_price = base_price + asymmetry_adjustment + risk_adjustment
        
        return {
            "compound_option_price": compound_option_price,
            "base_bs_price": base_price,
            "asymmetry_premium": asymmetry_adjustment,
            "risk_adjustment": risk_adjustment,
            "information_curvature": curvature,
            "fair_value_ratio": compound_option_price / base_price
        }
    
    def generate_risk_scenarios(self, term_sheet, user_info, num_scenarios=1000):
        """Monte Carlo simulation for risk scenario analysis"""
        scenario_prices = []
        
        for _ in range(num_scenarios):
            scenario_term_sheet = term_sheet.copy()
            scenario_user_info = user_info.copy()
            
            # Add noise to underlying price and volatility
            scenario_term_sheet["underlying_price"] *= (1 + np.random.normal(0, 0.1))
            scenario_term_sheet["volatility"] *= (1 + np.random.normal(0, 0.2))
            
            # Add noise to transparency factor
            scenario_user_info["transparency_factor"] = np.clip(
                scenario_user_info["transparency_factor"] + np.random.normal(0, 0.1),
                0.01, 0.99
            )
            
            result = self.calculate_compound_option_price(scenario_term_sheet, scenario_user_info)
            scenario_prices.append(result["compound_option_price"])
        
        scenario_prices = np.array(scenario_prices)
        
        return {
            "mean_price": np.mean(scenario_prices),
            "price_std": np.std(scenario_prices),
            "var_95": np.percentile(scenario_prices, 5),
            "var_99": np.percentile(scenario_prices, 1),
            "max_loss": np.min(scenario_prices),
            "max_gain": np.max(scenario_prices),
            "scenario_prices": scenario_prices
        }

def create_visualizations(model, term_sheet, user_info):
    """Create visualizations for the pricing model"""
    try:
        print("📈 Generating visualizations...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Transparency Factor vs Price
        transparency_range = np.linspace(0.01, 0.99, 30)
        prices = []
        
        for trans in transparency_range:
            user_temp = user_info.copy()
            user_temp["transparency_factor"] = trans
            result = model.calculate_compound_option_price(term_sheet, user_temp)
            prices.append(result["compound_option_price"])
        
        ax1.plot(transparency_range, prices, 'b-', linewidth=2)
        ax1.set_xlabel('Transparency Factor')
        ax1.set_ylabel('Compound Option Price')
        ax1.set_title('Price vs Information Transparency')
        ax1.grid(True, alpha=0.3)
        
        # 2. User Level vs Price
        user_levels = np.linspace(0.1, 5.0, 30)
        prices_user = []
        
        for level in user_levels:
            user_temp = user_info.copy()
            user_temp["user_level"] = level
            result = model.calculate_compound_option_price(term_sheet, user_temp)
            prices_user.append(result["compound_option_price"])
        
        ax2.plot(user_levels, prices_user, 'r-', linewidth=2)
        ax2.set_xlabel('User Sophistication Level')
        ax2.set_ylabel('Compound Option Price')
        ax2.set_title('Price vs User Level')
        ax2.grid(True, alpha=0.3)
        
        # 3. Risk Scenario Distribution
        print("🎲 Generating risk scenarios...")
        risk_results = model.generate_risk_scenarios(term_sheet, user_info, 500)
        ax3.hist(risk_results["scenario_prices"], bins=30, alpha=0.7, color='green')
        ax3.axvline(risk_results["mean_price"], color='red', linestyle='--', 
                    label=f'Mean: {risk_results["mean_price"]:.2f}')
        ax3.axvline(risk_results["var_95"], color='orange', linestyle='--', 
                    label=f'95% VaR: {risk_results["var_95"]:.2f}')
        ax3.set_xlabel('Price')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Risk Scenario Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Curvature Surface
        print("📐 Generating curvature surface...")
        trans_grid = np.linspace(0.01, 0.99, 15)
        user_grid = np.linspace(0.1, 3.0, 15)
        X, Y = np.meshgrid(trans_grid, user_grid)
        Z = np.zeros_like(X)
        
        for i in range(len(trans_grid)):
            for j in range(len(user_grid)):
                Z[j, i] = model.calculate_information_curvature(X[j, i], Y[j, i])
        
        contour = ax4.contourf(X, Y, Z, levels=15, cmap='viridis')
        ax4.set_xlabel('Transparency Factor')
        ax4.set_ylabel('User Level')
        ax4.set_title('Information Curvature Surface')
        plt.colorbar(contour, ax=ax4)
        
        plt.tight_layout()
        
        # Ensure directory exists and save
        os.makedirs('simulation_charts', exist_ok=True)
        plt.savefig('simulation_charts/advanced_analysis.png', dpi=300, bbox_inches='tight')
        print("📊 Chart saved to simulation_charts/advanced_analysis.png")
        plt.close()
        
        return risk_results
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        return None

# Main execution
if __name__ == "__main__":
    try:
        print("🚀 Starting Advanced Information Asymmetry Derivative Pricing Model...")
        
        # Initialize model
        model = InformationAsymmetryDerivative()
        print("✅ Model initialized successfully")
        
        # Example parameters
        term_sheet = {
            "underlying_price": 100,
            "strike_price": 105,
            "time_to_maturity": 0.25,
            "volatility": 0.3
        }
        
        user_info = {
            "transparency_factor": 0.3,
            "user_level": 1.5,
            "risk_tolerance": 0.4
        }
        
        print("📋 Calculating pricing...")
        result = model.calculate_compound_option_price(term_sheet, user_info)
        
        print("\n" + "="*60)
        print("🎯 ADVANCED INFORMATION ASYMMETRY DERIVATIVE PRICING")
        print("="*60)
        print(f"💰 Compound Option Price: ${result['compound_option_price']:.4f}")
        print(f"📈 Base Black-Scholes Price: ${result['base_bs_price']:.4f}")
        print(f"⚖️  Information Asymmetry Premium: ${result['asymmetry_premium']:.4f}")
        print(f"🛡️  Risk Adjustment: ${result['risk_adjustment']:.4f}")
        print(f"📐 Information Curvature: {result['information_curvature']:.6f}")
        print(f"📊 Fair Value Ratio: {result['fair_value_ratio']:.4f}")
        
        # Generate visualizations and risk analysis
        risk_results = create_visualizations(model, term_sheet, user_info)
        
        if risk_results:
            print("\n" + "="*40)
            print("🎲 RISK ANALYSIS")
            print("="*40)
            print(f"📊 Mean Price: ${risk_results['mean_price']:.4f}")
            print(f"📈 Price Volatility: ${risk_results['price_std']:.4f}")
            print(f"⚠️  95% VaR: ${risk_results['var_95']:.4f}")
            print(f"🚨 99% VaR: ${risk_results['var_99']:.4f}")
            print(f"📉 Maximum Loss: ${risk_results['max_loss']:.4f}")
            print(f"📈 Maximum Gain: ${risk_results['max_gain']:.4f}")
        
        print("\n✅ All calculations completed successfully!")
        print("🎉 Your advanced derivative pricing model is ready!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()