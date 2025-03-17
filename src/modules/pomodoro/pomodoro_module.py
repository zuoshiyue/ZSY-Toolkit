#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
番茄时钟模块
提供番茄工作法计时功能
"""

import logging
from typing import Optional

class PomodoroModule:
    """番茄时钟模块类"""
    
    def __init__(self, platform_adapter, config_manager):
        self.logger = logging.getLogger("左拾月.番茄时钟")
        self.platform_adapter = platform_adapter
        self.config_manager = config_manager
        
    def create_widget(self, parent):
        """创建模块UI组件
        
        Args:
            parent: 父级窗口
            
        Returns:
            PomodoroUI: 番茄时钟UI组件
        """
        from .pomodoro_ui import PomodoroUI
        return PomodoroUI(parent, self.platform_adapter, self.config_manager) 