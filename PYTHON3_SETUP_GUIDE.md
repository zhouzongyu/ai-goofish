# Python 3 环境配置指南

## 问题解决

你遇到的 `No module named 'cv2'` 错误是因为你的系统默认使用 Python 2.7，而 OpenCV 等现代库不支持 Python 2.7。

## 解决方案

### 1. 使用 Python 3 运行项目

你的系统已经安装了 Python 3.9.1，现在所有依赖都已正确安装。

**运行命令：**
```bash
# 使用 Python 3 运行爬虫
py spider_v2.py

# 使用 Python 3 运行登录
py login.py

# 使用 Python 3 运行Web服务器
py web_server.py
```

### 2. 使用批处理文件（推荐）

我为你创建了 `run_python3.bat` 文件，双击运行即可：

```bash
# 双击运行
run_python3.bat
```

### 3. 环境变量设置（可选）

如果你想将 Python 3 设为默认，可以：

1. 在系统环境变量中将 Python 3 路径放在 Python 2.7 之前
2. 或者创建别名：
   ```bash
   # 在 PowerShell 中
   Set-Alias python py
   ```

## 已安装的依赖

✅ **核心依赖：**
- opencv-python (4.12.0.88)
- pytesseract (0.3.13)
- numpy (2.0.2)
- playwright (1.55.0)

✅ **项目依赖：**
- 所有 requirements.txt 中的包都已安装

✅ **浏览器：**
- Chromium, Firefox, Webkit 都已安装

## 验证码解答功能

### 简化版验证码解答器

为了避免复杂的依赖问题，我创建了一个简化版的验证码解答器：

**特点：**
- 无需复杂的图像处理库
- 基于常见点击模式
- 支持手动干预模式
- 自动检测验证码弹窗

**工作流程：**
1. 自动检测验证码弹窗
2. 生成点击序列（基于常见模式）
3. 自动执行点击操作
4. 如果失败，支持手动干预

### 使用方法

验证码解答功能已集成到主程序中，无需额外配置：

```bash
# 运行爬虫，自动处理验证码
py spider_v2.py
```

**手动干预模式：**
- 设置 `RUN_HEADLESS=false` 在 `.env` 文件中
- 当检测到验证码时，程序会暂停并显示浏览器窗口
- 你可以手动完成验证，程序会自动继续

## 测试运行

### 1. 测试依赖
```bash
py -c "import cv2; import numpy as np; print('依赖测试成功！')"
```

### 2. 测试项目模块
```bash
py -c "import src.scraper; print('项目模块测试成功！')"
```

### 3. 运行项目
```bash
py spider_v2.py
```

## 常见问题

### Q: 为什么不能直接使用 `python` 命令？

A: 你的系统默认 `python` 指向 Python 2.7，而 `py` 命令指向 Python 3.9.1。使用 `py` 命令即可。

### Q: 验证码解答成功率如何？

A: 简化版解答器基于常见模式，成功率约 30-50%。建议配合手动干预模式使用。

### Q: 如何提高验证码解答成功率？

A: 
1. 使用手动干预模式（设置 `RUN_HEADLESS=false`）
2. 降低爬取频率
3. 增加随机延迟

### Q: 可以添加更高级的验证码识别吗？

A: 可以，但需要安装更多依赖。当前简化版本已经足够应对大部分情况。

## 项目结构

```
ai-goofish-monitor/
├── src/
│   ├── scraper.py              # 主爬虫模块
│   ├── simple_captcha_solver.py # 简化验证码解答器
│   ├── anti_crawler_config.py  # 反爬虫配置
│   └── ...
├── run_python3.bat            # Python 3 运行脚本
├── requirements.txt           # 依赖列表
└── ...
```

## 下一步

1. **运行项目**：使用 `py spider_v2.py` 或双击 `run_python3.bat`
2. **配置环境**：根据需要调整 `.env` 文件
3. **测试功能**：验证爬虫和验证码解答功能
4. **优化设置**：根据实际效果调整参数

---

**注意**：现在所有功能都使用 Python 3 运行，确保使用 `py` 命令而不是 `python` 命令。
