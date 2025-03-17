#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统控制模块
提供系统控制相关功能
"""

import logging
from typing import Optional

class SystemModule:
    """系统控制模块类"""
    
    def __init__(self, platform_adapter, config_manager):
        self.logger = logging.getLogger("左拾月.系统控制")
        self.platform_adapter = platform_adapter
        self.config_manager = config_manager
        
    def create_widget(self, parent):
        """创建模块UI组件
        
        Args:
            parent: 父级窗口
            
        Returns:
            SystemUI: 系统控制UI组件
        """
        from .system_ui import SystemUI
        return SystemUI(parent, self.platform_adapter, self.config_manager) 