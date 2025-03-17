#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
应用启动器模块初始化
"""

import customtkinter as ctk
import logging
from typing import Optional

class LauncherUI(ctk.CTkFrame):
    """应用启动器UI类"""
    
    def __init__(self, master, platform_adapter, config_manager):
        super().__init__(master)
        self.logger = logging.getLogger("左拾月.应用启动器")
        self.platform_adapter = platform_adapter
        self.config_manager = config_manager
        
        # 初始化UI
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建标题
        title_label = ctk.CTkLabel(
            self,
            text="应用启动器",
            font=("微软雅黑", 24, "bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)
        
        # 创建提示信息
        info_label = ctk.CTkLabel(
            self,
            text="功能开发中...",
            font=("微软雅黑", 16)
        )
        info_label.grid(row=1, column=0, padx=20, pady=10)

def create_widget(parent, platform_adapter, config_manager):
    """创建应用启动器模块的UI组件
    
    Args:
        parent: 父容器
        platform_adapter: 平台适配器实例
        config_manager: 配置管理器实例
        
    Returns:
        LauncherUI: 应用启动器UI组件
    """
    return LauncherUI(parent, platform_adapter, config_manager) 