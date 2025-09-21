import asyncio
import json
import os
import random
import time
from datetime import datetime
from urllib.parse import urlencode
import requests

from playwright.async_api import (
    Response,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from src.ai_handler import (
    download_all_images,
    get_ai_analysis,
    send_ntfy_notification,
    cleanup_task_images,
)
from src.config import (
    AI_DEBUG_MODE,
    API_URL_PATTERN,
    DETAIL_API_URL_PATTERN,
    LOGIN_IS_EDGE,
    RUN_HEADLESS,
    RUNNING_IN_DOCKER,
    STATE_FILE,
)
from src.parsers import (
    _parse_search_results_json,
    _parse_user_items_data,
    calculate_reputation_from_ratings,
    parse_ratings_data,
    parse_user_head_data,
)
from src.utils import (
    format_registration_days,
    get_link_unique_key,
    random_sleep,
    safe_get,
    save_to_jsonl,
)
from src.anti_crawler_config import (
    get_all_detection_selectors,
    get_retry_delay,
    should_retry,
    STEALTH_CONFIG,
    SUSPICIOUS_INDICATORS,
    JS_ERROR_KEYWORDS,
    MANUAL_INTERVENTION,
)
from src.simple_captcha_solver import simple_captcha_solver


async def search_xianyu_api(keyword, min_price=None, max_price=None, 
                           personal_only=False, page_number=1, 
                           rows_per_page=30):
    """
    直接调用闲鱼搜索API获取商品数据
    
    Args:
        keyword: 搜索关键词
        min_price: 最低价格
        max_price: 最高价格
        personal_only: 是否只搜索个人卖家
        page_number: 页码
        rows_per_page: 每页商品数量
    
    Returns:
        API响应数据
    """
    import urllib.parse
    
    # 从xianyu_state.json读取Cookie和认证信息
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        # 提取Cookie信息
        cookies = state_data.get('cookies', [])
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        
        # 构建Cookie字符串
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        print(f"LOG: 从 {STATE_FILE} 加载了 {len(cookie_dict)} 个Cookie")
        
        # 提取认证令牌
        m_h5_tk = cookie_dict.get('_m_h5_tk', '')
        m_h5_tk_enc = cookie_dict.get('_m_h5_tk_enc', '')
        tb_token = cookie_dict.get('_tb_token_', '')
        
        print(f"LOG: 认证令牌 - _m_h5_tk: {m_h5_tk[:20]}..., _tb_token_: {tb_token[:20]}...")
        
    except Exception as e:
        print(f"LOG: 读取Cookie失败: {e}")
        cookie_str = ""
        m_h5_tk = ""
        m_h5_tk_enc = ""
        tb_token = ""
    
    # 构建API URL
    base_url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"
    
    # 构建请求体
    request_body = {
        "pageNumber": page_number,
        "keyword": keyword,
        "fromFilter": True,
        "rowsPerPage": rows_per_page,
        "sortValue": "",
        "sortField": "",
        "customDistance": "",
        "gps": "",
        "propValueStr": {},
        "customGps": "",
        "searchReqFromPage": "pcSearch",
        "extraFilterValue": "{}",
        "userPositionJson": "{}"
    }
    
    # 添加价格筛选
    if min_price or max_price:
        price_range = ""
        if min_price:
            price_range += f"{min_price},"
        else:
            price_range += ","
        if max_price:
            price_range += f"{max_price};"
        else:
            price_range += ";"
        request_body["propValueStr"]["searchFilter"] = f"priceRange:{price_range}"
    
    # 添加个人卖家筛选
    if personal_only:
        if "searchFilter" not in request_body["propValueStr"]:
            request_body["propValueStr"]["searchFilter"] = ""
        request_body["propValueStr"]["searchFilter"] += "sellerType:1;"
    
    # 生成时间戳和签名
    timestamp = str(int(time.time() * 1000))
    
    # 尝试生成简单的签名（基于令牌和时间戳）
    import hashlib
    if m_h5_tk and '_' in m_h5_tk:
        # 提取令牌的前半部分
        token_part = m_h5_tk.split('_')[0]
        # 简单的签名生成（实际算法可能更复杂）
        sign_data = f"{token_part}&{timestamp}&34839810&{json.dumps(request_body, ensure_ascii=False, separators=(',', ':'))}"
        sign = hashlib.md5(sign_data.encode('utf-8')).hexdigest()
        print(f"LOG: 生成签名: {sign[:20]}...")
    else:
        sign = ""
        print("LOG: 无法生成签名，缺少_m_h5_tk令牌")
    
    # 构建查询参数
    params = {
        "jsv": "2.7.2",
        "appKey": "34839810",
        "t": timestamp,
        "sign": sign,
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
    
    # 设置请求头 - 使用从文件读取的Cookie
    headers = {
        "Host": "h5api.m.goofish.com",
        "Cookie": cookie_str,
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
    
    # 将请求体编码为URL格式
    data = urllib.parse.urlencode({"data": json.dumps(request_body, ensure_ascii=False)})
    
    try:
        # 禁用SSL验证以解决证书问题
        response = requests.post(
            base_url,
            params=params,
            data=data,
            headers=headers,
            timeout=30,
            verify=False  # 禁用SSL验证
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return {"ret": [f"HTTP_ERROR::{response.status_code}"], "data": {}}
            
    except Exception as e:
        print(f"API请求异常: {e}")
        return {"ret": [f"REQUEST_ERROR::{str(e)}"], "data": {}}


async def check_anti_crawler_measures(page, keyword: str) -> bool:
    """
    增强的反爬虫检测机制
    检测多种类型的反爬虫验证弹窗和异常情况
    """
    print("   [反爬检测] 开始检测反爬虫验证弹窗...")
    
    # 使用配置文件中的检测选择器
    detection_selectors = get_all_detection_selectors()
    
    detected_elements = []
    
    # 检测各种反爬虫元素
    for selector in detection_selectors:
        try:
            element = page.locator(selector)
            if await element.count() > 0:
                # 检查元素是否可见
                if await element.first.is_visible():
                    detected_elements.append(selector)
                    print(f"   [反爬检测] 检测到可疑元素: {selector}")
        except Exception as e:
            # 忽略选择器错误，继续检测其他元素
            continue
    
    # 检测页面标题和URL中的异常
    try:
        page_title = await page.title()
        current_url = page.url
        
        suspicious_indicators = SUSPICIOUS_INDICATORS
        
        for indicator in suspicious_indicators:
            if indicator in page_title.lower() or indicator in current_url.lower():
                detected_elements.append(f"页面异常: {indicator}")
                print(f"   [反爬检测] 页面异常检测: {indicator}")
    except Exception as e:
        print(f"   [反爬检测] 页面信息检测失败: {e}")
    
    # 检测JavaScript错误和异常
    try:
        # 检查是否有验证相关的JavaScript错误
        js_errors = await page.evaluate("""
            () => {
                const errors = [];
                // 检查控制台错误
                if (window.console && window.console.error) {
                    const originalError = window.console.error;
                    window.console.error = function(...args) {
                        errors.push(args.join(' '));
                        originalError.apply(console, args);
                    };
                }
                return errors;
            }
        """)
        
        if js_errors:
            for error in js_errors:
                if any(keyword in error.lower() for keyword in JS_ERROR_KEYWORDS):
                    detected_elements.append(f"JS错误: {error}")
                    print(f"   [反爬检测] JavaScript异常: {error}")
    except Exception as e:
        print(f"   [反爬检测] JavaScript检测失败: {e}")
    
    # 如果检测到反爬虫元素，执行处理逻辑
    if detected_elements:
        print("\n==================== 反爬虫检测触发 ====================")
        print(f"检测到 {len(detected_elements)} 个反爬虫验证元素:")
        for element in detected_elements:
            print(f"  - {element}")
        print("\n可能的原因:")
        print("1. 操作频率过高，被识别为机器人")
        print("2. IP地址被标记为可疑")
        print("3. 浏览器指纹被识别")
        print("4. 登录状态异常或过期")
        print("\n建议解决方案:")
        print("1. 立即停止脚本，等待 30-60 分钟")
        print("2. 设置 RUN_HEADLESS=false 以手动处理验证")
        print("3. 更换IP地址或使用代理")
        print("4. 重新登录获取新的认证状态")
        print("5. 降低爬取频率，增加随机延迟")
        
        # 检查是否启用了手动干预模式
        if not RUN_HEADLESS:
            print("\n检测到非无头模式，尝试自动解答验证码...")
            
            # 首先尝试自动解答验证码
            auto_solve_result = await simple_captcha_solver.solve_captcha(page)
            if auto_solve_result:
                print("✅ 验证码自动解答成功，继续执行任务...")
                return False
            else:
                print("⚠️ 自动解答失败，尝试手动干预...")
                manual_intervention_result = await handle_manual_intervention(page, detected_elements)
                if manual_intervention_result:
                    print("✅ 手动干预成功，继续执行任务...")
                    return False
                else:
                    print("❌ 手动干预失败或用户选择退出。")
        else:
            print("\n检测到无头模式，尝试自动解答验证码...")
            auto_solve_result = await simple_captcha_solver.solve_captcha(page)
            if auto_solve_result:
                print("✅ 验证码自动解答成功，继续执行任务...")
                return False
            else:
                print("❌ 自动解答失败，无头模式下无法手动干预。")
        
        print(f"\n任务 '{keyword}' 将在此处中止。")
        print("========================================================")
        return True
    
    print("   [反爬检测] 未检测到反爬虫验证弹窗，继续执行...")
    return False


async def handle_manual_intervention(page, detected_elements: list) -> bool:
    """
    处理手动干预，允许用户在非无头模式下手动完成验证
    """
    print("\n--- 手动干预模式 ---")
    print("检测到反爬虫验证弹窗，请在浏览器中手动完成验证。")
    print("完成验证后，程序将自动继续执行。")
    print("\n操作说明:")
    print("1. 在浏览器窗口中完成所有验证步骤")
    print("2. 等待页面恢复正常状态")
    print("3. 程序将在30秒后自动检测验证是否完成")
    print("4. 如果验证失败，程序将退出")
    
    # 使用配置文件中的手动干预设置
    max_wait_time = MANUAL_INTERVENTION["max_wait_time"]
    check_interval = MANUAL_INTERVENTION["check_interval"]
    stabilization_delay = MANUAL_INTERVENTION["stabilization_delay"]
    elapsed_time = 0
    
    while elapsed_time < max_wait_time:
        print(f"\n等待验证完成... ({elapsed_time}/{max_wait_time}秒)")
        
        # 重新检测反爬虫元素
        current_detected = []
        for selector in [
            "div.baxia-dialog-mask",
            "div.J_MIDDLEWARE_FRAME_WIDGET", 
            "div[class*='baxia-dialog']",
            "div[class*='verify-dialog']",
            "div[class*='captcha-dialog']",
            "text=异常流量",
            "text=请完成验证",
            "text=安全验证",
        ]:
            try:
                element = page.locator(selector)
                if await element.count() > 0 and await element.first.is_visible():
                    current_detected.append(selector)
            except:
                continue
        
        # 如果检测不到反爬虫元素，说明验证可能已完成
        if not current_detected:
            print("✅ 验证元素已消失，验证可能已完成。")
            
            # 额外等待几秒确保页面稳定
            await asyncio.sleep(stabilization_delay)
            
            # 再次确认页面状态
            try:
                # 检查页面是否可以正常访问
                await page.wait_for_selector('text=新发布', timeout=10)
                print("✅ 页面恢复正常，验证成功！")
                return True
            except:
                print("⚠️ 页面状态异常，继续等待...")
        
        await asyncio.sleep(check_interval)
        elapsed_time += check_interval
    
    print("❌ 等待超时，验证可能未完成或失败。")
    return False


async def scrape_user_profile(context, user_id: str) -> dict:
    """
    【新版】访问指定用户的个人主页，按顺序采集其摘要信息、完整的商品列表和完整的评价列表。
    """
    print(f"   -> 开始采集用户ID: {user_id} 的完整信息...")
    profile_data = {}
    page = await context.new_page()

    # 为各项异步任务准备Future和数据容器
    head_api_future = asyncio.get_event_loop().create_future()

    all_items, all_ratings = [], []
    stop_item_scrolling, stop_rating_scrolling = asyncio.Event(), asyncio.Event()

    async def handle_response(response: Response):
        # 捕获头部摘要API
        if "mtop.idle.web.user.page.head" in response.url and not head_api_future.done():
            try:
                head_api_future.set_result(await response.json())
                print(f"      [API捕获] 用户头部信息... 成功")
            except Exception as e:
                if not head_api_future.done(): head_api_future.set_exception(e)

        # 捕获商品列表API
        elif "mtop.idle.web.xyh.item.list" in response.url:
            try:
                data = await response.json()
                all_items.extend(data.get('data', {}).get('cardList', []))
                print(f"      [API捕获] 商品列表... 当前已捕获 {len(all_items)} 件")
                if not data.get('data', {}).get('nextPage', True):
                    stop_item_scrolling.set()
            except Exception as e:
                stop_item_scrolling.set()

        # 捕获评价列表API
        elif "mtop.idle.web.trade.rate.list" in response.url:
            try:
                data = await response.json()
                all_ratings.extend(data.get('data', {}).get('cardList', []))
                print(f"      [API捕获] 评价列表... 当前已捕获 {len(all_ratings)} 条")
                if not data.get('data', {}).get('nextPage', True):
                    stop_rating_scrolling.set()
            except Exception as e:
                stop_rating_scrolling.set()

    page.on("response", handle_response)

    try:
        # --- 任务1: 导航并采集头部信息 ---
        await page.goto(f"https://www.goofish.com/personal?userId={user_id}", wait_until="domcontentloaded", timeout=20000)
        head_data = await asyncio.wait_for(head_api_future, timeout=15)
        profile_data = await parse_user_head_data(head_data)

        # --- 任务2: 滚动加载所有商品 (默认页面) ---
        print("      [采集阶段] 开始采集该用户的商品列表...")
        await random_sleep(2, 4) # 等待第一页商品API完成
        while not stop_item_scrolling.is_set():
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            try:
                await asyncio.wait_for(stop_item_scrolling.wait(), timeout=8)
            except asyncio.TimeoutError:
                print("      [滚动超时] 商品列表可能已加载完毕。")
                break
        profile_data["卖家发布的商品列表"] = await _parse_user_items_data(all_items)

        # --- 任务3: 点击并采集所有评价 ---
        print("      [采集阶段] 开始采集该用户的评价列表...")
        rating_tab_locator = page.locator("//div[text()='信用及评价']/ancestor::li")
        if await rating_tab_locator.count() > 0:
            await rating_tab_locator.click()
            await random_sleep(3, 5) # 等待第一页评价API完成

            while not stop_rating_scrolling.is_set():
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                try:
                    await asyncio.wait_for(stop_rating_scrolling.wait(), timeout=8)
                except asyncio.TimeoutError:
                    print("      [滚动超时] 评价列表可能已加载完毕。")
                    break

            profile_data['卖家收到的评价列表'] = await parse_ratings_data(all_ratings)
            reputation_stats = await calculate_reputation_from_ratings(all_ratings)
            profile_data.update(reputation_stats)
        else:
            print("      [警告] 未找到评价选项卡，跳过评价采集。")

    except Exception as e:
        print(f"   [错误] 采集用户 {user_id} 信息时发生错误: {e}")
    finally:
        page.remove_listener("response", handle_response)
        await page.close()
        print(f"   -> 用户 {user_id} 信息采集完成。")

    return profile_data


async def scrape_xianyu(task_config: dict, debug_limit: int = 0, retry_count: int = 0):
    """
    【核心执行器】
    根据单个任务配置，异步爬取闲鱼商品数据，并对每个新发现的商品进行实时的、独立的AI分析和通知。
    
    Args:
        task_config: 任务配置
        debug_limit: 调试限制
        retry_count: 重试次数（用于反爬虫检测后的智能重试）
    """
    keyword = task_config['keyword']
    max_pages = task_config.get('max_pages', 1)
    personal_only = task_config.get('personal_only', False)
    min_price = task_config.get('min_price')
    max_price = task_config.get('max_price')
    ai_prompt_text = task_config.get('ai_prompt_text', '')

    processed_item_count = 0
    stop_scraping = False

    processed_links = set()
    output_filename = os.path.join("jsonl", f"{keyword.replace(' ', '_')}_full_data.jsonl")
    if os.path.exists(output_filename):
        print(f"LOG: 发现已存在文件 {output_filename}，正在加载历史记录以去重...")
        try:
            with open(output_filename, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        link = record.get('商品信息', {}).get('商品链接', '')
                        if link:
                            processed_links.add(get_link_unique_key(link))
                    except json.JSONDecodeError:
                        print(f"   [警告] 文件中有一行无法解析为JSON，已跳过。")
            print(f"LOG: 加载完成，已记录 {len(processed_links)} 个已处理过的商品。")
        except IOError as e:
            print(f"   [警告] 读取历史文件时发生错误: {e}")
    else:
        print(f"LOG: 输出文件 {output_filename} 不存在，将创建新文件。")

    async with async_playwright() as p:
        if LOGIN_IS_EDGE:
            browser = await p.chromium.launch(headless=RUN_HEADLESS, channel="msedge")
        else:
            # Docker环境内，使用Playwright自带的chromium；本地环境，使用系统安装的Chrome
            if RUNNING_IN_DOCKER:
                browser = await p.chromium.launch(headless=RUN_HEADLESS)
            else:
                browser = await p.chromium.launch(headless=RUN_HEADLESS, channel="chrome")
        # 使用配置文件中的隐身模式设置
        context = await browser.new_context(
            storage_state=STATE_FILE,
            **STEALTH_CONFIG
        )
        page = await context.new_page()

        try:
            print("LOG: 步骤 1 - 直接调用闲鱼搜索API...")
            print(f"   -> 搜索关键词: {keyword}")
            print(f"   -> 价格范围: {min_price or '无限制'} - {max_price or '无限制'}")
            print(f"   -> 个人卖家: {'是' if personal_only else '否'}")

            # 直接调用搜索API
            search_result = await search_xianyu_api(
                keyword=keyword,
                min_price=min_price,
                max_price=max_price,
                personal_only=personal_only,
                page_number=1,
                rows_per_page=30
            )
            
            print(f"LOG: API调用完成，响应状态: {search_result.get('ret', '未知')}")

            # 检查API响应是否有错误
            ret_field = await safe_get(search_result, "ret", default=[])
            if isinstance(ret_field, list) and ret_field:
                ret_string = str(ret_field)
                if "被挤爆啦" in ret_string or "RGV587_ERROR" in ret_string:
                    print(f"\n==================== API限流检测 ====================")
                    print(f"检测到闲鱼API限流错误: {ret_string}")
                    print("建议解决方案:")
                    print("1. 等待30-60分钟后重试")
                    print("2. 降低爬取频率，增加随机延迟")
                    print("3. 检查是否有其他程序同时在访问闲鱼")
                    print("4. 考虑使用代理IP轮换")
                    print("========================================================")
                    await browser.close()
                    return 0
                elif "FAIL_SYS_USER_VALIDATE" in ret_string:
                    print(f"\n==================== 反爬虫验证检测 ====================")
                    print(f"检测到闲鱼反爬虫验证: {ret_string}")
                    print("建议解决方案:")
                    print("1. 重新登录获取新的认证状态")
                    print("2. 设置 RUN_HEADLESS=false 手动处理验证")
                    print("3. 等待更长时间后重试")
                    print("========================================================")
                    await browser.close()
                    return 0
                elif "HTTP_ERROR" in ret_string or "REQUEST_ERROR" in ret_string:
                    print(f"\n==================== API请求错误 ====================")
                    print(f"API请求失败: {ret_string}")
                    print("建议解决方案:")
                    print("1. 检查网络连接")
                    print("2. 检查API接口是否正常")
                    print("3. 稍后重试")
                    print("========================================================")
                    await browser.close()
                    return 0

            # 解析搜索结果
            search_items = await _parse_search_results_json(search_result, "API搜索")
            if not search_items:
                print("LOG: 未获取到任何商品数据，任务结束。")
                await browser.close()
                return 0
            
            print(f"LOG: 成功获取到 {len(search_items)} 个商品")

            # 由于使用API直接获取数据，跳过页面操作和反爬虫检测
            print("LOG: 步骤 2 - 开始处理商品数据...")
            
            # 应用调试限制
            if debug_limit > 0:
                search_items = search_items[:debug_limit]
                print(f"LOG: 调试模式：限制处理前 {debug_limit} 个商品")
            
            all_items = search_items
            print(f"LOG: 总共获取到 {len(all_items)} 个商品")

            # 处理所有商品
            for i, item_data in enumerate(all_items, 1):
                if debug_limit > 0 and processed_item_count >= debug_limit:
                    print(f"LOG: 已达到调试上限 ({debug_limit})，停止处理商品。")
                    stop_scraping = True
                    break

                    unique_key = get_link_unique_key(item_data["商品链接"])
                    if unique_key in processed_links:
                        print(f"   -> [页内进度 {i}/{total_items_on_page}] 商品 '{item_data['商品标题'][:20]}...' 已存在，跳过。")
                        continue

                    print(f"-> [页内进度 {i}/{total_items_on_page}] 发现新商品，获取详情: {item_data['商品标题'][:30]}...")
                    # --- 修改: 访问详情页前的等待时间，模拟用户在列表页上看了一会儿 ---
                    await random_sleep(3, 6) # 原来是 (2, 4)

                    detail_page = await context.new_page()
                    try:
                        async with detail_page.expect_response(lambda r: DETAIL_API_URL_PATTERN in r.url, timeout=25000) as detail_info:
                            await detail_page.goto(item_data["商品链接"], wait_until="domcontentloaded", timeout=25000)

                        detail_response = await detail_info.value
                        if detail_response.ok:
                            detail_json = await detail_response.json()

                            ret_string = str(await safe_get(detail_json, 'ret', default=[]))
                            if "FAIL_SYS_USER_VALIDATE" in ret_string:
                                print("\n==================== CRITICAL BLOCK DETECTED ====================")
                                print("检测到闲鱼反爬虫验证 (FAIL_SYS_USER_VALIDATE)，程序将终止。")
                                long_sleep_duration = random.randint(300, 600)
                                print(f"为避免账户风险，将执行一次长时间休眠 ({long_sleep_duration} 秒) 后再退出...")
                                await asyncio.sleep(long_sleep_duration)
                                print("长时间休眠结束，现在将安全退出。")
                                print("===================================================================")
                                stop_scraping = True
                                break

                            # 解析商品详情数据并更新 item_data
                            item_do = await safe_get(detail_json, 'data', 'itemDO', default={})
                            seller_do = await safe_get(detail_json, 'data', 'sellerDO', default={})

                            reg_days_raw = await safe_get(seller_do, 'userRegDay', default=0)
                            registration_duration_text = format_registration_days(reg_days_raw)

                            # --- START: 新增代码块 ---

                            # 1. 提取卖家的芝麻信用信息
                            # zhima_credit_text = await safe_get(seller_do, 'zhimaLevelInfo', 'levelName')

                            # 2. 提取该商品的完整图片列表
                            # image_infos = await safe_get(item_do, 'imageInfos', default=[])
                            # if image_infos:
                            #     # 使用列表推导式获取所有有效的图片URL
                            #     all_image_urls = [img.get('url') for img in image_infos if img.get('url')]
                            #     if all_image_urls:
                            #         item_data['商品图片列表'] = all_image_urls
                            #         # (可选) 仍然保留主图链接，以防万一
                            #         item_data['商品主图链接'] = all_image_urls[0]

                            # --- END: 新增代码块 ---
                            # item_data['“想要”人数'] = await safe_get(item_do, 'wantCnt', default=item_data.get('“想要”人数', 'NaN'))
                            # item_data['浏览量'] = await safe_get(item_do, 'browseCnt', default='-')
                            # ...[此处可添加更多从详情页解析出的商品信息]...

                            # 调用核心函数采集卖家信息
                            user_profile_data = {}
                            # user_id = await safe_get(seller_do, 'sellerId')
                            # if user_id:
                            #     # 新的、高效的调用方式:
                            #     user_profile_data = await scrape_user_profile(context, str(user_id))
                            # else:
                            #     print("   [警告] 未能从详情API中获取到卖家ID。")
                            # user_profile_data['卖家芝麻信用'] = zhima_credit_text
                            # user_profile_data['卖家注册时长'] = registration_duration_text

                            # 构建基础记录
                            final_record = {
                                "爬取时间": datetime.now().isoformat(),
                                "搜索关键字": keyword,
                                "任务名称": task_config.get('task_name', 'Untitled Task'),
                                "商品信息": item_data,
                                "卖家信息": user_profile_data
                            }

                            # --- START: Real-time AI Analysis & Notification ---
                            from src.config import SKIP_AI_ANALYSIS
                            
                            # 检查是否跳过AI分析并直接发送通知
                            if SKIP_AI_ANALYSIS:
                                print(f"   -> 环境变量 SKIP_AI_ANALYSIS 已设置，跳过AI分析并直接发送通知...")
                                # 下载图片 (暂时删除删除图片)
                              
                                # image_urls = item_data.get('商品图片列表', [])
                                # downloaded_image_paths = await download_all_images(item_data['商品ID'], image_urls, task_config.get('task_name', 'default'))
                                
                                # 删除下载的图片文件，节省空间
                                # for img_path in downloaded_image_paths:
                                #     try:
                                #         if os.path.exists(img_path):
                                #             os.remove(img_path)
                                #             print(f"   [图片] 已删除临时图片文件: {img_path}")
                                #     except Exception as e:
                                #         print(f"   [图片] 删除图片文件时出错: {e}")
                                
                                # 直接发送通知，将所有商品标记为推荐
                                print(f"   -> 商品已跳过AI分析，准备发送通知...")
                                await send_ntfy_notification(item_data, "商品已跳过AI分析，直接通知")
                            else:
                                print(f"   -> 开始对商品 #{item_data['商品ID']} 进行实时AI分析...")
                                # 1. Download images
                                image_urls = item_data.get('商品图片列表', [])
                                downloaded_image_paths = await download_all_images(item_data['商品ID'], image_urls, task_config.get('task_name', 'default'))

                                # 2. Get AI analysis
                                ai_analysis_result = None
                                if ai_prompt_text:
                                    try:
                                        # 注意：这里我们将整个记录传给AI，让它拥有最全的上下文
                                        ai_analysis_result = await get_ai_analysis(final_record, downloaded_image_paths, prompt_text=ai_prompt_text)
                                        if ai_analysis_result:
                                            final_record['ai_analysis'] = ai_analysis_result
                                            print(f"   -> AI分析完成。推荐状态: {ai_analysis_result.get('is_recommended')}")
                                        else:
                                            final_record['ai_analysis'] = {'error': 'AI analysis returned None after retries.'}
                                    except Exception as e:
                                        print(f"   -> AI分析过程中发生严重错误: {e}")
                                        final_record['ai_analysis'] = {'error': str(e)}
                                else:
                                    print("   -> 任务未配置AI prompt，跳过分析。")

                                # 删除下载的图片文件，节省空间
                                for img_path in downloaded_image_paths:
                                    try:
                                        if os.path.exists(img_path):
                                            os.remove(img_path)
                                            print(f"   [图片] 已删除临时图片文件: {img_path}")
                                    except Exception as e:
                                        print(f"   [图片] 删除图片文件时出错: {e}")

                                # 3. Send notification if recommended
                                if ai_analysis_result and ai_analysis_result.get('is_recommended'):
                                    print(f"   -> 商品被AI推荐，准备发送通知...")
                                    await send_ntfy_notification(item_data, ai_analysis_result.get("reason", "无"))
                            # --- END: Real-time AI Analysis & Notification ---

                            # 4. 保存包含AI结果的完整记录
                            await save_to_jsonl(final_record, keyword)

                            processed_links.add(unique_key)
                            processed_item_count += 1
                            print(f"   -> 商品处理流程完毕。累计处理 {processed_item_count} 个新商品。")

                            # --- 修改: 增加单个商品处理后的主要延迟 ---
                            print("   [反爬] 执行一次主要的随机延迟以模拟用户浏览间隔...")
                            #await random_sleep(15, 30) # 原来是 (8, 15)，这是最重要的修改之一
                        else:
                            print(f"   错误: 获取商品详情API响应失败，状态码: {detail_response.status}")
                            if AI_DEBUG_MODE:
                                print(f"--- [DETAIL DEBUG] FAILED RESPONSE from {item_data['商品链接']} ---")
                                try:
                                    print(await detail_response.text())
                                except Exception as e:
                                    print(f"无法读取响应内容: {e}")
                                print("----------------------------------------------------")

                    except PlaywrightTimeoutError:
                        print(f"   错误: 访问商品详情页或等待API响应超时。")
                    except Exception as e:
                        print(f"   错误: 处理商品详情时发生未知错误: {e}")
                    finally:
                        await detail_page.close()
                        # --- 修改: 增加关闭页面后的短暂整理时间 ---
                        await random_sleep(2, 4) # 原来是 (1, 2.5)

                # --- 新增: 在处理完一页所有商品后，翻页前，增加一个更长的“休息”时间 ---
                if not stop_scraping and page_num < max_pages:
                    print(f"--- 第 {page_num} 页处理完毕，准备翻页。执行一次页面间的长时休息... ---")
                    await random_sleep(25, 50)

        except PlaywrightTimeoutError as e:
            print(f"\n操作超时错误: 页面元素或网络响应未在规定时间内出现。\n{e}")
        except Exception as e:
            print(f"\n爬取过程中发生未知错误: {e}")
        finally:
            print("\nLOG: 任务执行完毕，浏览器将在5秒后自动关闭...")
            await asyncio.sleep(5)
            if debug_limit:
                input("按回车键关闭浏览器...")
            await browser.close()

    # 清理任务图片目录
    cleanup_task_images(task_config.get('task_name', 'default'))

    return processed_item_count
