# 常见问题解答 (FAQ)

本文档整理了用户在使用 AI-Goofish-Monitor 项目时遇到的常见问题和解决方案。

---

### **Q1: AI 分析与配置**

#### 问：为什么日志显示 `任务未配置AI prompt，跳过分析` 或 `AI推荐：待定；原因：无分析`？

**答：** 这是因为您没有为该监控任务启用或正确配置 AI 分析功能。

1.  打开 `config.json` 文件。
2.  找到您要配置的任务。
3.  确保 `enable_ai_analysis` 的值是 `true`。
4.  确保 `ai_prompt_file` 指向一个真实存在的、为您需求定制的分析标准 `.txt` 文件。如果您还没有自己的标准，可以先使用 `prompts/macbook_criteria.txt` 作为模板。

#### 问：创建任务或运行时，提示 "Request timed out", "Connection error", "404错误" 或 `函数 get_ai_analysis ... 尝试失败` 是什么原因？

**答：** 这通常是网络问题或AI服务配置错误，表示你的服务器无法连接到 `.env` 文件中配置的 `OPENAI_BASE_URL`。请检查：
*   **API 密钥问题**：检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确、有效，或者账户是否余额不足。
*   **网络问题**：确保您的服务器可以正常访问 `OPENAI_BASE_URL` 指定的 AI 服务地址。如果在中国大陆，访问国外 AI 服务（如 OpenAI, Gemini）可能需要设置网络代理。现在你可以直接在 `.env` 文件中配置 `PROXY_URL` 变量来解决此问题。
*   **API端点地址错误**：确认 `OPENAI_BASE_URL` 地址填写正确，并且该服务正在正常运行。如果遇到404错误，建议先使用阿里云或火山引擎等国内服务商的API进行调试。
*   **模型名称错误**：检查 `.env` 文件中的 `OPENAI_MODEL_NAME` 是否是您所用服务提供的正确模型。

#### 问：我选择的 AI 模型不支持图片分析怎么办？

**答：** 本项目的核心优势之一是结合图片进行多模态分析，因此 **必须** 选择一个支持图片识别（Vision / Multi-modal）的 AI 模型。如果你配置的模型不支持图片，AI 分析会失败或效果大打折扣。请在 `.env` 文件中将 `OPENAI_MODEL_NAME` 更换为支持图片输入的模型，例如 `gpt-4o`, `gemini-1.5-pro`, `deepseek-v2`, `qwen-vl-plus` 等。

#### 问：如何配置使用 Gemini / Qwen 或其他非 OpenAI 的大语言模型？

**答：** 本项目理论上支持任何提供 OpenAI 兼容 API 接口的模型。关键在于正确配置 `.env` 文件中的三个变量：
*   `OPENAI_API_KEY`: 你的模型服务商提供的 API Key。
*   `OPENAI_BASE_URL`: 模型服务商提供的 API-Compatible Endpoint 地址。请务必查阅你所使用模型的官方文档，通常格式为 `https://api.your-provider.com/v1` (注意，末尾不需要 `/chat/completions`)。
*   `OPENAI_MODEL_NAME`: 你要使用的具体模型名称，需要模型支持图片识别，例如 `gemini-2.5-flash`。
- **示例:** 如果你的服务商文档说 Completions 接口是 `https://xx.xx.com/v1/chat/completions`，那么 `OPENAI_BASE_URL` 就应该填 `https://xx.xx.com/v1`。

#### 问：为什么AI模型连接测试失败，提示 "Invalid JSON payload received. Unknown name "enable_thinking": Cannot find field" 错误？

**答：** 这是因为某些AI模型不支持 `enable_thinking` 参数导致的。项目现在支持通过环境变量 `ENABLE_THINKING` 来控制是否添加这个参数：

*   **解决方案：** 在 `.env` 文件中设置 `ENABLE_THINKING=false`，然后重新运行AI模型连接测试。
*   **默认行为：** 从项目v1.0版本开始，默认情况下 `ENABLE_THINKING` 设置为 `false`，不会添加 `enable_thinking` 参数，以兼容更多AI模型。
*   **特殊需求：** 如果你使用的AI模型需要这个参数，可以将 `ENABLE_THINKING` 设置为 `true`。

---

### **Q3: 登录与反爬虫**

#### 问：为什么 `xianyu_state.json` 文件会自动消失？

**答：** 当程序检测到 `xianyu_state.json` 中的登录凭证失效时，会自动删除该文件，以强制您重新登录获取有效的 Cookie。如果遇到此问题，请重新登录闲鱼后通过chrome插件提取cookie。

#### 问：运行一段时间后被闲鱼检测到，提示“异常流量”或需要滑动验证？

**答：** 这是闲鱼的反爬虫机制。为了降低被检测的风险，可以尝试以下方法：
*   **关闭无头模式:** 在 `.env` 文件中设置 `RUN_HEADLESS=false`。这样浏览器会以有界面的方式运行，当出现滑动验证码时，你可以手动完成验证，程序会继续执行。
*   **降低监控频率:** 在 `config.json` 中，适当调大 `scheduler_interval_minutes` 的值，例如从 `5` 分钟改为 `15` 或 `30` 分钟。
*   **使用代理**：（进阶）在 `.env` 文件中配置 `PROXY_URL` 来避免IP被封禁。
*   **重新登录**：删除旧的 `xianyu_state.json` 文件，重新登录闲鱼后通过chrome插件提取cookie。

---

### **Q4: 环境与部署**

#### 问：运行 `login.py` 或 `spider_v2.py` 时出现 `'gbk' codec can't encode character` 相关的编码错误？
**答:** 这是典型的 Windows 环境下的编码问题。项目代码和日志默认使用 UTF-8 编码。
- **解决方案:** 在运行 Python 脚本前，通过设置环境变量强制使用 UTF-8。在 PowerShell 或 CMD 中执行以下命令，然后再运行脚本：

    ```bash
    set PYTHONUTF8=1
    python spider_v2.py
    ```

    或者使用 `chcp 65001` 命令切换活动代码页为 UTF-8。

#### 问：运行 `login.py` 时提示需要 `playwright install` 或报错 `Old Headless mode has been removed from the Chrome binary` 怎么办？
**答:** 这个错误表示 Playwright 运行所需的浏览器文件缺失或版本不兼容。推荐的解决方法是，确保所有依赖都已通过 `requirements.txt` 正确安装。请在命令行中运行：

    ```bash
    pip install -r requirements.txt
    ```

    如果问题依旧，可以尝试手动安装或更新 chromium 浏览器：

    ```bash
    playwright install chromium
    ```

#### 问：pyzbar 在 Windows 上安装失败怎么办？
**答:** pyzbar 在 Windows 上需要额外的 zbar 动态链接库支持。
- **解决方案 (Windows):**
    - **方法1 (推荐):** 使用 Chocolatey 安装：

        ```cmd
        choco install zbar
        ```

    - **方法2:** 手动下载并添加到 PATH：
        1. 从 [zbar releases](https://github.com/NaturalHistoryMuseum/pyzbar/releases) 下载对应版本的 `libzbar-64.dll`
        2. 将文件放到 Python 安装目录或添加到系统 PATH
    - **方法3:** 使用 conda 安装：

        ```cmd
        conda install -c conda-forge zbar
        ```

- **Linux 用户:** 直接安装系统包即可：

    ```bash
    # Ubuntu/Debian
    sudo apt-get install libzbar0
    
    # CentOS/RHEL
    sudo yum install zbar
    
    # Arch Linux
    sudo pacman -S zbar
    ```

#### 问：运行 `login.py` 时提示 `ModuleNotFoundError: No module named 'PIL'` 是什么原因？
**答:** 这个错误通常是因为Python版本过低或者依赖包安装不完整导致的。本项目推荐使用 Python 3.10 或更高版本。
- **解决方案:**
    - 确保使用 Python 3.10+ 版本运行项目
    - 重新安装依赖包：

        ```bash
        pip install -r requirements.txt
        ```

    - 如果问题依旧，可以尝试单独安装 Pillow 包：

        ```bash
        pip install Pillow
        ```

#### 问：使用 Docker 部署时，日志报错 `客户端初始化出错`。
**答:** 这通常是 Docker 容器内共享内存不足导致的。在运行 `docker run` 命令时，请添加 `--shm-size=1gb` 参数，例如：
```bash
docker run --shm-size=1gb -v "$(pwd)":/app ai-goofish-monitor
```
如果使用 `docker-compose`，可以在 `docker-compose.yaml` 中为服务添加 `shm_size: '1gb'`。

#### 问：我可以在群晖 (Synology) NAS 上通过 Docker 部署吗？
**答:** 可以。部署步骤与标准的 Docker 部署基本一致。注意：在群晖环境中部署时，可能需要配置Docker镜像仓库访问权限，确保能够正常拉取镜像。

---

### **Q5: 功能使用问题**

#### 问：如何设置定时任务的执行频率？

**答：** 定时任务的执行频率由 `config.json` 文件中的全局参数 `scheduler_interval_minutes` 控制。它定义了调度器每隔多少分钟检查并执行所有已启用的任务。例如，设置为 `10`，则所有启用的任务会每隔 10 分钟运行一次。
