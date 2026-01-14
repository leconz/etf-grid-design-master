#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清除所有数据缓存脚本
"""

import os
import shutil

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def clear_application_cache():
    """清除应用程序缓存"""
    cache_dir = os.path.join(ROOT_DIR, "cache")
    print(f"正在清除应用程序缓存: {cache_dir}")
    
    # 获取cache目录下的所有文件和子目录
    for item in os.listdir(cache_dir):
        item_path = os.path.join(cache_dir, item)
        # 跳过.gitkeep文件
        if item == ".gitkeep":
            continue
        
        # 删除文件或目录
        if os.path.isfile(item_path):
            os.remove(item_path)
            print(f"  删除文件: {item}")
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"  删除目录: {item}")
    
    print("应用程序缓存清除完成")


def clear_test_cache():
    """清除测试缓存"""
    pytest_cache_dir = os.path.join(ROOT_DIR, ".pytest_cache")
    print(f"正在清除测试缓存: {pytest_cache_dir}")
    
    if os.path.exists(pytest_cache_dir):
        shutil.rmtree(pytest_cache_dir)
        print("  删除目录: .pytest_cache")
        print("测试缓存清除完成")
    else:
        print("  .pytest_cache目录不存在，跳过")


def verify_cleanup():
    """验证清除结果"""
    print("\n正在验证清除结果...")
    
    # 验证cache目录
    cache_dir = os.path.join(ROOT_DIR, "cache")
    cache_items = os.listdir(cache_dir)
    print(f"cache目录内容: {cache_items}")
    
    if set(cache_items) == {".gitkeep"}:
        print("✓ cache目录仅保留.gitkeep文件，清除成功")
    else:
        print("✗ cache目录清除不完整")
    
    # 验证.pytest_cache目录
    pytest_cache_dir = os.path.join(ROOT_DIR, ".pytest_cache")
    if not os.path.exists(pytest_cache_dir):
        print("✓ .pytest_cache目录已删除，清除成功")
    else:
        print("✗ .pytest_cache目录未删除")


if __name__ == "__main__":
    print("=== 开始清除所有数据缓存 ===")
    clear_application_cache()
    clear_test_cache()
    verify_cleanup()
    print("\n=== 缓存清除完成 ===")
