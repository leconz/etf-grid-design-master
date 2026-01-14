#!/usr/bin/env python3
"""
测试脚本：直接调用富途get_etf_daily_data获取159870的历史数据
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from backend.services.data.futu_client import futuClient

def test_get_etf_daily_data():
    """测试获取ETF历史数据"""
    etf_code = "159915"
    days = 365
    
    # 计算日期范围
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    print(f"测试获取ETF {etf_code} 的历史数据 ({start_date}~{end_date})")
    print("=" * 60)
    
    # 只测试富途客户端
    print("测试富途客户端:")
    try:
        futu_client = futuClient()
        print(f"   ✓ 富途客户端初始化完成")
        
        # df_futu = futu_client.get_etf_daily_data(etf_code, start_date, end_date)
        # if df_futu is not None and len(df_futu) > 0:
        #     print(f"   ✓ 成功获取数据，共{len(df_futu)}条记录")
        #     print(f"   数据示例：")
        #     print(df_futu.head())
        # else:
        #     print(f"   ✗ 未获取到数据")
            
            # 检查富途API的_complet_etf_code方法
        full_code = futu_client._complete_etf_code(etf_code)
        print(f"   补全后的代码: {full_code}")
            
            # 直接测试富途API连接
        try:
            # 测试获取基本信息
            basic_info = futu_client.get_etf_basic_info(etf_code)
            print(f"   基本信息: {basic_info}")
        except Exception as e:
            print(f"   获取基本信息失败: {str(e)}")
    except Exception as e:
        print(f"   ✗ 调用失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_etf_daily_data()