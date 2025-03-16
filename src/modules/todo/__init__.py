#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
Todo模块包
"""

from src.modules.todo.todo_module import TodoModule
from src.modules.todo.todo_ui import TodoUI

def create_widget(parent, config_manager, **kwargs):
    """创建Todo模块UI组件
    
    Args:
        parent: 父容器
        config_manager: 配置管理器实例
        
    Returns:
        TodoUI: Todo模块UI实例
    """
    return TodoUI(parent, config_manager, **kwargs) 