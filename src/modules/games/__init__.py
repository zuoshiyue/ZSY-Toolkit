#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
游戏空间模块初始化
"""

from src.modules.games.sudoku.sudoku_ui import SudokuUI
from src.modules.games.minesweeper.minesweeper_ui import MinesweeperUI

__all__ = ['SudokuUI', 'MinesweeperUI']

def create_widget(parent, config_manager):
    """创建游戏空间模块的UI组件
    
    Args:
        parent: 父容器
        config_manager: 配置管理器实例
        
    Returns:
        GameSpaceUI: 游戏空间UI组件
    """
    from src.modules.games.game_space_ui import GameSpaceUI
    return GameSpaceUI(parent, config_manager) 