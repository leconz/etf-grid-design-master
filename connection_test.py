#!/usr/bin/env python3
"""
测试脚本：只测试富途API的连接情况
"""

import futu as ft

def test_connection():
    """测试富途API连接"""
    print("测试富途API连接...")
    print("=" * 50)
    
    try:
        # 尝试连接到富途API
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        print("✓ 成功连接到富途API")
        
        # 测试获取服务器时间
        ret, data = quote_ctx.get_cur_kline('SH.000001', 1, ft.KLType.K_DAY)
        if ret == ft.RET_OK:
            print("✓ 成功调用API获取数据")
        else:
            print(f"✗ API调用失败: {data}")
        
        # 关闭连接
        quote_ctx.close()
        print("✓ 成功关闭连接")
        
    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        print("可能原因：")
        print("- 富途牛牛客户端未启动")
        print("- 富途牛牛的API服务未开启")
        print("- 端口号不正确（默认11111）")
        print("- 网络连接问题")

if __name__ == "__main__":
    test_connection()