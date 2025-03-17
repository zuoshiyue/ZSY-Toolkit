#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
游戏空间主界面实现
"""

import logging
import customtkinter as ctk
from PIL import Image, ImageTk
from pathlib import Path

from src.modules.games.sudoku.sudoku_ui import SudokuUI
from src.modules.games.minesweeper.minesweeper_ui import MinesweeperUI

class GameSpaceUI(ctk.CTkFrame):
    """游戏空间主界面类"""
    
    def __init__(self, master, config_manager, **kwargs):
        """初始化游戏空间主界面
        
        Args:
            master: 父容器
            config_manager: 配置管理器实例
        """
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger("左拾月.游戏空间")
        self.config_manager = config_manager
        
        # 数据目录
        self.data_dir = Path(config_manager.get_app_data_dir()) / "games"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前活跃的游戏界面
        self.active_game = None
        
        # 初始化UI
        self._init_ui()
        
        self.logger.info("游戏空间界面已初始化")
    
    def _init_ui(self):
        """初始化UI界面"""
        # 主界面容器
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 顶部标题区域
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="左拾月游戏空间",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # 返回按钮
        self.back_button = ctk.CTkButton(
            header_frame,
            text="返回游戏选择",
            width=120,
            command=self._show_game_selection,
            fg_color="#264653"
        )
        self.back_button.pack(side="right", padx=10)
        self.back_button.configure(state="disabled")  # 初始状态禁用
        
        # 游戏选择区域
        self.games_frame = ctk.CTkFrame(self.main_frame)
        self.games_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 游戏容器区域（初始隐藏）
        self.game_container = ctk.CTkFrame(self.main_frame)
        
        # 添加游戏卡片
        self._add_game_cards()
    
    def _add_game_cards(self):
        """添加游戏卡片"""
        # 创建卡片容器
        cards_frame = ctk.CTkFrame(self.games_frame, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        ctk.CTkLabel(
            cards_frame,
            text="选择一个游戏开始",
            font=("Helvetica", 18, "bold")
        ).pack(pady=(0, 30))
        
        # 游戏卡片区域
        game_cards = ctk.CTkFrame(cards_frame, fg_color="transparent")
        game_cards.pack(fill="both", expand=True)
        
        # 配置网格布局
        game_cards.columnconfigure(0, weight=1)
        game_cards.columnconfigure(1, weight=1)
        game_cards.rowconfigure(0, weight=1)
        
        # 数独游戏卡片
        sudoku_card = self._create_game_card(
            game_cards,
            "数独挑战",
            "三级难度、实时错误检测、提示系统",
            self._open_sudoku
        )
        sudoku_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # 扫雷游戏卡片
        minesweeper_card = self._create_game_card(
            game_cards,
            "经典扫雷",
            "初级/中级/高级难度、自定义模式、计时器",
            self._open_minesweeper
        )
        minesweeper_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    def _create_game_card(self, parent, title, description, command):
        """创建游戏卡片
        
        Args:
            parent: 父容器
            title: 游戏标题
            description: 游戏描述
            command: 点击回调函数
            
        Returns:
            CTkFrame: 创建的卡片框架
        """
        card = ctk.CTkFrame(parent)
        
        # 卡片内容
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 游戏标题
        ctk.CTkLabel(
            content_frame,
            text=title,
            font=("Helvetica", 16, "bold")
        ).pack(pady=(0, 10))
        
        # 游戏描述
        ctk.CTkLabel(
            content_frame,
            text=description,
            font=("Helvetica", 12),
            text_color="gray"
        ).pack(pady=(0, 20))
        
        # 开始按钮
        ctk.CTkButton(
            content_frame,
            text="开始游戏",
            width=120,
            height=32,
            command=command,
            fg_color="#2A9D8F"
        ).pack(pady=10)
        
        return card
    
    def _open_sudoku(self):
        """打开数独游戏"""
        self._show_game(SudokuUI, "数独挑战")
    
    def _open_minesweeper(self):
        """打开扫雷游戏"""
        self._show_game(MinesweeperUI, "经典扫雷")
    
    def _show_game(self, game_class, game_name):
        """显示游戏界面
        
        Args:
            game_class: 游戏UI类
            game_name: 游戏名称
        """
        # 隐藏游戏选择界面
        self.games_frame.pack_forget()
        
        # 清除游戏容器中的所有小部件
        for widget in self.game_container.winfo_children():
            widget.destroy()
        
        # 显示游戏容器
        self.game_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建并显示游戏
        self.active_game = game_class(
            self.game_container, 
            self.config_manager
        )
        self.active_game.pack(fill="both", expand=True)
        
        # 启用返回按钮
        self.back_button.configure(state="normal")
        
        # 调整主窗口大小以适应游戏
        self._adjust_window_size(game_name)
        
        self.logger.info(f"已加载游戏：{game_name}")
    
    def _adjust_window_size(self, game_name):
        """根据游戏类型调整窗口大小
        
        Args:
            game_name: 游戏名称
        """
        # 获取主窗口
        root = self.winfo_toplevel()
        
        # 根据游戏类型设置合适的窗口大小
        if game_name == "数独挑战":
            # 数独游戏需要较大的窗口
            new_width = 1200
            new_height = 800
        elif game_name == "经典扫雷":
            # 扫雷游戏窗口大小根据难度可能需要更大
            new_width = 1200
            new_height = 800
        else:
            # 默认大小
            new_width = 1200
            new_height = 800
        
        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # 确保窗口不会超出屏幕
        new_width = min(new_width, screen_width - 100)
        new_height = min(new_height, screen_height - 100)
        
        # 计算窗口位置，使其居中
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        
        # 设置窗口大小和位置
        root.geometry(f"{new_width}x{new_height}+{x}+{y}")
        
        self.logger.info(f"已调整窗口大小为 {new_width}x{new_height}")
    
    def _show_game_selection(self):
        """显示游戏选择界面"""
        # 隐藏游戏容器
        self.game_container.pack_forget()
        
        # 显示游戏选择界面
        self.games_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 禁用返回按钮
        self.back_button.configure(state="disabled")
        
        # 关闭当前游戏
        if self.active_game:
            if hasattr(self.active_game, 'on_close'):
                self.active_game.on_close()
            self.active_game = None
        
        # 恢复默认窗口大小
        root = self.winfo_toplevel()
        root.geometry("1200x800")
        
        self.logger.info("返回游戏选择界面")
    
    def _center_dialog(self, dialog, width, height):
        """使对话框居中于主窗口
        
        Args:
            dialog: 对话框
            width: 对话框宽度
            height: 对话框高度
        """
        # 获取主窗口
        main_window = self.winfo_toplevel()
        
        # 获取主窗口位置和大小
        main_x = main_window.winfo_x()
        main_y = main_window.winfo_y()
        main_width = main_window.winfo_width()
        main_height = main_window.winfo_height()
        
        # 计算对话框应该出现的位置（相对于主窗口居中）
        x = main_x + (main_width - width) // 2
        y = main_y + (main_height - height) // 2
        
        # 设置对话框位置
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_close(self):
        """关闭时调用"""
        # 关闭当前游戏
        if self.active_game and hasattr(self.active_game, 'on_close'):
            self.active_game.on_close()
        
        self.logger.info("游戏空间已关闭") 