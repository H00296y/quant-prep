"""
可转债低溢价率筛选器
使用模拟数据演示可转债筛选策略
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体（防止方块）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def generate_mock_cb_data(n=50, seed=42):
    """
    生成模拟可转债数据
    
    Parameters:
        n (int): 可转债数量
        seed (int): 随机种子
    
    Returns:
        pd.DataFrame: 包含转债名称、价格、转股价值、溢价率等
    """
    np.random.seed(seed)
    
    # 转债代码和名称
    industries = ['银行', '医药', '科技', '新能源', '消费', '化工', '机械']
    names = [f'{industries[i % len(industries)]}转债{i+1:02d}' for i in range(n)]
    codes = [f'12{i+1:04d}.SH' if i % 2 == 0 else f'12{i+1:04d}.SZ' for i in range(n)]
    
    # 生成数据
    # 转股价值：正股价格 / 转股价 * 100，通常在 70-150 之间
    conversion_value = np.random.uniform(60, 150, n)
    
    # 转债价格：通常在 90-150 之间，与转股价值相关
    price = conversion_value * np.random.uniform(0.8, 1.3, n)
    price = np.clip(price, 85, 160)  # 限制在合理范围
    
    # 溢价率 = (转债价格 - 转股价值) / 转股价值 * 100
    premium_rate = (price - conversion_value) / conversion_value * 100
    
    # 到期收益率（简化计算）
    ytm = np.random.uniform(-5, 8, n)
    
    df = pd.DataFrame({
        '转债代码': codes,
        '转债名称': names,
        '转债价格': np.round(price, 2),
        '转股价值': np.round(conversion_value, 2),
        '转股溢价率': np.round(premium_rate, 2),
        '到期收益率': np.round(ytm, 3),
    })
    
    return df


# ==================== 筛选逻辑 ====================

print("=" * 60)
print("可转债筛选器 - 双低策略")
print("=" * 60)

# 1. 获取数据
df = generate_mock_cb_data(n=50)
print(f"\n全市场共 {len(df)} 只可转债\n")
print(df.head(10).to_string(index=False))

# 2. 筛选条件
# 条件1：转股溢价率 < 30%
# 条件2：转债价格 < 130元
# 条件3：到期收益率 > 0%

condition1 = df['转股溢价率'] < 30
condition2 = df['转债价格'] < 130
condition3 = df['到期收益率'] > 0

filtered = df[condition1 & condition2 & condition3].copy()

print(f"\n{'=' * 60}")
print(f"筛选结果：满足条件的可转债共 {len(filtered)} 只")
print(f"筛选条件：溢价率<30% | 价格<130元 | 到期收益率>0%")
print(f"{'=' * 60}")

if len(filtered) > 0:
    # 按溢价率排序
    filtered = filtered.sort_values('转股溢价率').reset_index(drop=True)
    print("\n【按溢价率从低到高排序】\n")
    print(filtered.to_string(index=False))
    
    # 计算双低值 = 价格 + 溢价率
    filtered['双低值'] = filtered['转债价格'] + filtered['转股溢价率']
    top10 = filtered.nsmallest(10, '双低值')
    
    print(f"\n{'=' * 60}")
    print("【双低策略 Top 10】（双低值 = 价格 + 溢价率）")
    print(f"{'=' * 60}")
    print(top10[['转债名称', '转债价格', '转股溢价率', '双低值', '到期收益率']].to_string(index=False))
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 图1：价格 vs 溢价率 散点图
    ax1 = axes[0]
    ax1.scatter(df['转股溢价率'], df['转债价格'], alpha=0.4, color='gray', label='全部转债')
    ax1.scatter(filtered['转股溢价率'], filtered['转债价格'], alpha=0.8, color='red', s=60, label='筛选结果')
    ax1.axhline(130, color='blue', linestyle='--', alpha=0.5, label='价格=130')
    ax1.axvline(30, color='blue', linestyle='--', alpha=0.5, label='溢价率=30%')
    ax1.set_xlabel('转股溢价率 (%)')
    ax1.set_ylabel('转债价格 (元)')
    ax1.set_title('可转债价格-溢价率分布')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 图2：Top10 双低值柱状图
    ax2 = axes[1]
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(top10)))
    bars = ax2.barh(top10['转债名称'], top10['双低值'], color=colors)
    ax2.set_xlabel('双低值')
    ax2.set_title('双低策略 Top 10')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 在柱子上标注数值
    for bar, val in zip(bars, top10['双低值']):
        ax2.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val:.1f}', 
                va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('cb_screen_result.png', dpi=150, bbox_inches='tight')
    print("\n图表已保存至: D:\\github\\cb_screen_result.png")
    plt.show()
    
else:
    print("\n没有满足条件的可转债，请放宽筛选条件。")