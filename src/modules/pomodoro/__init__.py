#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
番茄时钟模块初始化
"""

from src.modules.pomodoro.pomodoro_ui import PomodoroUI

__all__ = ['PomodoroUI']

def create_widget(parent, platform_adapter, config_manager):
    """创建番茄时钟模块的UI组件
    
    Args:
        parent: 父容器
        platform_adapter: 平台适配器实例
        config_manager: 配置管理器实例
        
    Returns:
        PomodoroUI: 番茄时钟UI组件
    """
    return PomodoroUI(parent, platform_adapter, config_manager) 