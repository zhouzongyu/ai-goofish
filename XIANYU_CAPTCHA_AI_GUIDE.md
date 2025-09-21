# XianyuCaptchaAI 使用指南

## 概述

`XianyuCaptchaAI` 是一个专门用于识别和解答闲鱼验证码的AI模块，使用计算机视觉和机器学习技术来自动识别图像拼图验证码。

## 主要功能

### 1. 智能图像识别
- **图标识别**：识别汉堡包、勾选、时钟、贝壳、人物、礼物、垃圾桶、灯泡、对话气泡等图标
- **颜色分析**：分析背景颜色（黄色、粉色、蓝色、绿色）
- **字符特征**：识别中文字符的形状特征

### 2. 自动解答算法
- **优先级计算**：基于图标类型、背景颜色、字符特征计算点击优先级
- **智能排序**：自动生成最优点击序列
- **自动执行**：自动完成点击操作

## 使用方法

### 1. 基本使用

```python
from src.xianyu_captcha_ai import captcha_ai
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 导航到闲鱼页面
        await page.goto("https://www.goofish.com/")
        
        # 使用AI解答验证码
        success = await captcha_ai.solve_captcha_with_ai(page)
        
        if success:
            print("验证码解答成功！")
        else:
            print("验证码解答失败！")
        
        await browser.close()
```

### 2. 集成到爬虫中

```python
from src.xianyu_captcha_ai import captcha_ai

async def handle_captcha(page):
    """处理验证码"""
    print("检测到验证码，开始AI识别...")
    
    # 使用AI解答验证码
    result = await captcha_ai.solve_captcha_with_ai(page)
    
    if result:
        print("✅ AI识别成功，继续执行任务")
        return True
    else:
        print("❌ AI识别失败，需要手动处理")
        return False
```

### 3. 手动分析验证码

```python
import cv2
from src.xianyu_captcha_ai import captcha_ai

# 加载验证码图像
img = cv2.imread("captcha_image.png")

# 分析单个格子
cell_analysis = captcha_ai.analyze_cell_content(img)

print(f"图标类型: {cell_analysis['icon_type']}")
print(f"背景颜色: {cell_analysis['background_color']}")
print(f"字符特征: {cell_analysis['character_feature']}")
print(f"置信度: {cell_analysis['confidence']}")
```

## 配置选项

### 1. 字符模式配置

```python
# 在 XianyuCaptchaAI 类中修改
self.character_patterns = {
    '的': {'features': ['hamburger', 'yellow'], 'priority': 1},
    '闲': {'features': ['checkmark', 'pink'], 'priority': 2},
    # ... 其他字符
}
```

### 2. 图标模板调整

```python
def _create_hamburger_template(self):
    """自定义汉堡包图标模板"""
    template = np.zeros((20, 20), dtype=np.uint8)
    # 调整模板形状
    cv2.rectangle(template, (2, 8), (18, 10), 255, -1)
    return template
```

### 3. 优先级权重调整

```python
def _calculate_priority(self, analysis: Dict) -> int:
    """调整优先级计算权重"""
    priority = 0
    
    # 图标权重
    icon_weight = 10
    # 颜色权重  
    color_weight = 1
    # 字符权重
    char_weight = 100
    
    return priority
```

## 工作流程

### 1. 检测阶段
```python
# 检测验证码弹窗
captcha_selectors = [
    "div[class*='captcha']",
    "div[class*='verify']",
    "div[class*='puzzle']",
    "text=请依次连出",
]
```

### 2. 图像处理阶段
```python
# 截图保存验证码
screenshot_path = "temp_captcha_ai.png"
await captcha_dialog.screenshot(path=screenshot_path)

# 读取并预处理图像
img = cv2.imread(screenshot_path)
```

### 3. 分析阶段
```python
# 提取3x3网格
for row in range(3):
    for col in range(3):
        cell_img = img[y1:y2, x1:x2]
        analysis = self.analyze_cell_content(cell_img)
```

### 4. 解答阶段
```python
# 生成点击序列
click_sequence = self.solve_puzzle_sequence(cell_analyses)

# 执行点击操作
await self._execute_click_sequence(page, captcha_dialog, click_sequence)
```

## 识别准确率优化

### 1. 模板优化
- 根据实际验证码调整图标模板
- 优化模板匹配阈值
- 添加更多图标变体

### 2. 特征权重调整
```python
# 调整各特征权重
icon_priority = {
    'hamburger': 1, 'checkmark': 2, 'clock': 3,
    'shell': 4, 'person': 5, 'gift': 6,
    'trash': 7, 'lightbulb': 8, 'speech': 9
}
```

### 3. 图像预处理优化
```python
def preprocess_image(self, image_path: str) -> np.ndarray:
    """优化图像预处理"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 调整二值化阈值
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # 优化去噪参数
    denoised = cv2.medianBlur(binary, 3)
    
    return denoised
```

## 故障排除

### 1. 识别失败
```python
# 检查图像质量
img = cv2.imread("captcha.png")
if img is None:
    print("图像读取失败")

# 检查模板匹配
result = cv2.matchTemplate(cell_img, template, cv2.TM_CCOEFF_NORMED)
_, max_val, _, _ = cv2.minMaxLoc(result)
print(f"匹配度: {max_val}")
```

### 2. 点击失败
```python
# 检查坐标计算
bounding_box = await captcha_dialog.bounding_box()
cell_x = col * (bounding_box['width'] // 3) + 50
cell_y = row * (bounding_box['height'] // 3) + 50

# 验证点击坐标
print(f"点击坐标: ({cell_x}, {cell_y})")
```

### 3. 验证不通过
```python
# 检查点击序列
print(f"点击序列: {click_sequence}")

# 调整等待时间
await asyncio.sleep(3)  # 增加等待时间
```

## 高级用法

### 1. 自定义识别规则
```python
class CustomXianyuCaptchaAI(XianyuCaptchaAI):
    def solve_puzzle_sequence(self, cell_analyses: List[Dict]) -> List[Tuple[int, int]]:
        """自定义解答规则"""
        # 实现自定义逻辑
        pass
```

### 2. 批量处理
```python
async def batch_solve_captchas(pages: List[Page]):
    """批量处理多个验证码"""
    results = []
    for page in pages:
        result = await captcha_ai.solve_captcha_with_ai(page)
        results.append(result)
    return results
```

### 3. 结果统计
```python
class CaptchaStats:
    def __init__(self):
        self.total_attempts = 0
        self.successful_attempts = 0
    
    def record_attempt(self, success: bool):
        self.total_attempts += 1
        if success:
            self.successful_attempts += 1
    
    @property
    def success_rate(self):
        return self.successful_attempts / self.total_attempts if self.total_attempts > 0 else 0
```

## 注意事项

⚠️ **重要提醒**：

1. **依赖要求**：需要安装 OpenCV、NumPy 等依赖
2. **图像质量**：确保验证码图像清晰，避免模糊
3. **网络延迟**：考虑网络延迟对识别的影响
4. **合法使用**：请确保遵守相关法律法规
5. **持续优化**：根据实际效果调整参数

## 示例代码

### 完整示例
```python
import asyncio
from playwright.async_api import async_playwright
from src.xianyu_captcha_ai import captcha_ai

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 导航到闲鱼
            await page.goto("https://www.goofish.com/")
            
            # 等待可能的验证码
            await page.wait_for_timeout(3000)
            
            # 尝试解答验证码
            success = await captcha_ai.solve_captcha_with_ai(page)
            
            if success:
                print("🎉 验证码解答成功！")
            else:
                print("😞 验证码解答失败，需要手动处理")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

**总结**：`XianyuCaptchaAI` 提供了强大的验证码识别和解答功能，通过合理配置和使用，可以大大提高自动化爬取的效率。
