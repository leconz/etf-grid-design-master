#!/usr/bin/env python3
"""
测试300676解决方案
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import logging
from services.data.futu_client import futuClient
from services.analysis.etf_analysis_service import ETFAnalysisService

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_300676_solution():
    """测试300676解决方案"""
    logger.info("=== 测试300676解决方案 ===")
    
    # 初始化客户端
    client = futuClient()
    service = ETFAnalysisService()
    
    test_code = '300676'
    
    logger.info("\n1. 测试代码补全")
    full_code = client._complete_etf_code(test_code)
    logger.info(f"代码补全结果: {test_code} -> {full_code}")
    
    logger.info("\n2. 测试获取证券名称")
    name = client.get_security_name(test_code)
    logger.info(f"证券名称: {name}")
    
    logger.info("\n3. 测试获取证券基本信息")
    basic_info = client.get_security_basic_info(test_code)
    logger.info(f"证券基本信息: {basic_info}")
    
    logger.info("\n4. 测试兼容旧方法get_etf_basic_info")
    etf_basic_info = client.get_etf_basic_info(test_code)
    logger.info(f"使用旧方法获取基本信息: {etf_basic_info}")
    
    logger.info("\n5. 测试获取最新价格")
    price = client.get_latest_price(test_code)
    logger.info(f"最新价格: {price}")
    
    logger.info("\n6. 测试ETFAnalysisService.get_etf_basic_info")
    try:
        etf_info = service.get_etf_basic_info(test_code)
        logger.info(f"服务层获取ETF信息成功: {etf_info}")
    except Exception as e:
        logger.error(f"服务层获取ETF信息失败: {e}")
    
    logger.info("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_300676_solution()
