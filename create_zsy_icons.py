#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建清晰简约的ZSY图标 - 字母分散设计
生成.ico和.icns格式的图标文件
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_zsy_icon(size, bg_color, accent_color, output_dir="src/ui/assets"):
    """创建清晰的ZSY字母图标
    
    Args:
        size: 图标大小
        bg_color: 背景颜色
        accent_color: 线条颜色
        output_dir: 输出目录
    """
    # 创建一个正方形透明背景图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 边距比例
    margin_ratio = 0.08
    margin = int(size * margin_ratio)
    
    # 绘制背景圆形 - 使用纯色
    draw.ellipse([
        (margin, margin),
        (size - margin, size - margin)
    ], fill=bg_color)
    
    # 计算中心点和工作区域
    center_x, center_y = size // 2, size // 2
    working_area = size - 2 * margin
    
    # 线条宽度 - 更细的线条
    line_width = max(2, size // 25)  # 比之前的更细
    
    # 为三个字母计算独立的区域
    letter_width = working_area // 4  # 给每个字母分配的宽度
    letter_spacing = letter_width // 2  # 字母之间的间距
    
    # Z的位置 - 左侧
    z_left = center_x - letter_width - letter_spacing
    z_top = center_y - letter_width // 2
    z_bottom = center_y + letter_width // 2
    z_width = letter_width
    
    # 绘制Z
    z_top_left = (z_left, z_top)
    z_top_right = (z_left + z_width, z_top)
    z_bottom_left = (z_left, z_bottom)
    z_bottom_right = (z_left + z_width, z_bottom)
    
    draw.line([z_top_left, z_top_right], fill=accent_color, width=line_width)
    draw.line([z_top_right, z_bottom_left], fill=accent_color, width=line_width)
    draw.line([z_bottom_left, z_bottom_right], fill=accent_color, width=line_width)
    
    # S的位置 - 中间
    s_left = center_x - letter_width // 2
    s_width = letter_width
    s_height = letter_width * 1.2
    s_top = center_y - s_height // 2
    
    # 计算S的曲线半径和位置
    s_radius = s_width // 2.5
    s_top_center_x = s_left + s_width // 2
    s_top_center_y = s_top + s_radius
    s_bottom_center_x = s_left + s_width // 2
    s_bottom_center_y = s_top + s_height - s_radius
    
    # 绘制S的两个半圆
    draw.arc([
        s_top_center_x - s_radius, s_top_center_y - s_radius,
        s_top_center_x + s_radius, s_top_center_y + s_radius
    ], 180, 0, fill=accent_color, width=line_width)
    
    draw.arc([
        s_bottom_center_x - s_radius, s_bottom_center_y - s_radius,
        s_bottom_center_x + s_radius, s_bottom_center_y + s_radius
    ], 0, 180, fill=accent_color, width=line_width)
    
    # 连接S的两个半圆
    mid_y = (s_top_center_y + s_radius + s_bottom_center_y - s_radius) // 2
    draw.line([
        (s_top_center_x + s_radius, s_top_center_y),
        (s_bottom_center_x - s_radius, s_bottom_center_y)
    ], fill=accent_color, width=line_width)
    
    # Y的位置 - 右侧
    y_left = center_x + letter_spacing
    y_width = letter_width
    y_height = letter_width * 1.2
    y_top = center_y - y_height // 2
    
    # Y的分叉点
    y_fork_x = y_left + y_width // 2
    y_fork_y = y_top + y_height * 0.4
    
    # 绘制Y
    draw.line([
        (y_left, y_top),
        (y_fork_x, y_fork_y)
    ], fill=accent_color, width=line_width)
    
    draw.line([
        (y_left + y_width, y_top),
        (y_fork_x, y_fork_y)
    ], fill=accent_color, width=line_width)
    
    draw.line([
        (y_fork_x, y_fork_y),
        (y_fork_x, y_top + y_height)
    ], fill=accent_color, width=line_width)
    
    # 添加非常轻微的高光 - 只为macOS版本
    if size >= 128:
        highlight = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight)
        
        # 上部高光很轻微
        highlight_draw.ellipse([
            (margin + line_width, margin + line_width),
            (size - margin - line_width, center_y)
        ], fill=(255, 255, 255, 10))  # 非常透明的白色
        
        # 轻微的边缘增强
        img.paste(highlight, (0, 0), highlight)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    return img

def generate_icon_files():
    """生成多种尺寸的图标，并输出为 .ico 和 .icns 文件"""
    # 使用浅色系配色方案
    bg_color = (220, 235, 250, 255)  # 非常浅的蓝色
    accent_color = (70, 110, 170, 255)  # 适中的蓝色 - 不要太深，保持清晰
    
    # 生成不同尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
    icons = {}
    
    for size in sizes:
        icons[size] = create_zsy_icon(size, bg_color, accent_color)
    
    # 保存为 .ico 文件 (Windows)
    icons[48].save("src/ui/assets/icon.ico", format="ICO", sizes=[(s, s) for s in sizes if s <= 256])
    print("已生成 icon.ico")
    
    # 保存为 .png 文件
    png_path = "src/ui/assets/icon.png"
    icons[1024].save(png_path, format="PNG")
    print("已生成 icon.png")
    
    # 保存为 .icns 文件
    icons[1024].save("src/ui/assets/icon.icns", format="PNG")
    print("已生成 icon.icns (PNG格式)")
    
    # 尝试使用 iconutil 将 .iconset 转换为 .icns (macOS)
    try:
        # 创建 .iconset 目录
        iconset_dir = "src/ui/assets/icon.iconset"
        os.makedirs(iconset_dir, exist_ok=True)
        
        # 保存不同尺寸的图标到 .iconset 目录
        for size in [16, 32, 128, 256, 512]:
            icons[size].save(f"{iconset_dir}/icon_{size}x{size}.png", format="PNG")
            if size < 512:  # 添加 @2x 版本
                icons[size*2].save(f"{iconset_dir}/icon_{size}x{size}@2x.png", format="PNG")
        
        # 使用 iconutil 转换为 .icns (仅macOS系统可用)
        os.system(f"iconutil -c icns {iconset_dir}")
        print("已使用 iconutil 生成 icon.icns")
    except Exception as e:
        print(f"使用 iconutil 生成 .icns 失败: {e}，使用PNG格式作为备用")

if __name__ == "__main__":
    print("开始生成清晰分散的ZSY图标...")
    generate_icon_files()
    print("图标生成完成！") 