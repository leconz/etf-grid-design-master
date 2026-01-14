#!/usr/bin/env python3
"""
测试get_security_name方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import logging
from services.data.futu_client import futuClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_security_name():
    """测试get_security_name方法"""
    client = futuClient()
    
    # 测试ETF代码
    etf_codes = ['510300', '159919', '159949']
    # 测试普通股票代码
    stock_codes = ['300676', '000001', '600000']
    
    logger.info("=== 测试ETF名称查询 ===")
    for code in etf_codes:
        name = client.get_security_name(code)
        logger.info(f"ETF {code}: {name}")
    
    logger.info("\n=== 测试股票名称查询 ===")
    for code in stock_codes:
        name = client.get_security_name(code)
        logger.info(f"股票 {code}: {name}")
    
    logger.info("\n=== 测试兼容旧方法get_etf_name ===")
    for code in etf_codes + stock_codes:
        name = client.get_etf_name(code)
        logger.info(f"使用旧方法查询 {code}: {name}")

if __name__ == "__main__":
    test_security_name()
