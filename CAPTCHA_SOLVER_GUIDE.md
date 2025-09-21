# 闲鱼验证码自动解答指南

## 概述

本项目实现了针对闲鱼图像拼图验证码的自动识别和解答功能，能够自动处理类似你提供的验证码弹窗。

## 验证码类型分析

从你提供的图片可以看出，这是一个**3x3图像拼图验证码**，具有以下特征：

- **布局**：3行3列的网格布局
- **内容**：每个格子包含中文字符和对应图标
- **任务**：按顺序连接特定的图像
- **交互**：需要鼠标点击按顺序连接

## 技术实现

### 1. 双重识别策略

#### AI识别方法（主要）
- **图像特征识别**：使用OpenCV进行图像处理
- **模板匹配**：预定义图标模板进行匹配
- **颜色分析**：分析背景颜色特征
- **轮廓检测**：识别字符形状特征

#### 传统OCR方法（备用）
- **OCR识别**：使用Tesseract进行中文字符识别
- **图像预处理**：二值化、去噪等处理
- **特征提取**：提取字符和图标特征

### 2. 智能解答算法

```python
# 优先级计算示例
def calculate_priority(analysis):
    priority = 0
    
    # 图标优先级
    icon_priority = {
        'hamburger': 1, 'checkmark': 2, 'clock': 3,
        'shell': 4, 'person': 5, 'gift': 6,
        'trash': 7, 'lightbulb': 8, 'speech': 9
    }
    
    # 背景颜色优先级
    color_priority = {'yellow': 1, 'pink': 2, 'blue': 3, 'green': 4}
    
    # 字符特征优先级
    char_priority = {'的': 1, '闲': 2, '禅': 3, '露': 4, '昨': 5, '加': 6, '古': 7, '漠': 8, '语': 9}
    
    return priority
```

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Tesseract OCR

**Windows:**
```bash
# 下载并安装 Tesseract OCR
# 默认路径: C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang
```

### 3. 运行脚本

```bash
python spider_v2.py
```

## 工作流程

### 1. 自动检测
- 程序运行时会自动检测验证码弹窗
- 支持多种检测选择器

### 2. 图像识别
- 截取验证码区域
- 提取3x3网格中的每个格子
- 分析每个格子的内容特征

### 3. 智能解答
- 基于特征计算优先级
- 生成点击序列
- 自动执行点击操作

### 4. 结果验证
- 等待验证结果
- 检测是否成功通过验证

## 配置选项

### 验证码检测配置

```python
# 在 src/anti_crawler_config.py 中
ANTI_CRAWLER_SELECTORS = {
    "main_dialogs": [
        "div.baxia-dialog-mask",
        "div.J_MIDDLEWARE_FRAME_WIDGET",
        "div[class*='captcha']",
        "div[class*='verify']",
        "div[class*='puzzle']",
    ],
    "warning_texts": [
        "text=请依次连出",
        "text=请按顺序点击",
        "text=验证码",
    ],
}
```

### 识别参数调整

```python
# 在 src/xianyu_captcha_ai.py 中
def _calculate_priority(self, analysis: Dict) -> int:
    # 可以调整各种特征的权重
    icon_weight = 10      # 图标权重
    color_weight = 1      # 颜色权重
    char_weight = 100     # 字符权重
```

## 识别准确率优化

### 1. 模板优化
- 根据实际验证码调整图标模板
- 优化模板匹配阈值

### 2. 特征权重调整
- 根据识别效果调整各特征权重
- 优化优先级计算算法

### 3. 图像预处理
- 调整二值化阈值
- 优化去噪参数

## 故障排除

### 1. 识别失败
- 检查Tesseract是否正确安装
- 验证图像预处理效果
- 调整识别参数

### 2. 点击失败
- 检查DOM选择器是否正确
- 验证坐标计算是否准确
- 调整点击延迟时间

### 3. 验证不通过
- 检查点击序列是否正确
- 调整验证等待时间
- 考虑手动干预模式

## 手动干预模式

当自动识别失败时，程序会：

1. **暂停执行**：显示浏览器窗口
2. **等待手动操作**：用户手动完成验证
3. **自动检测**：检测验证是否完成
4. **继续执行**：验证完成后自动继续

## 最佳实践

### 1. 提高识别率
- 保持验证码图像清晰
- 避免网络延迟影响
- 定期更新识别模板

### 2. 降低检测风险
- 使用随机延迟
- 模拟人类操作模式
- 避免频繁触发验证

### 3. 监控和调试
- 查看识别日志
- 保存失败案例
- 持续优化算法

## 技术细节

### 图像处理流程

```python
# 1. 图像预处理
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
denoised = cv2.medianBlur(binary, 3)

# 2. 网格提取
cell_height = height // 3
cell_width = width // 3
cell = img[y1:y2, x1:x2]

# 3. 特征识别
icon_type = self.detect_icon_in_cell(cell)
bg_color = self.detect_background_color(cell)
char_feature = self.extract_character_features(cell)
```

### 点击执行流程

```python
# 1. 计算点击坐标
cell_x = col * (dialog_width // 3) + offset_x
cell_y = row * (dialog_height // 3) + offset_y

# 2. 执行点击
await page.mouse.click(cell_x, cell_y)

# 3. 等待验证
await asyncio.sleep(2)
```

## 注意事项

⚠️ **重要提醒**：

1. **合法使用**：请确保遵守相关法律法规
2. **技术学习**：本工具仅供技术学习和研究
3. **适度使用**：避免过度频繁的请求
4. **持续优化**：根据实际效果调整参数

## 更新日志

- **v1.0**：基础验证码检测
- **v2.0**：AI图像识别
- **v3.0**：双重识别策略
- **v4.0**：智能解答算法

---

**免责声明**：本工具仅供技术学习和研究使用，使用者需自行承担使用风险，并确保遵守相关法律法规。
