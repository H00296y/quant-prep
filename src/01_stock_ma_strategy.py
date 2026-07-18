"""
股票双均线策略回测
"""

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. 获取数据
print("正在下载数据...")
df = ak.stock_zh_a_hist(
    symbol="600519", 
    period="daily",
    start_date="20200101", 
    end_date="20251231", 
    adjust="qfq"
)
print(f"下载完成，共 {len(df)} 条数据")

# 2. 计算均线
df['MA5'] = df['收盘'].rolling(window=5).mean()
df['MA20'] = df['收盘'].rolling(window=20).mean()

# 3. 生成交易信号
df['signal'] = 0
df.loc[df['MA5'] > df['MA20'], 'signal'] = 1   # 买入/持仓
df.loc[df['MA5'] <= df['MA20'], 'signal'] = -1  # 卖出/空仓

# 4. 计算策略收益
df['daily_return'] = df['收盘'].pct_change()
df['strategy_return'] = df['signal'].shift(1) * df['daily_return']
df['cum_return'] = (1 + df['strategy_return']).cumprod()
df['buy_hold_return'] = (1 + df['daily_return']).cumprod()

# 5. 计算指标
sharpe = df['strategy_return'].mean() / df['strategy_return'].std() * np.sqrt(252)
max_dd = (df['cum_return'].cummax() - df['cum_return']).max() / df['cum_return'].cummax().max()

print(f"\n===== 策略绩效 =====")
print(f"夏普比率: {sharpe:.2f}")
print(f"最大回撤: {max_dd:.2%}")

# 6. 画图
plt.figure(figsize=(14, 8))

# 子图1：价格与均线
plt.subplot(2, 1, 1)
plt.plot(df['日期'], df['收盘'], label='收盘价', alpha=0.6)
plt.plot(df['日期'], df['MA5'], label='MA5', linewidth=1)
plt.plot(df['日期'], df['MA20'], label='MA20', linewidth=1)
plt.legend()
plt.title("600519 贵州茅台 - 双均线策略")

# 子图2：累计收益对比
plt.subplot(2, 1, 2)
plt.plot(df['日期'], df['cum_return'], label='策略收益', linewidth=2)
plt.plot(df['日期'], df['buy_hold_return'], label='买入持有', alpha=0.6)
plt.legend()
plt.title("累计收益率对比")

plt.tight_layout()
plt.savefig('ma_strategy_result.png', dpi=150)
print("\n图表已保存为 ma_strategy_result.png")
plt.show()