#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试scraper.py中的API搜索函数
"""
import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import search_xianyu_api

async def test_scraper_api():
    """测试scraper.py中的API搜索函数"""
    print("=== 测试scraper.py中的API搜索函数 ===\n")
    
    try:
        result = await search_xianyu_api(
            keyword="按键精灵写脚本",
            min_price="100",
            max_price="1000",
            personal_only=True
        )
        
        print(f"API响应状态: {result.get('ret', '未知')}")
        print(f"数据字段: {list(result.get('data', {}).keys())}")
        
        if 'data' in result and 'resultList' in result['data']:
            items = result['data']['resultList']
            print(f"✅ 商品数量: {len(items)}")
            if items:
                first_item = items[0].get('data', {}).get('item', {}).get('main', {}).get('exContent', {})
                print(f"第一个商品标题: {first_item.get('title', '无标题')}")
        else:
            print("⚠️ 未获取到商品数据")
            print(f"完整响应: {result}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_scraper_api())
