#!/usr/bin/env python3
"""
测试300676代码是否为ETF
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import logging
from services.data.futu_client import futuClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_300676():
    """测试300676代码"""
    client = futuClient()
    
    # 测试代码补全
    full_code = client._complete_etf_code('300676')
    logger.info(f"补全后的代码: {full_code}")
    
    # 测试获取基本信息
    basic_info = client.get_etf_basic_info('300676')
    logger.info(f"基本信息: {basic_info}")
    
    # 测试获取名称
    name = client.get_etf_name('300676')
    logger.info(f"ETF名称: {name}")
    
    # 测试获取最新价格
    price = client.get_latest_price('300676')
    logger.info(f"最新价格: {price}")

if __name__ == "__main__":
    test_300676()
