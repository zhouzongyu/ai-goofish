#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试闲鱼API搜索功能
"""
import sys
import os
import requests
import time
import urllib.parse
import json
import warnings

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
warnings.filterwarnings('ignore', message='SNIMissingWarning')
warnings.filterwarnings('ignore', message='InsecurePlatformWarning')

def test_api_search():
    """测试API搜索功能"""
    print("=== 测试闲鱼API搜索功能 ===\n")
    
    # 构建API URL
    base_url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"
    
    # 构建查询参数
    params = {
        "jsv": "2.7.2",
        "appKey": "34839810",
        "t": str(int(time.time() * 1000)),
        "sign": "",
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
        "propValueStr": {"searchFilter": "priceRange:100,1000;sellerType:1;"},
        "customGps": "",
        "searchReqFromPage": "pcSearch",
        "extraFilterValue": "{}",
        "userPositionJson": "{}"
    }
    
    # 设置请求头 - 参考您的curl请求
    headers = {
        "Host": "h5api.m.goofish.com",
        "Cookie": "cna=tJHHHc2NKV0CAV2zczFKcXZg; tracknick=zhouzongyu1984; t=b5dcc9cb840eba41a690577567b2b9d1; isg=BOLiW0MD_locVeIGiBp33VcrM2hEM-ZNKYWjGyx7FtUA_4N5FMD3XCt8KzsDb17l; unb=355293012; havana_lgc2_77=eyJoaWQiOjM1NTI5MzAxMiwic2ciOiI4ZGVhMjU1ZjY2Mzg1NTE5MmMyNDRlZjg2MjZjZTljNyIsInNpdGUiOjc3LCJ0b2tlbiI6IjFFdzF3U0FIbUk4eENWR3lCYUdQaVFnIn0; _hvn_lgc_=77; havana_lgc_exp=1760684166245; _samesite_flag_=true; cookie2=1744bafcf27e37618b5d6a158d9796cd; _tb_token_=f777563bba073; xlly_s=1; sgcookie=E100fEVZpvqREKpCu3PP4UeFC5b4XbSP3LrYJpXzsnwFrhkPp9j41Mgwsm5FfyhsyZs392PDJmZDAHuOXEopI50IbEOrXlwjXqKCtM6dKrgheWBXb1rez%2BaaWCPLx2lPoxd5; csg=1e66a319; sdkSilent=1758512130709; mtop_partitioned_detect=1; _m_h5_tk=bc254c6eedc662b3a052ccf13e0d386a_1758445758129; _m_h5_tk_enc=b2840d3c78ceec2bf47e5eca008b0f34; _m_h5_tk=0609c1033cc3b673fcd82adbfe1d3ec3_1758445184107; _m_h5_tk_enc=c31de03929909208a8ce6b23ac62e8bf; x5sec=7b22733b32223a2233303364393433666235623037316365222c22617365727665723b33223a22307c43505378767359474549712b325a59444767737a4e5455794f544d774d5449374d53494859323975626d566a6444432b317679422f2f2f2f2f2f3842227d; tfstk=g1vtHmYtY20MM_zaXEcnnjUHbYi3BXxwsF-7nZbgGeLpV3zGGdXMkSLM0Efj7OvvJnT-bi0wnlRer3wMIfW0HOWVh40oEYqwbtWXynUBHPPC2GHcfN_fQ9NWShH-EYxwfljsqHMknUlD1ibfh11fAM_FVSZ6l1aQRwSVcPsbCDKC8ws_ft1_OMsN0iwXltipAwSfhGTf1DKC8i6flb9gXZq1k-d1z7Tm1rV_w7pdX1QYnN2AYLelMaihR-eA8MCTsh_Lh-9ptIdy7NGzxZWG7HI9uYyNCsdXI99sRx6WaepANThmb1tv9EWMdmN1PCYGddO8c-tdBZTkd6atJa9wALWCtYiJAp8MbpK0cxsHrwtwCtHS4OB159Ien2y1kBOXI1W45qQ2pH96Mgo2EL387zbRm5iKvSPV1MPd8-90hbFGHMQoxWV4g6jFvamKvSPV1MSdrDDugS5hY",
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
            verify=False  # 禁用SSL验证
        )
        
        print("   状态码: {}".format(response.status_code))
        
        if response.status_code == 200:
            result = response.json()
            print("   响应状态: {}".format(result.get('ret', '未知')))
            print("   数据字段: {}".format(list(result.get('data', {}).keys())))
            
            if 'data' in result and 'resultList' in result['data']:
                items = result['data']['resultList']
                print("   商品数量: {}".format(len(items)))
                if items:
                    first_item = items[0].get('data', {}).get('item', {}).get('main', {}).get('exContent', {})
                    print("   第一个商品标题: {}".format(first_item.get('title', '无标题')))
            else:
                print("   未获取到商品数据")
        else:
            print("   API请求失败: {}".format(response.status_code))
            print("   响应内容: {}...".format(response.text[:200]))
            
    except Exception as e:
        print("   请求异常: {}".format(e))
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_api_search()
