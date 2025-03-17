#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建左拾月应用的简单图标
生成.ico和.icns格式的图标文件
使用简单的月亮设计，不包含文字
"""

import os
import math
from PIL import Image, ImageDraw

def create_moon_icon(size, bg_color, fg_color, output_dir="src/ui/assets"):
    """创建月亮图标
    
    Args:
        size: 图标大小
        bg_color: 背景颜色
        fg_color: 前景颜色
        output_dir: 输出目录
    """
    # 创建一个正方形透明背景图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 画圆形背景
    margin = size // 20
    draw.ellipse([(margin, margin), (size - margin, size - margin)], fill=bg_color)
    
    # 添加月亮图案 - 半月形状
    moon_radius = (size - 2 * margin) // 2
    center_x, center_y = size // 2, size // 2
    
    # 绘制满月
    draw.ellipse([
        (center_x - moon_radius // 1.2, center_y - moon_radius),
        (center_x + moon_radius // 1.2, center_y + moon_radius)
    ], fill=fg_color)
    
    # 绘制覆盖的圆形，创建半月形状
    offset = size // 8
    draw.ellipse([
        (center_x - moon_radius // 1.2 + offset, center_y - moon_radius),
        (center_x + moon_radius // 1.2 + offset, center_y + moon_radius)
    ], fill=bg_color)
    
    # 数字"10"的简化表示 - 垂直线和圆形
    line_width = size // 16
    
    # 数字"1"
    draw.rectangle([
        (center_x - moon_radius // 2, center_y + moon_radius // 4),
        (center_x - moon_radius // 2 + line_width, center_y + moon_radius - line_width)
    ], fill=fg_color)
    
    # 数字"0"
    small_radius = moon_radius // 4
    draw.ellipse([
        (center_x - small_radius, center_y + moon_radius // 4),
        (center_x + small_radius, center_y + moon_radius // 4 + small_radius * 2)
    ], outline=fg_color, width=line_width // 2)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    return img

def generate_icon_files():
    """生成多种尺寸的图标，并输出为 .ico 和 .icns 文件"""
    # 定义颜色方案 - 深蓝色背景，白色前景
    bg_color = (28, 40, 65, 255)  # 深蓝色
    fg_color = (240, 240, 240, 255)  # 白色
    
    # 生成不同尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
    icons = {}
    
    for size in sizes:
        icons[size] = create_moon_icon(size, bg_color, fg_color)
    
    # 保存为 .ico 文件 (Windows)
    icons[48].save("src/ui/assets/icon.ico", format="ICO", sizes=[(s, s) for s in sizes if s <= 256])
    print("已生成 icon.ico")
    
    # 保存为 .png 文件 (用于转换为 .icns)
    png_path = "src/ui/assets/icon.png"
    icons[1024].save(png_path, format="PNG")
    print("已生成 icon.png")
    
    # 直接将PNG保存为ICNS作为备用
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
        print(f"使用 iconutil 生成 .icns 失败: {e}")

if __name__ == "__main__":
    print("开始生成简单图标...")
    generate_icon_files()
    print("图标生成完成！") 