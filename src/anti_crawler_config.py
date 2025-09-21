"""
反爬虫策略配置文件
用于管理各种反爬虫检测和绕过策略
"""

# 反爬虫检测选择器配置
ANTI_CRAWLER_SELECTORS = {
    # 主要验证弹窗
    "main_dialogs": [
        "div.baxia-dialog-mask",
        "div.J_MIDDLEWARE_FRAME_WIDGET",
        "div[class*='baxia-dialog']",
        "div[class*='verify-dialog']",
        "div[class*='captcha-dialog']",
        "div[class*='anti-robot']",
    ],
    
    # 滑动验证相关
    "slider_verification": [
        "div[class*='slider']",
        "div[class*='drag']",
        "div[class*='puzzle']",
        "div[class*='slider-verify']",
    ],
    
    # 其他验证元素
    "other_verification": [
        "div[class*='verification']",
        "div[class*='challenge']",
        "iframe[src*='captcha']",
        "iframe[src*='verify']",
        "div[class*='human-verify']",
    ],
    
    # 异常提示文本
    "warning_texts": [
        "text=异常流量",
        "text=请完成验证",
        "text=安全验证",
        "text=人机验证",
        "text=滑动验证",
        "text=点击验证",
        "text=验证码",
        "text=请稍后再试",
        "text=访问过于频繁",
    ],
}

# 页面异常检测关键词
SUSPICIOUS_INDICATORS = [
    "验证", "captcha", "verify", "challenge", "robot", "异常",
    "block", "ban", "limit", "rate", "frequency"
]

# JavaScript错误检测关键词
JS_ERROR_KEYWORDS = [
    "captcha", "verify", "robot", "block", "ban", "limit",
    "rate", "frequency", "anti", "crawler", "bot"
]

# 重试策略配置
RETRY_STRATEGY = {
    "max_retries": 3,
    "base_delay": 60,  # 基础延迟（秒）
    "max_delay": 300,  # 最大延迟（秒）
    "delay_multiplier": 2,  # 延迟倍数
}

# 手动干预配置
MANUAL_INTERVENTION = {
    "max_wait_time": 300,  # 最大等待时间（秒）
    "check_interval": 10,  # 检查间隔（秒）
    "stabilization_delay": 5,  # 稳定化延迟（秒）
}

# 隐身模式配置
STEALTH_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
    "device_scale_factor": 1,
    "is_mobile": False,
    "has_touch": False,
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai",
    "geolocation": {"latitude": 39.9042, "longitude": 116.4074},
    "permissions": ["geolocation"],
    "extra_http_headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
}

# 延迟策略配置
DELAY_STRATEGY = {
    "page_load_delay": (2, 4),  # 页面加载延迟范围
    "action_delay": (1, 3),     # 操作间延迟范围
    "item_delay": (15, 30),     # 商品处理延迟范围
    "page_delay": (25, 50),     # 翻页延迟范围
    "retry_delay": (60, 300),   # 重试延迟范围
}

# 检测策略配置
DETECTION_STRATEGY = {
    "check_timeout": 2,  # 检测超时时间（秒）
    "recheck_interval": 10,  # 重新检测间隔（秒）
    "max_detection_attempts": 3,  # 最大检测尝试次数
}

def get_all_detection_selectors():
    """获取所有检测选择器"""
    all_selectors = []
    for category, selectors in ANTI_CRAWLER_SELECTORS.items():
        all_selectors.extend(selectors)
    return all_selectors

def get_retry_delay(retry_count: int) -> int:
    """计算重试延迟时间"""
    base_delay = RETRY_STRATEGY["base_delay"]
    max_delay = RETRY_STRATEGY["max_delay"]
    multiplier = RETRY_STRATEGY["delay_multiplier"]
    
    delay = base_delay * (multiplier ** retry_count)
    return min(delay, max_delay)

def should_retry(retry_count: int) -> bool:
    """判断是否应该重试"""
    return retry_count < RETRY_STRATEGY["max_retries"]
