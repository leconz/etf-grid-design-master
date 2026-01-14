#!/usr/bin/env python3
"""
测试脚本：直接调用get_etf_daily_data方法
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from backend.services.data.futu_client import futuClient

def test_get_etf_daily_data():
    """测试get_etf_daily_data方法"""
    etf_code = "510300"  # 沪深300ETF
    days = 30  # 获取最近30天的数据
    
    # 计算日期范围
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    print(f"直接调用get_etf_daily_data方法")
    print(f"ETF代码: {etf_code}")
    print(f"日期范围: {start_date} ~ {end_date}")
    print("=" * 60)
    
    try:
        # 创建富途客户端实例
        client = futuClient()
        print("✓ 富途客户端初始化成功")
        
        # 直接调用get_etf_daily_data方法
        print(f"调用get_etf_daily_data('{etf_code}', '{start_date}', '{end_date}')")
        df = client.get_etf_daily_data(etf_code, start_date, end_date)
        
        if df is not None and len(df) > 0:
            print(f"✓ 成功获取数据，共{len(df)}条记录")
            print("\n数据示例:")
            print(df[['trade_date', 'open', 'high', 'low', 'close']].head())
            print("\n数据统计:")
            print(f"- 数据起始日期: {df['trade_date'].min().strftime('%Y-%m-%d')}")
            print(f"- 数据结束日期: {df['trade_date'].max().strftime('%Y-%m-%d')}")
            print(f"- 数据天数: {len(df)}")
        else:
            print("✗ 未获取到数据")
            
    except Exception as e:
        print(f"✗ 调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭客户端连接（如果有close方法）
        if 'client' in locals() and hasattr(client, 'close'):
            client.close()
            print("✓ 客户端已关闭")

if __name__ == "__main__":
    test_get_etf_daily_data()