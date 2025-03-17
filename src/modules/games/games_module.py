#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
游戏空间模块
提供游戏启动和管理功能
"""

import logging
from typing import Optional
from .games_ui import GamesUI

class GamesModule:
    """游戏空间模块类"""
    
    def __init__(self, platform_adapter, config_manager):
        self.logger = logging.getLogger("左拾月.游戏空间")
        self.platform_adapter = platform_adapter
        self.config_manager = config_manager
        
    def create_widget(self, parent) -> Optional[GamesUI]:
        """创建UI组件"""
        try:
            return GamesUI(parent, self.platform_adapter, self.config_manager)
        except Exception as e:
            self.logger.error(f"创建游戏空间UI失败: {str(e)}")
            return None 