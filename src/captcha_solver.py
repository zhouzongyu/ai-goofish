"""
闲鱼验证码自动解答模块
支持图像拼图验证码的自动识别和解答
"""

import asyncio
import base64
import json
import os
import re
from typing import List, Tuple, Dict, Optional
import cv2
import numpy as np
from PIL import Image
import pytesseract
from playwright.async_api import Page, Locator
from src.xianyu_captcha_ai import captcha_ai

# 设置tesseract路径（Windows）
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class XianyuCaptchaSolver:
    """闲鱼验证码解答器"""
    
    def __init__(self):
        self.grid_size = (3, 3)  # 3x3网格
        self.cell_size = (100, 100)  # 每个格子的预期大小
        
    async def detect_captcha_dialog(self, page: Page) -> bool:
        """检测是否存在验证码弹窗"""
        captcha_selectors = [
            "div[class*='captcha']",
            "div[class*='verify']",
            "div[class*='puzzle']",
            "div[class*='baxia-dialog']",
            "text=请依次连出",
            "text=请按顺序点击",
        ]
        
        for selector in captcha_selectors:
            try:
                element = page.locator(selector)
                if await element.count() > 0 and await element.first.is_visible():
                    return True
            except:
                continue
        return False
    
    async def extract_captcha_image(self, page: Page) -> Optional[str]:
        """提取验证码图像"""
        try:
            # 查找验证码容器
            captcha_container = page.locator("div[class*='captcha'], div[class*='verify'], div[class*='puzzle']")
            if await captcha_container.count() == 0:
                return None
            
            # 截图保存验证码区域
            screenshot_path = "temp_captcha.png"
            await captcha_container.first.screenshot(path=screenshot_path)
            return screenshot_path
        except Exception as e:
            print(f"提取验证码图像失败: {e}")
            return None
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """图像预处理"""
        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("无法读取图像")
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # 去噪
        denoised = cv2.medianBlur(binary, 3)
        
        return denoised
    
    def extract_grid_cells(self, image: np.ndarray) -> List[np.ndarray]:
        """提取3x3网格中的每个格子"""
        height, width = image.shape
        cell_height = height // 3
        cell_width = width // 3
        
        cells = []
        for row in range(3):
            for col in range(3):
                y1 = row * cell_height
                y2 = (row + 1) * cell_height
                x1 = col * cell_width
                x2 = (col + 1) * cell_width
                
                cell = image[y1:y2, x1:x2]
                cells.append(cell)
        
        return cells
    
    def recognize_character(self, cell_image: np.ndarray) -> str:
        """识别格子中的中文字符"""
        try:
            # 使用OCR识别中文字符
            text = pytesseract.image_to_string(cell_image, lang='chi_sim')
            # 清理识别结果
            text = re.sub(r'[^\u4e00-\u9fff]', '', text)
            return text.strip()
        except Exception as e:
            print(f"字符识别失败: {e}")
            return ""
    
    def detect_icon_type(self, cell_image: np.ndarray) -> str:
        """检测格子中的图标类型"""
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(cv2.cvtColor(cell_image, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2HSV)
        
        # 检测不同颜色的区域
        color_ranges = {
            'yellow': ([20, 100, 100], [30, 255, 255]),
            'pink': ([140, 100, 100], [160, 255, 255]),
            'blue': ([100, 100, 100], [120, 255, 255]),
            'green': ([40, 100, 100], [80, 255, 255]),
        }
        
        dominant_color = 'unknown'
        max_area = 0
        
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            area = cv2.countNonZero(mask)
            if area > max_area:
                max_area = area
                dominant_color = color_name
        
        return dominant_color
    
    def analyze_captcha_content(self, image_path: str) -> List[Dict]:
        """分析验证码内容"""
        try:
            # 预处理图像
            processed_img = self.preprocess_image(image_path)
            
            # 提取网格格子
            cells = self.extract_grid_cells(processed_img)
            
            # 分析每个格子
            cell_analysis = []
            for i, cell in enumerate(cells):
                row = i // 3
                col = i % 3
                
                # 识别字符
                character = self.recognize_character(cell)
                
                # 检测图标类型
                icon_type = self.detect_icon_type(cell)
                
                cell_analysis.append({
                    'position': (row, col),
                    'index': i,
                    'character': character,
                    'icon_type': icon_type,
                    'cell_image': cell
                })
            
            return cell_analysis
        except Exception as e:
            print(f"分析验证码内容失败: {e}")
            return []
    
    def solve_puzzle_sequence(self, cell_analysis: List[Dict]) -> List[Tuple[int, int]]:
        """解答拼图序列"""
        # 根据字符和图标特征推断正确的点击顺序
        # 这里需要根据具体的验证码规则来实现
        
        # 示例：按字符的笔画数或特定规则排序
        def get_click_priority(cell):
            char = cell['character']
            icon = cell['icon_type']
            
            # 简单的优先级规则（需要根据实际情况调整）
            priority = 0
            
            # 根据字符优先级
            if char in ['的', '闲', '禅']:
                priority += 10
            elif char in ['露', '昨', '加']:
                priority += 20
            elif char in ['古', '漠', '语']:
                priority += 30
            
            # 根据图标类型优先级
            if icon == 'yellow':
                priority += 1
            elif icon == 'pink':
                priority += 2
            elif icon == 'blue':
                priority += 3
            
            return priority
        
        # 按优先级排序
        sorted_cells = sorted(cell_analysis, key=get_click_priority)
        
        # 返回点击顺序（坐标）
        click_sequence = []
        for cell in sorted_cells:
            click_sequence.append(cell['position'])
        
        return click_sequence
    
    async def solve_captcha(self, page: Page) -> bool:
        """自动解答验证码"""
        try:
            print("🔍 开始检测验证码...")
            
            # 检测验证码弹窗
            if not await self.detect_captcha_dialog(page):
                print("❌ 未检测到验证码弹窗")
                return False
            
            print("✅ 检测到验证码弹窗")
            
            # 首先尝试AI方法
            print("🤖 尝试AI识别方法...")
            ai_result = await captcha_ai.solve_captcha_with_ai(page)
            if ai_result:
                print("✅ AI识别成功")
                return True
            
            print("⚠️ AI识别失败，尝试传统方法...")
            
            # 提取验证码图像
            image_path = await self.extract_captcha_image(page)
            if not image_path:
                print("❌ 无法提取验证码图像")
                return False
            
            print("✅ 验证码图像提取成功")
            
            # 分析验证码内容
            cell_analysis = self.analyze_captcha_content(image_path)
            if not cell_analysis:
                print("❌ 验证码内容分析失败")
                return False
            
            print("✅ 验证码内容分析完成")
            
            # 解答拼图序列
            click_sequence = self.solve_puzzle_sequence(cell_analysis)
            if not click_sequence:
                print("❌ 无法确定点击序列")
                return False
            
            print(f"✅ 点击序列确定: {click_sequence}")
            
            # 执行点击操作
            await self.execute_click_sequence(page, click_sequence)
            
            # 清理临时文件
            if os.path.exists(image_path):
                os.remove(image_path)
            
            print("✅ 验证码解答完成")
            return True
            
        except Exception as e:
            print(f"❌ 验证码解答失败: {e}")
            return False
    
    async def execute_click_sequence(self, page: Page, click_sequence: List[Tuple[int, int]]):
        """执行点击序列"""
        try:
            # 查找验证码网格容器
            grid_container = page.locator("div[class*='captcha'], div[class*='verify'], div[class*='puzzle']")
            
            for i, (row, col) in enumerate(click_sequence):
                print(f"🖱️ 点击第 {i+1} 个格子: ({row}, {col})")
                
                # 计算格子位置（需要根据实际DOM结构调整）
                cell_selector = f"div[class*='captcha'] > div:nth-child({row * 3 + col + 1})"
                
                try:
                    # 点击格子
                    await page.click(cell_selector, timeout=5000)
                    await asyncio.sleep(0.5)  # 短暂延迟
                except Exception as e:
                    print(f"⚠️ 点击格子失败: {e}")
                    # 尝试备用选择器
                    try:
                        await page.click(f"div[class*='captcha'] div:nth-child({row * 3 + col + 1})", timeout=5000)
                        await asyncio.sleep(0.5)
                    except:
                        print(f"❌ 备用点击也失败")
                        continue
            
            # 等待验证结果
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ 执行点击序列失败: {e}")
    
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


# 全局验证码解答器实例
captcha_solver = XianyuCaptchaSolver()
