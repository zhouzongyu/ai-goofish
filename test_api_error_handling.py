#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试闲鱼API错误处理机制
"""
import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parsers import _parse_search_results_json

async def test_api_error_handling():
    """测试API错误处理"""
    print("=== 测试闲鱼API错误处理机制 ===\n")
    
    # 测试用例1: "被挤爆啦"错误
    print("1. 测试'被挤爆啦'错误处理:")
    error_data_1 = {
        "ret": ["RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!"],
        "data": {
            "url": "https://passport.goofish.com/mini_login.htm",
            "h5url": "https://passport.goofish.com/mini_login.htm"
        }
    }
    
    result_1 = await _parse_search_results_json(error_data_1, "测试源1")
    print(f"   结果: {len(result_1)} 个商品 (应该为0)")
    print()
    
    # 测试用例2: 反爬虫验证错误
    print("2. 测试反爬虫验证错误处理:")
    error_data_2 = {
        "ret": ["FAIL_SYS_USER_VALIDATE::SM::用户验证失败"],
        "data": {}
    }
    
    result_2 = await _parse_search_results_json(error_data_2, "测试源2")
    print(f"   结果: {len(result_2)} 个商品 (应该为0)")
    print()
    
    # 测试用例3: 正常数据
    print("3. 测试正常数据处理:")
    normal_data = {
        "ret": ["SUCCESS::调用成功"],
        "data": {
            "resultList": [
                {
                    "data": {
                        "item": {
                            "main": {
                                "exContent": {
                                    "title": "测试商品",
                                    "price": [{"text": "¥100"}],
                                    "area": "北京",
                                    "userNickName": "测试卖家",
                                    "itemId": "123456"
                                },
                                "clickParam": {
                                    "args": {
                                        "publishTime": "1640995200000",
                                        "wantNum": "5"
                                    }
                                }
                            },
                            "targetUrl": "https://www.goofish.com/item/123456"
                        }
                    }
                }
            ]
        }
    }
    
    result_3 = await _parse_search_results_json(normal_data, "测试源3")
    print(f"   结果: {len(result_3)} 个商品 (应该为1)")
    if result_3:
        print(f"   商品标题: {result_3[0]['商品标题']}")
    print()
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_api_error_handling())
