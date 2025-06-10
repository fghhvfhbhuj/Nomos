import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from tqdm import tqdm
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PricingModel:
    def __init__(self, S0, mu, sigma, T, dt, M, tick_size, margin_ratio, initial_equity, payout, tick_threshold):
        self.S0 = S0
        self.mu = mu
        self.sigma = sigma
        self.T = T
        self.dt = dt
        self.N = int(T / dt)
        self.M = M
        self.tick_size = tick_size
        self.margin_ratio = margin_ratio
        self.initial_equity = initial_equity
        self.strong_line = initial_equity * (1 - margin_ratio)
        self.payout = payout
        self.tick_threshold = tick_threshold
        self.output_dir = './simulation_charts'
        os.makedirs(self.output_dir, exist_ok=True)

    def is_jump_triggered(self, price_path):
        for i in range(self.tick_threshold, len(price_path)):
            ticks = price_path[i - self.tick_threshold:i]
            deltas = np.diff(ticks)
            if np.all(deltas < -self.tick_size):
                pre_equity = self.initial_equity * (ticks[-2] / self.S0)
                now_equity = self.initial_equity * (ticks[-1] / self.S0)
                if pre_equity > self.strong_line and now_equity < self.strong_line:
                    return True
        return False

    def simulate(self):
        triggered_count = 0
        results = []
        example_trigger = None

        logging.info("开始模拟路径...")
        for _ in tqdm(range(self.M)):
            Z = np.random.normal(size=self.N)
            price_path = self.S0 * np.exp(np.cumsum((self.mu - 0.5 * self.sigma**2) * self.dt + self.sigma * np.sqrt(self.dt) * Z))
            if self.is_jump_triggered(price_path):
                triggered_count += 1
                if example_trigger is None:
                    example_trigger = price_path
            results.append(price_path)

        trigger_prob = triggered_count / self.M
        price = self.payout * trigger_prob

        logging.info("模拟完成，开始输出结果...")
        logging.info(f"模拟次数: {self.M}, 赔付金额: {self.payout}, 触发比例: {trigger_prob:.4f}, 结构价格: {price:.2f}")

        if example_trigger is not None:
            self.save_example_chart(example_trigger)

        self.save_results(results)

    def save_example_chart(self, example_trigger):
        plt.figure(figsize=(10, 4))
        plt.plot(example_trigger, label='示例路径')
        plt.axhline(self.S0 * (1 - self.margin_ratio), linestyle='--', color='red', label='强平线')
        plt.title('Day003: Tick Jump Path Example')
        plt.xlabel('时间')
        plt.ylabel('价格')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'price_jump_demo.png'))
        plt.close()

    def save_results(self, results):
        mean_path = np.mean(results, axis=0)
        df = pd.DataFrame({'time': np.arange(self.N), 'mean_price': mean_path})
        df.to_csv('pricing_result_day003.csv', index=False)

if __name__ == "__main__":
    model = PricingModel(
        S0=100,
        mu=0.02,
        sigma=0.3,
        T=1 / 12,
        dt=1 / 252,
        M=10000,
        tick_size=0.5,
        margin_ratio=0.1,
        initial_equity=10000,
        payout=1000,
        tick_threshold=3
    )
    model.simulate()
