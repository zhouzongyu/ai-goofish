#!/usr/bin/env python3
"""
XianyuCaptchaAI 使用示例
展示如何在你的项目中使用AI验证码识别
"""

import asyncio
from playwright.async_api import async_playwright
from src.xianyu_captcha_ai import captcha_ai

async def example_1_basic_usage():
    """示例1：基本使用方法"""
    print("📖 示例1：基本使用方法")
    print("-" * 30)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 导航到闲鱼
            await page.goto("https://www.goofish.com/")
            
            # 使用AI解答验证码
            success = await captcha_ai.solve_captcha_with_ai(page)
            
            if success:
                print("✅ 验证码解答成功！")
            else:
                print("ℹ️ 未检测到验证码或解答失败")
                
        finally:
            await browser.close()

async def example_2_integration_with_scraper():
    """示例2：集成到爬虫中"""
    print("\n📖 示例2：集成到爬虫中")
    print("-" * 30)
    
    async def handle_captcha_in_scraper(page):
        """在爬虫中处理验证码"""
        print("🔍 检测到验证码，开始AI识别...")
        
        # 使用AI解答验证码
        result = await captcha_ai.solve_captcha_with_ai(page)
        
        if result:
            print("✅ AI识别成功，继续执行任务")
            return True
        else:
            print("❌ AI识别失败，需要手动处理")
            return False
    
    # 模拟爬虫使用
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto("https://www.goofish.com/")
            
            # 在爬虫逻辑中调用
            captcha_handled = await handle_captcha_in_scraper(page)
            
            if captcha_handled:
                print("🚀 可以继续爬取数据")
            else:
                print("⏸️ 需要手动处理验证码")
                
        finally:
            await browser.close()

def example_3_manual_analysis():
    """示例3：手动分析验证码图像"""
    print("\n📖 示例3：手动分析验证码图像")
    print("-" * 30)
    
    # 如果你有验证码图像文件
    image_path = "captcha_image.png"
    
    if os.path.exists(image_path):
        try:
            import cv2
            img = cv2.imread(image_path)
            
            if img is not None:
                # 分析图像
                analysis = captcha_ai.analyze_cell_content(img)
                
                print(f"🔍 图标类型: {analysis['icon_type']}")
                print(f"🎨 背景颜色: {analysis['background_color']}")
                print(f"📝 字符特征: {analysis['character_feature']}")
                print(f"📊 置信度: {analysis['confidence']:.2f}")
            else:
                print("❌ 无法读取图像文件")
        except Exception as e:
            print(f"❌ 分析图像时出错: {e}")
    else:
        print("ℹ️ 未找到测试图像文件")

def example_4_custom_configuration():
    """示例4：自定义配置"""
    print("\n📖 示例4：自定义配置")
    print("-" * 30)
    
    # 创建自定义AI识别器
    class CustomCaptchaAI(captcha_ai.__class__):
        def __init__(self):
            super().__init__()
            # 自定义字符模式
            self.character_patterns.update({
                '新字符': {'features': ['new_icon', 'new_color'], 'priority': 10}
            })
        
        def _calculate_priority(self, analysis: dict) -> int:
            """自定义优先级计算"""
            priority = super()._calculate_priority(analysis)
            
            # 添加自定义逻辑
            if analysis['icon_type'] == 'hamburger':
                priority += 50  # 汉堡包优先级更高
            
            return priority
    
    # 使用自定义配置
    custom_ai = CustomCaptchaAI()
    print("✅ 自定义AI识别器创建成功")
    print(f"📋 字符模式数量: {len(custom_ai.character_patterns)}")

async def example_5_error_handling():
    """示例5：错误处理"""
    print("\n📖 示例5：错误处理")
    print("-" * 30)
    
    async def safe_captcha_solve(page):
        """安全的验证码解答，包含错误处理"""
        try:
            print("🔍 开始验证码识别...")
            result = await captcha_ai.solve_captcha_with_ai(page)
            return result
        except Exception as e:
            print(f"❌ 验证码识别出错: {e}")
            return False
    
    # 使用安全的方法
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto("https://www.goofish.com/")
            result = await safe_captcha_solve(page)
            print(f"🎯 识别结果: {result}")
        finally:
            await browser.close()

async def main():
    """运行所有示例"""
    print("🚀 XianyuCaptchaAI 使用示例")
    print("=" * 50)
    
    # 运行示例
    await example_1_basic_usage()
    await example_2_integration_with_scraper()
    example_3_manual_analysis()
    example_4_custom_configuration()
    await example_5_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ 所有示例运行完成！")
    print("💡 查看代码了解具体实现细节")

if __name__ == "__main__":
    import os
    asyncio.run(main())
