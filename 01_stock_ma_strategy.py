"""
股票双均线策略回测（模拟数据版）
使用模拟数据演示完整的策略回测框架
实际使用时，将 generate_mock_data() 替换为真实数据接口即可
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def generate_mock_data(start_date='2020-01-01', periods=1200, seed=42):
    """
    生成模拟股票日线数据（随机游走模型）
    
    Parameters:
        start_date (str): 起始日期
        periods (int): 交易日数量（约5年）
        seed (int): 随机种子，保证可复现
    
    Returns:
        pd.DataFrame: 包含日期、开盘、收盘、最高、最低、成交量
    """
    np.random.seed(seed)
    
    # 生成日期序列（排除周末）
    dates = pd.bdate_range(start=start_date, periods=periods)
    
    # 随机游走生成价格
    returns = np.random.normal(loc=0.0005, scale=0.02, size=periods)  # 日均收益0.05%，波动2%
    prices = 100 * np.exp(np.cumsum(returns))  # 从100元开始
    
    # 构造OHLC数据
    df = pd.DataFrame({
        '日期': dates,
        '开盘': prices * (1 + np.random.normal(0, 0.005, periods)),
        '收盘': prices,
        '最高': prices * (1 + np.abs(np.random.normal(0, 0.01, periods))),
        '最低': prices * (1 - np.abs(np.random.normal(0, 0.01, periods))),
        '成交量': np.random.randint(1000000, 10000000, periods)
    })
    
    return df


# ==================== 策略回测主逻辑 ====================

# 1. 获取数据（模拟）
print("正在生成模拟数据...")
df = generate_mock_data(start_date='2020-01-01', periods=1200)
print(f"数据生成完成，共 {len(df)} 条记录，时间跨度：{df['日期'].iloc[0].date()} 至 {df['日期'].iloc[-1].date()}")

# 2. 计算均线
df['MA5'] = df['收盘'].rolling(window=5).mean()
df['MA20'] = df['收盘'].rolling(window=20).mean()

# 3. 生成交易信号
# signal = 1 表示持仓（MA5 > MA20），signal = -1 表示空仓（MA5 <= MA20）
df['signal'] = 0
df.loc[df['MA5'] > df['MA20'], 'signal'] = 1
df.loc[df['MA5'] <= df['MA20'], 'signal'] = -1

# 4. 计算收益
# 日收益率
df['daily_return'] = df['收盘'].pct_change()

# 策略收益：根据前一天的信号决定当天的仓位
# shift(1) 是因为今天收盘后才能确定信号，明天才能执行
df['strategy_return'] = df['signal'].shift(1) * df['daily_return']

# 累计收益
df['cum_strategy'] = (1 + df['strategy_return']).cumprod()
df['cum_buyhold'] = (1 + df['daily_return']).cumprod()

# 5. 计算绩效指标
# 夏普比率 = (日均收益 / 日均波动) * sqrt(252)
sharpe = df['strategy_return'].mean() / df['strategy_return'].std() * np.sqrt(252)

# 最大回撤
cummax = df['cum_strategy'].cummax()
drawdown = (cummax - df['cum_strategy']) / cummax
max_dd = drawdown.max()

# 胜率（有收益的天数 / 总交易天数）
win_rate = (df['strategy_return'] > 0).sum() / (df['strategy_return'] != 0).sum()

print(f"\n{'='*40}")
print("策略绩效报告")
print(f"{'='*40}")
print(f"总收益率:     {(df['cum_strategy'].iloc[-1] - 1):.2%}")
print(f"买入持有收益: {(df['cum_buyhold'].iloc[-1] - 1):.2%}")
print(f"夏普比率:     {sharpe:.2f}")
print(f"最大回撤:     {max_dd:.2%}")
print(f"胜率:         {win_rate:.2%}")
print(f"交易次数:     {(df['signal'].diff() != 0).sum() // 2} 次")
print(f"{'='*40}")

# 6. 可视化
fig, axes = plt.subplots(3, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1, 1]})

# 子图1：价格与均线 + 买卖信号
ax1 = axes[0]
ax1.plot(df['日期'], df['收盘'], label='收盘价', alpha=0.7, linewidth=1)
ax1.plot(df['日期'], df['MA5'], label='MA5', linewidth=1.2, color='orange')
ax1.plot(df['日期'], df['MA20'], label='MA20', linewidth=1.2, color='purple')

# 标记买卖点
buy_signals = df[(df['signal'].shift(1) == -1) & (df['signal'] == 1)]
sell_signals = df[(df['signal'].shift(1) == 1) & (df['signal'] == -1)]
ax1.scatter(buy_signals['日期'], buy_signals['收盘'], marker='^', color='red', s=50, label='买入信号', zorder=5)
ax1.scatter(sell_signals['日期'], sell_signals['收盘'], marker='v', color='green', s=50, label='卖出信号', zorder=5)

ax1.set_title('双均线策略 - 价格与交易信号', fontsize=14)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# 子图2：累计收益对比
ax2 = axes[1]
ax2.plot(df['日期'], df['cum_strategy'], label='策略收益', linewidth=2, color='blue')
ax2.plot(df['日期'], df['cum_buyhold'], label='买入持有', linewidth=1.5, color='gray', alpha=0.7)
ax2.fill_between(df['日期'], 1, df['cum_strategy'], alpha=0.2, color='blue')
ax2.set_title('累计收益率对比', fontsize=12)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

# 子图3：回撤曲线
ax3 = axes[2]
ax3.fill_between(df['日期'], 0, drawdown, color='red', alpha=0.3)
ax3.plot(df['日期'], drawdown, color='red', linewidth=1)
ax3.set_title('策略回撤', fontsize=12)
ax3.set_ylabel('回撤幅度')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('ma_strategy_result.png', dpi=150, bbox_inches='tight')
print("\n图表已保存至: D:\\github\\ma_strategy_result.png")
plt.show()