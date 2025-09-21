#!/usr/bin/env python3
"""
XianyuCaptchaAI 测试脚本
演示如何使用AI验证码识别功能
"""

import asyncio
import os
from playwright.async_api import async_playwright
from src.xianyu_captcha_ai import captcha_ai

async def test_captcha_ai():
    """测试验证码AI识别功能"""
    print("🤖 开始测试 XianyuCaptchaAI...")
    
    async with async_playwright() as p:
        # 启动浏览器（非无头模式，方便观察）
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        try:
            print("🌐 导航到闲鱼首页...")
            await page.goto("https://www.goofish.com/", timeout=30000)
            
            print("⏰ 等待页面加载...")
            await page.wait_for_timeout(5000)
            
            print("🔍 检测验证码...")
            
            # 使用AI解答验证码
            success = await captcha_ai.solve_captcha_with_ai(page)
            
            if success:
                print("✅ 验证码解答成功！")
                print("🎉 AI识别功能正常工作")
            else:
                print("ℹ️ 未检测到验证码或解答失败")
                print("💡 这是正常的，因为可能没有触发验证码")
            
            # 等待一下让用户观察结果
            print("⏰ 等待5秒后关闭浏览器...")
            await page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
        finally:
            await browser.close()
            print("🔚 测试完成")

async def test_image_analysis():
    """测试图像分析功能（如果有测试图像）"""
    print("\n🖼️ 测试图像分析功能...")
    
    # 检查是否有测试图像
    test_images = [
        "test_captcha.png",
        "captcha_sample.png", 
        "temp_captcha_ai.png"
    ]
    
    for img_path in test_images:
        if os.path.exists(img_path):
            print(f"📁 找到测试图像: {img_path}")
            
            try:
                import cv2
                img = cv2.imread(img_path)
                if img is not None:
                    # 分析图像
                    analysis = captcha_ai.analyze_cell_content(img)
                    print(f"🔍 分析结果: {analysis}")
                else:
                    print(f"❌ 无法读取图像: {img_path}")
            except Exception as e:
                print(f"❌ 分析图像时出错: {e}")
            break
    else:
        print("ℹ️ 未找到测试图像，跳过图像分析测试")

def test_character_patterns():
    """测试字符模式配置"""
    print("\n📝 测试字符模式配置...")
    
    print("🔤 当前配置的字符模式:")
    for char, pattern in captcha_ai.character_patterns.items():
        print(f"  {char}: {pattern}")
    
    print(f"\n🎯 图标模板数量: {len(captcha_ai.icon_templates)}")
    print("📋 支持的图标类型:")
    for icon_name in captcha_ai.icon_templates.keys():
        print(f"  - {icon_name}")

async def main():
    """主测试函数"""
    print("=" * 50)
    print("🧪 XianyuCaptchaAI 功能测试")
    print("=" * 50)
    
    # 测试字符模式
    test_character_patterns()
    
    # 测试图像分析
    await test_image_analysis()
    
    # 测试完整功能
    await test_captcha_ai()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
