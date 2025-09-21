#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新闲鱼API请求的Cookie和签名参数
"""
import json
import time
import urllib.parse
import requests
import warnings

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
warnings.filterwarnings('ignore', message='SNIMissingWarning')
warnings.filterwarnings('ignore', message='InsecurePlatformWarning')

def get_fresh_cookies():
    """从闲鱼网站获取最新的Cookie"""
    print("正在获取闲鱼网站Cookie...")
    
    try:
        # 访问闲鱼首页获取Cookie
        session = requests.Session()
        session.verify = False
        
        response = session.get("https://www.goofish.com/", timeout=30)
        
        if response.status_code == 200:
            print("✅ 成功获取Cookie")
            return session.cookies.get_dict()
        else:
            print(f"❌ 获取Cookie失败，状态码: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"❌ 获取Cookie异常: {e}")
        return {}

def test_api_with_cookies():
    """使用获取的Cookie测试API"""
    print("=== 测试闲鱼API搜索功能 ===\n")
    
    # 获取Cookie
    cookies = get_fresh_cookies()
    print(f"获取到的Cookie: {cookies}")
    
    if not cookies:
        print("无法获取Cookie，使用默认参数")
        # 使用您之前提供的Cookie
        cookies = {
            "cna": "tJHHHc2NKV0CAV2zczFKcXZg",
            "tracknick": "zhouzongyu1984",
            "t": "b5dcc9cb840eba41a690577567b2b9d1"
        }
    
    # 构建API URL
    base_url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"
    
    # 构建查询参数
    params = {
        "jsv": "2.7.2",
        "appKey": "34839810",
        "t": str(int(time.time() * 1000)),
        "sign": "",  # 暂时留空
        "v": "1.0",
        "type": "originaljson",
        "accountSite": "xianyu",
        "dataType": "json",
        "timeout": "20000",
        "api": "mtop.taobao.idlemtopsearch.pc.search",
        "sessionOption": "AutoLoginOnly",
        "spm_cnt": "a21ybx.search.0.0",
        "spm_pre": "a21ybx.search.searchInput.0"
    }
    
    # 构建请求体
    request_body = {
        "pageNumber": 1,
        "keyword": "按键精灵写脚本",
        "fromFilter": True,
        "rowsPerPage": 30,
        "sortValue": "",
        "sortField": "",
        "customDistance": "",
        "gps": "",
        "propValueStr": {"searchFilter": "priceRange:100,1000;"},
        "customGps": "",
        "searchReqFromPage": "pcSearch",
        "extraFilterValue": "{}",
        "userPositionJson": "{}"
    }
    
    # 设置请求头
    headers = {
        "Host": "h5api.m.goofish.com",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "accept": "application/json",
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua-mobile": "?0",
        "origin": "https://www.goofish.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.goofish.com/",
        "accept-language": "zh-CN,zh;q=0.9",
        "priority": "u=1, i"
    }
    
    # 将Cookie添加到请求头
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    headers["Cookie"] = cookie_str
    
    try:
        print("1. 发送API请求...")
        # 将请求体编码为URL格式
        data = urllib.parse.urlencode({"data": json.dumps(request_body, ensure_ascii=False)})
        
        response = requests.post(
            base_url,
            params=params,
            data=data,
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   响应状态: {result.get('ret', '未知')}")
            print(f"   数据字段: {list(result.get('data', {}).keys())}")
            
            if 'data' in result and 'resultList' in result['data']:
                items = result['data']['resultList']
                print(f"   商品数量: {len(items)}")
                if items:
                    first_item = items[0].get('data', {}).get('item', {}).get('main', {}).get('exContent', {})
                    print(f"   第一个商品标题: {first_item.get('title', '无标题')}")
            else:
                print("   未获取到商品数据")
                print(f"   完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"   API请求失败: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   请求异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_api_with_cookies()
