#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建左拾月应用的图标
生成.ico和.icns格式的图标文件
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_circle_icon(size, bg_color, fg_color, text="左拾月", output_dir="src/ui/assets"):
    """创建圆形图标
    
    Args:
        size: 图标大小
        bg_color: 背景颜色
        fg_color: 前景颜色
        text: 图标文字
        output_dir: 输出目录
    """
    # 创建一个正方形透明背景图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 画圆形背景
    margin = size // 20
    draw.ellipse([(margin, margin), (size - margin, size - margin)], fill=bg_color)
    
    # 添加月亮图案
    moon_radius = (size - 2 * margin) // 2 - size // 10
    center_x, center_y = size // 2, size // 2
    offset = size // 12
    
    # 绘制月亮
    for angle in range(0, 360, 1):
        rad = math.radians(angle)
        x = center_x + offset + int(moon_radius * math.cos(rad))
        y = center_y + int(moon_radius * math.sin(rad))
        
        # 在右侧画月亮暗部
        if x > center_x + offset // 2:
            continue
        
        # 画月亮亮部像素点
        r = size // 60
        draw.ellipse([(x-r, y-r), (x+r, y+r)], fill=fg_color)
    
    # 添加文字
    try:
        font_size = size // 4
        try:
            # 尝试加载中文字体
            font = ImageFont.truetype("Microsoft YaHei", font_size)
        except:
            try:
                # macOS中文字体
                font = ImageFont.truetype("PingFang SC", font_size)
            except:
                # 回退到默认字体
                font = ImageFont.load_default()
        
        # 获取文字尺寸
        text_width = draw.textlength(text, font=font)
        text_height = font_size
        
        # 文字位置 - 居中偏下
        text_x = (size - text_width) // 2
        text_y = center_y + moon_radius // 2
        
        # 绘制文字
        draw.text((text_x, text_y), text, font=font, fill=fg_color)
    except Exception as e:
        print(f"添加文字时出错: {e}")
    
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
        icons[size] = create_circle_icon(size, bg_color, fg_color)
    
    # 保存为 .ico 文件 (Windows)
    icons[48].save("src/ui/assets/icon.ico", format="ICO", sizes=[(s, s) for s in sizes if s <= 256])
    print("已生成 icon.ico")
    
    # 保存为 .png 文件 (用于转换为 .icns)
    png_path = "src/ui/assets/icon.png"
    icons[1024].save(png_path, format="PNG")
    print("已生成 icon.png")
    
    # 方法1：尝试使用 iconutil 将 .iconset 转换为 .icns (macOS)
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
        print("将直接使用 .png 文件作为图标")
        # 复制一份 PNG 图标作为备用
        icons[1024].save("src/ui/assets/icon.icns", format="PNG")

if __name__ == "__main__":
    print("开始生成图标...")
    generate_icon_files()
    print("图标生成完成！") 