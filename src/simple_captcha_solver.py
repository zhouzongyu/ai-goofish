"""
简化的闲鱼验证码解答器
避免复杂依赖，专注于基本功能
"""

import asyncio
import os
from typing import List, Tuple, Dict, Optional
from playwright.async_api import Page


class SimpleCaptchaSolver:
    """简化的验证码解答器"""
    
    def __init__(self):
        self.grid_size = (3, 3)
        
    async def detect_captcha_dialog(self, page: Page) -> bool:
        """检测是否存在验证码弹窗"""
        captcha_selectors = [
            "div[class*='captcha']",
            "div[class*='verify']", 
            "div[class*='puzzle']",
            "div[class*='baxia-dialog']",
            "text=请依次连出",
            "text=请按顺序点击",
            "text=验证码",
        ]
        
        for selector in captcha_selectors:
            try:
                element = page.locator(selector)
                if await element.count() > 0 and await element.first.is_visible():
                    return True
            except:
                continue
        return False
    
    def get_click_sequence_by_pattern(self) -> List[Tuple[int, int]]:
        """基于常见模式生成点击序列"""
        # 常见的点击模式（可以根据实际情况调整）
        patterns = [
            # 模式1：从左到右，从上到下
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
            
            # 模式2：Z字形
            [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (2, 2)],
            
            # 模式3：螺旋形
            [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1)],
            
            # 模式4：对角线
            [(0, 0), (1, 1), (2, 2), (0, 2), (2, 0), (0, 1), (1, 0), (1, 2), (2, 1)],
        ]
        
        # 随机选择一个模式（这里选择第一个作为默认）
        import random
        return random.choice(patterns)
    
    async def execute_click_sequence(self, page: Page, click_sequence: List[Tuple[int, int]]):
        """执行点击序列"""
        try:
            print(f"🎯 开始执行点击序列: {click_sequence}")
            
            # 查找验证码容器
            captcha_container = None
            selectors = [
                "div[class*='captcha']",
                "div[class*='verify']",
                "div[class*='puzzle']",
                "div[class*='baxia-dialog']"
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector)
                    if await element.count() > 0 and await element.first.is_visible():
                        captcha_container = element.first
                        break
                except:
                    continue
            
            if not captcha_container:
                print("❌ 未找到验证码容器")
                return False
            
            # 获取容器尺寸
            bounding_box = await captcha_container.bounding_box()
            if not bounding_box:
                print("❌ 无法获取容器尺寸")
                return False
            
            container_width = bounding_box['width']
            container_height = bounding_box['height']
            cell_width = container_width / 3
            cell_height = container_height / 3
            
            # 执行点击
            for i, (row, col) in enumerate(click_sequence):
                print(f"🖱️ 点击第 {i+1} 个格子: ({row}, {col})")
                
                # 计算点击坐标（格子中心）
                x = bounding_box['x'] + col * cell_width + cell_width / 2
                y = bounding_box['y'] + row * cell_height + cell_height / 2
                
                try:
                    # 点击坐标
                    await page.mouse.click(x, y)
                    await asyncio.sleep(0.5)  # 短暂延迟
                except Exception as e:
                    print(f"⚠️ 点击失败: {e}")
                    continue
            
            # 等待验证结果
            print("⏰ 等待验证结果...")
            await asyncio.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ 执行点击序列失败: {e}")
            return False
    
    async def solve_captcha(self, page: Page) -> bool:
        """解答验证码"""
        try:
            print("🔍 开始检测验证码...")
            
            # 检测验证码弹窗
            if not await self.detect_captcha_dialog(page):
                print("❌ 未检测到验证码弹窗")
                return False
            
            print("✅ 检测到验证码弹窗")
            
            # 生成点击序列
            click_sequence = self.get_click_sequence_by_pattern()
            print(f"🎯 生成点击序列: {click_sequence}")
            
            # 执行点击
            success = await self.execute_click_sequence(page, click_sequence)
            
            if success:
                print("✅ 验证码解答完成")
                return True
            else:
                print("❌ 验证码解答失败")
                return False
                
        except Exception as e:
            print(f"❌ 验证码解答过程出错: {e}")
            return False
    
    async def manual_solve_captcha(self, page: Page) -> bool:
        """手动解答验证码（备用方案）"""
        print("\n--- 手动验证码解答模式 ---")
        print("检测到验证码，请在浏览器中手动完成验证。")
        print("完成验证后，程序将自动继续执行。")
        
        # 等待用户手动完成验证
        max_wait_time = 300  # 5分钟
        check_interval = 5   # 5秒检查一次
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            print(f"⏰ 等待验证完成... ({elapsed_time}/{max_wait_time}秒)")
            
            # 检查验证码是否还存在
            if not await self.detect_captcha_dialog(page):
                print("✅ 验证码已消失，验证可能已完成")
                await asyncio.sleep(2)  # 等待页面稳定
                return True
            
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
        
        print("❌ 等待超时，验证可能未完成")
        return False


# 全局简化验证码解答器实例
simple_captcha_solver = SimpleCaptchaSolver()
