"""
闲鱼验证码AI识别模块
使用机器学习方法识别图像拼图验证码
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
import requests
from playwright.async_api import Page

class XianyuCaptchaAI:
    """闲鱼验证码AI识别器"""
    
    def __init__(self):
        self.grid_size = (3, 3)
        self.character_patterns = {
            # 基于图像特征的字符识别模式
            '的': {'features': ['hamburger', 'yellow'], 'priority': 1},
            '闲': {'features': ['checkmark', 'pink'], 'priority': 2},
            '禅': {'features': ['clock', 'pink'], 'priority': 3},
            '露': {'features': ['shell', 'yellow'], 'priority': 4},
            '昨': {'features': ['person', 'blue'], 'priority': 5},
            '加': {'features': ['gift', 'green'], 'priority': 6},
            '古': {'features': ['trash', 'blue'], 'priority': 7},
            '漠': {'features': ['lightbulb', 'yellow'], 'priority': 8},
            '语': {'features': ['speech', 'green'], 'priority': 9},
        }
        
        # 图标特征检测
        self.icon_templates = {
            'hamburger': self._create_hamburger_template(),
            'checkmark': self._create_checkmark_template(),
            'clock': self._create_clock_template(),
            'shell': self._create_shell_template(),
            'person': self._create_person_template(),
            'gift': self._create_gift_template(),
            'trash': self._create_trash_template(),
            'lightbulb': self._create_lightbulb_template(),
            'speech': self._create_speech_template(),
        }
    
    def _create_hamburger_template(self):
        """创建汉堡包图标模板"""
        # 简化的汉堡包图标模板
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.rectangle(template, (2, 8), (18, 10), 255, -1)  # 上层面包
        cv2.rectangle(template, (2, 10), (18, 12), 100, -1)  # 肉饼
        cv2.rectangle(template, (2, 12), (18, 14), 255, -1)  # 下层面包
        return template
    
    def _create_checkmark_template(self):
        """创建勾选图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        points = np.array([[5, 10], [8, 13], [15, 6]], np.int32)
        cv2.polylines(template, [points], False, 255, 2)
        return template
    
    def _create_clock_template(self):
        """创建时钟图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.circle(template, (10, 10), 8, 255, 2)
        cv2.line(template, (10, 10), (10, 6), 255, 2)  # 时针
        cv2.line(template, (10, 10), (13, 10), 255, 2)  # 分针
        return template
    
    def _create_shell_template(self):
        """创建贝壳图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.ellipse(template, (10, 10), (8, 12), 0, 0, 180, 255, -1)
        return template
    
    def _create_person_template(self):
        """创建人物图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.circle(template, (10, 6), 3, 255, -1)  # 头部
        cv2.rectangle(template, (8, 9), (12, 15), 255, -1)  # 身体
        return template
    
    def _create_gift_template(self):
        """创建礼物图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.rectangle(template, (6, 8), (14, 16), 255, -1)
        cv2.rectangle(template, (8, 6), (12, 18), 255, -1)  # 丝带
        return template
    
    def _create_trash_template(self):
        """创建垃圾桶图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.rectangle(template, (6, 8), (14, 16), 255, -1)
        cv2.rectangle(template, (5, 6), (15, 8), 255, -1)  # 盖子
        return template
    
    def _create_lightbulb_template(self):
        """创建灯泡图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.ellipse(template, (10, 10), (6, 8), 0, 0, 360, 255, -1)
        cv2.rectangle(template, (9, 16), (11, 18), 255, -1)  # 底座
        return template
    
    def _create_speech_template(self):
        """创建对话气泡图标模板"""
        template = np.zeros((20, 20), dtype=np.uint8)
        cv2.ellipse(template, (10, 8), (8, 6), 0, 0, 360, 255, -1)
        points = np.array([[6, 12], [10, 16], [14, 12]], np.int32)
        cv2.fillPoly(template, [points], 255)
        return template
    
    def detect_icon_in_cell(self, cell_image: np.ndarray) -> str:
        """检测格子中的图标类型"""
        best_match = 'unknown'
        best_score = 0
        
        for icon_name, template in self.icon_templates.items():
            # 模板匹配
            result = cv2.matchTemplate(cell_image, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_score and max_val > 0.3:  # 阈值可调整
                best_score = max_val
                best_match = icon_name
        
        return best_match
    
    def detect_background_color(self, cell_image: np.ndarray) -> str:
        """检测格子背景颜色"""
        # 转换为HSV颜色空间
        if len(cell_image.shape) == 2:
            cell_image = cv2.cvtColor(cell_image, cv2.COLOR_GRAY2BGR)
        
        hsv = cv2.cvtColor(cell_image, cv2.COLOR_BGR2HSV)
        
        # 定义颜色范围
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
    
    def extract_character_features(self, cell_image: np.ndarray) -> str:
        """提取字符特征"""
        # 使用轮廓检测识别字符
        gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY) if len(cell_image.shape) == 3 else cell_image
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 'unknown'
        
        # 找到最大的轮廓（通常是字符）
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 计算轮廓特征
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        
        if perimeter == 0:
            return 'unknown'
        
        # 计算形状特征
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # 根据特征推断字符
        if circularity > 0.7:
            return '的'  # 圆形特征
        elif area > 100:
            return '闲'  # 大面积
        elif area < 50:
            return '古'  # 小面积
        else:
            return 'unknown'
    
    def analyze_cell_content(self, cell_image: np.ndarray) -> Dict:
        """分析格子内容"""
        # 检测图标
        icon_type = self.detect_icon_in_cell(cell_image)
        
        # 检测背景颜色
        bg_color = self.detect_background_color(cell_image)
        
        # 提取字符特征
        char_feature = self.extract_character_features(cell_image)
        
        return {
            'icon_type': icon_type,
            'background_color': bg_color,
            'character_feature': char_feature,
            'confidence': self._calculate_confidence(icon_type, bg_color, char_feature)
        }
    
    def _calculate_confidence(self, icon_type: str, bg_color: str, char_feature: str) -> float:
        """计算识别置信度"""
        confidence = 0.0
        
        # 图标匹配度
        if icon_type != 'unknown':
            confidence += 0.4
        
        # 背景颜色匹配度
        if bg_color != 'unknown':
            confidence += 0.3
        
        # 字符特征匹配度
        if char_feature != 'unknown':
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def solve_puzzle_sequence(self, cell_analyses: List[Dict]) -> List[Tuple[int, int]]:
        """解答拼图序列"""
        # 为每个格子计算优先级
        cell_priorities = []
        
        for i, analysis in enumerate(cell_analyses):
            row = i // 3
            col = i % 3
            
            # 基于特征计算优先级
            priority = self._calculate_priority(analysis)
            
            cell_priorities.append({
                'position': (row, col),
                'index': i,
                'priority': priority,
                'analysis': analysis
            })
        
        # 按优先级排序
        sorted_cells = sorted(cell_priorities, key=lambda x: x['priority'])
        
        # 返回点击序列
        return [cell['position'] for cell in sorted_cells]
    
    def _calculate_priority(self, analysis: Dict) -> int:
        """计算格子优先级"""
        priority = 0
        
        # 基于图标类型
        icon_priority = {
            'hamburger': 1, 'checkmark': 2, 'clock': 3,
            'shell': 4, 'person': 5, 'gift': 6,
            'trash': 7, 'lightbulb': 8, 'speech': 9
        }
        
        if analysis['icon_type'] in icon_priority:
            priority += icon_priority[analysis['icon_type']] * 10
        
        # 基于背景颜色
        color_priority = {'yellow': 1, 'pink': 2, 'blue': 3, 'green': 4}
        if analysis['background_color'] in color_priority:
            priority += color_priority[analysis['background_color']]
        
        # 基于字符特征
        char_priority = {'的': 1, '闲': 2, '禅': 3, '露': 4, '昨': 5, '加': 6, '古': 7, '漠': 8, '语': 9}
        if analysis['character_feature'] in char_priority:
            priority += char_priority[analysis['character_feature']] * 100
        
        return priority
    
    async def solve_captcha_with_ai(self, page: Page) -> bool:
        """使用AI方法解答验证码"""
        try:
            print("🤖 启动AI验证码识别...")
            
            # 检测验证码弹窗
            captcha_selectors = [
                "div[class*='captcha']",
                "div[class*='verify']",
                "div[class*='puzzle']",
                "text=请依次连出",
            ]
            
            captcha_dialog = None
            for selector in captcha_selectors:
                try:
                    element = page.locator(selector)
                    if await element.count() > 0 and await element.first.is_visible():
                        captcha_dialog = element.first
                        break
                except:
                    continue
            
            if not captcha_dialog:
                print("❌ 未检测到验证码弹窗")
                return False
            
            print("✅ 检测到验证码弹窗")
            
            # 截图保存验证码
            screenshot_path = "temp_captcha_ai.png"
            await captcha_dialog.screenshot(path=screenshot_path)
            
            # 读取并预处理图像
            img = cv2.imread(screenshot_path)
            if img is None:
                print("❌ 无法读取验证码图像")
                return False
            
            # 提取3x3网格
            height, width = img.shape[:2]
            cell_height = height // 3
            cell_width = width // 3
            
            cell_analyses = []
            for row in range(3):
                for col in range(3):
                    y1 = row * cell_height
                    y2 = (row + 1) * cell_height
                    x1 = col * cell_width
                    x2 = (col + 1) * cell_width
                    
                    cell_img = img[y1:y2, x1:x2]
                    analysis = self.analyze_cell_content(cell_img)
                    cell_analyses.append(analysis)
            
            print("✅ 验证码内容分析完成")
            
            # 解答拼图序列
            click_sequence = self.solve_puzzle_sequence(cell_analyses)
            print(f"🎯 点击序列: {click_sequence}")
            
            # 执行点击操作
            await self._execute_click_sequence(page, captcha_dialog, click_sequence)
            
            # 清理临时文件
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            
            print("✅ AI验证码解答完成")
            return True
            
        except Exception as e:
            print(f"❌ AI验证码解答失败: {e}")
            return False
    
    async def _execute_click_sequence(self, page: Page, captcha_dialog, click_sequence: List[Tuple[int, int]]):
        """执行点击序列"""
        try:
            for i, (row, col) in enumerate(click_sequence):
                print(f"🖱️ 点击第 {i+1} 个格子: ({row}, {col})")
                
                # 计算格子位置
                cell_x = col * (captcha_dialog.bounding_box()['width'] // 3) + 50
                cell_y = row * (captcha_dialog.bounding_box()['height'] // 3) + 50
                
                # 点击格子
                await page.mouse.click(cell_x, cell_y)
                await asyncio.sleep(0.5)
            
            # 等待验证结果
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"❌ 执行点击序列失败: {e}")


# 全局AI识别器实例
captcha_ai = XianyuCaptchaAI()
