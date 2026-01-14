#!/usr/bin/env python3
"""
测试富途API的stock_type参数
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import logging
import futu as ft

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_stock_type():
    """测试不同stock_type参数的效果"""
    # 初始化富途API
    quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    
    try:
        # 测试ETF代码
        etf_code = 'SZ.159919'
        # 测试普通股票代码
        stock_code = 'SZ.300676'
        
        # 测试1: 使用ETF类型查询ETF
        logger.info("=== 测试1: 使用ETF类型查询ETF ===")
        ret, data = quote_ctx.get_stock_basicinfo(market=ft.Market.SZ, stock_type=ft.SecurityType.ETF, code_list=[etf_code])
        logger.info(f"ETF查询结果: ret={ret}, data={data}")
        
        # 测试2: 使用ETF类型查询普通股票
        logger.info("\n=== 测试2: 使用ETF类型查询普通股票 ===")
        ret, data = quote_ctx.get_stock_basicinfo(market=ft.Market.SZ, stock_type=ft.SecurityType.ETF, code_list=[stock_code])
        logger.info(f"普通股票用ETF类型查询结果: ret={ret}, data={data}")
        
        # 测试3: 使用STOCK类型查询普通股票
        logger.info("\n=== 测试3: 使用STOCK类型查询普通股票 ===")
        ret, data = quote_ctx.get_stock_basicinfo(market=ft.Market.SZ, stock_type=ft.SecurityType.STOCK, code_list=[stock_code])
        logger.info(f"普通股票用STOCK类型查询结果: ret={ret}, data={data}")
        
        # 测试4: 不指定stock_type查询（如果支持）
        logger.info("\n=== 测试4: 不指定stock_type查询 ===")
        try:
            ret, data = quote_ctx.get_stock_basicinfo(market=ft.Market.SZ, code_list=[etf_code, stock_code])
            logger.info(f"不指定类型查询结果: ret={ret}, data={data}")
        except Exception as e:
            logger.error(f"不指定类型查询失败: {e}")
        
        # 测试5: 使用ALL类型查询
        logger.info("\n=== 测试5: 使用ALL类型查询 ===")
        if hasattr(ft.SecurityType, 'ALL'):
            ret, data = quote_ctx.get_stock_basicinfo(market=ft.Market.SZ, stock_type=ft.SecurityType.ALL, code_list=[etf_code, stock_code])
            logger.info(f"使用ALL类型查询结果: ret={ret}, data={data}")
        else:
            logger.info("富途API版本不支持SecurityType.ALL")
            
    finally:
        # 关闭连接
        quote_ctx.close()

if __name__ == "__main__":
    test_stock_type()
