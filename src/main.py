#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
主程序入口文件
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

# 导入核心组件
from src.core.app_manager import AppManager
from src.ui.main_window import MainWindow
from src.core.config_manager import ConfigManager
from src.core.platform_adapter import PlatformAdapter

# 配置日志
def setup_logging():
    """配置日志系统"""
    log_dir = root_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("左拾月")

def main():
    """应用程序主入口函数"""
    # 初始化日志
    logger = setup_logging()
    logger.info("左拾月启动中...")
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        
        # 初始化平台适配器
        platform_adapter = PlatformAdapter()
        logger.info(f"当前运行平台: {platform_adapter.get_platform_name()}")
        
        # 初始化应用管理器
        app_manager = AppManager(config_manager, platform_adapter)
        
        # 创建并启动主窗口
        main_window = MainWindow(app_manager)
        main_window.run()
        
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 