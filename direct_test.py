#!/usr/bin/env python3
"""
直接测试脚本：直接调用富途API获取159870的历史数据
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

import futu as ft

def direct_test():
    """直接测试富途API获取历史数据"""
    etf_code = "159870"
    days = 30  # 缩短时间范围，减少数据量
    
    # 计算日期范围
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    print(f"直接测试富途API获取ETF {etf_code} 的历史数据 ({start_date}~{end_date})")
    print("=" * 70)
    
    try:
        # 补全ETF代码
        if etf_code.startswith(('15', '16', '18')):
            full_code = f"SZ.{etf_code}"
        elif etf_code.startswith(('51', '58')):
            full_code = f"SH.{etf_code}"
        else:
            full_code = f"SH.{etf_code}"
        
        print(f"1. 使用代码: {full_code}")
        
        # 初始化富途API连接
        print("2. 初始化富途API连接...")
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        time.sleep(1)  # 等待连接建立
        
        # 设置超时
        print("3. 设置API超时...")
        quote_ctx.set_timeout(10)  # 10秒超时
        
        # 直接调用request_history_kline方法
        print("4. 直接调用request_history_kline方法...")
        ret, data, page_req_key = quote_ctx.request_history_kline(
            code=full_code,
            start=start_date,
            end=end_date,
            ktype=ft.KLType.K_DAY,
            autype=ft.AuType.QFQ,
            fields=['time_key', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        )
        
        print(f"5. API调用返回: ret={ret}, data={data}, page_req_key={page_req_key}")
        
        if ret == ft.RET_OK:
            if not data.empty:
                print(f"✓ 成功获取数据，共{len(data)}条记录")
                print("数据示例:")
                print(data.head())
            else:
                print("✗ 未获取到数据，返回数据为空")
        else:
            print(f"✗ API调用失败: ret={ret}, 错误信息: {data}")
        
        # 关闭连接
        quote_ctx.close()
        print("6. 连接已关闭")
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 确保连接关闭
        if 'quote_ctx' in locals():
            quote_ctx.close()

if __name__ == "__main__":
    direct_test()