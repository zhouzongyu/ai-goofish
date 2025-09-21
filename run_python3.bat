@echo off
echo 使用 Python 3 运行闲鱼监控项目
echo ================================

REM 检查 Python 3 是否可用
py --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python 3
    echo 请确保已安装 Python 3.7 或更高版本
    pause
    exit /b 1
)

echo 检测到 Python 3 环境
py --version

echo.
echo 选择运行模式:
echo 1. 运行爬虫 (spider_v2.py)
echo 2. 运行登录 (login.py)
echo 3. 运行Web服务器 (web_server.py)
echo 4. 安装依赖
echo 5. 退出

set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" (
    echo 启动爬虫...
    py spider_v2.py
) else if "%choice%"=="2" (
    echo 启动登录...
    py login.py
) else if "%choice%"=="3" (
    echo 启动Web服务器...
    py web_server.py
) else if "%choice%"=="4" (
    echo 安装依赖...
    py -m pip install -r requirements.txt
    py -m playwright install
) else if "%choice%"=="5" (
    echo 退出
    exit /b 0
) else (
    echo 无效选择
)

pause
