#!/usr/bin/env python3
"""
简单测试脚本：调用富途get_etf_daily_data获取159870的历史数据
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from backend.services.data.futu_client import futuClient

def simple_test():
    """简单测试获取ETF历史数据"""
    etf_code = "588000"
    days = 30  # 缩短时间范围，减少数据量
    
    # 计算日期范围
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    print(f"测试获取ETF {etf_code} 的历史数据 ({start_date}~{end_date})")
    print("=" * 60)
    
    try:
        # 创建富途客户端实例
        futu_client = futuClient()
        print("1. 富途客户端初始化成功")
        
        # 测试代码补全功能
        full_code = futu_client._complete_etf_code(etf_code)
        print(f"2. 代码补全成功: {full_code}")
        
        # 获取历史数据
        print("3. 开始获取历史数据...")
        df = futu_client.get_etf_daily_data(etf_code, start_date, end_date)
        
        if df is not None and len(df) > 0:
            print(f"✓ 成功获取数据，共{len(df)}条记录")
            print("数据示例:")
            print(df[['trade_date', 'open', 'high', 'low', 'close']].head())
        else:
            print("✗ 未获取到数据")
            print("可能原因：")
            print("- 富途API可能没有该ETF的数据")
            print("- ETF代码可能有误")
            print("- 网络连接问题")
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()