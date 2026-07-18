"""
数据获取工具函数
"""

import akshare as ak
def get_stock_data(symbol, start_date, end_date):
    """
    获取A股历史行情数据
    
    Parameters:
        symbol (str): 股票代码，如 "600519"
        start_date (str): 开始日期，如 "20200101"
        end_date (str): 结束日期，如 "20251231"
    
    Returns:
        pd.DataFrame: 包含日期、开盘、收盘、最高、最低、成交量等字段
    """
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"
    )
    return df
