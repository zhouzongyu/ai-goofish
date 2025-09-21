# 闲鱼API设置指南

## 问题说明

当前API请求返回"令牌为空"错误，这是因为闲鱼API需要有效的认证信息。

## 解决方案

### 方法1：从浏览器获取Cookie和令牌

1. **打开浏览器开发者工具**
   - 按F12打开开发者工具
   - 切换到Network（网络）标签页

2. **访问闲鱼搜索页面**
   - 打开 https://www.goofish.com/
   - 搜索任意商品（如"按键精灵写脚本"）

3. **找到API请求**
   - 在Network标签页中找到 `mtop.taobao.idlemtopsearch.pc.search` 请求
   - 点击查看详情

4. **复制必要信息**
   - 复制完整的Cookie字符串
   - 复制sign参数值
   - 复制其他必要的请求头

### 方法2：使用浏览器自动化获取

```python
# 使用Playwright自动获取Cookie
from playwright.sync_api import sync_playwright

def get_cookies_and_sign():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 访问闲鱼并登录
        page.goto("https://www.goofish.com/")
        # 这里需要手动登录或使用已有的登录状态
        
        # 执行搜索
        page.fill('input[placeholder="搜索你想要"]', "按键精灵写脚本")
        page.click('button[type="submit"]')
        
        # 等待API请求
        response = page.wait_for_response(lambda r: "mtop.taobao.idlemtopsearch.pc.search" in r.url)
        
        # 获取请求信息
        request = response.request
        cookies = page.context.cookies()
        
        browser.close()
        return cookies, request.headers
```

### 方法3：更新现有代码

在 `src/scraper.py` 的 `search_xianyu_api` 函数中更新：

```python
# 更新Cookie（从浏览器复制）
headers = {
    "Host": "h5api.m.goofish.com",
    "Cookie": "你的完整Cookie字符串",
    # ... 其他请求头
}

# 更新签名（从浏览器复制）
params = {
    "sign": "你的签名值",
    # ... 其他参数
}
```

## 当前状态

✅ **API请求格式** - 已正确配置
✅ **SSL问题** - 已解决（使用Python 3.11）
✅ **请求头格式** - 已按照curl请求调整
⚠️ **认证信息** - 需要更新有效的Cookie和签名

## 下一步

1. 从浏览器获取最新的Cookie和签名
2. 更新 `search_xianyu_api` 函数中的参数
3. 测试API请求是否成功

## 注意事项

- Cookie和签名会过期，需要定期更新
- 建议使用浏览器自动化来动态获取认证信息
- 可以考虑将认证信息存储在配置文件中
