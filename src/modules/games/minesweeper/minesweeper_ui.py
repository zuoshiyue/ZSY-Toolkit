#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
扫雷游戏界面实现
"""

import logging
import time
import threading
from typing import List, Tuple, Dict, Any, Optional

import customtkinter as ctk
from PIL import Image, ImageTk

from src.modules.games.minesweeper.minesweeper_module import (
    MinesweeperModule, MinesweeperDifficulty, CellState, GameState
)

class MinesweeperUI(ctk.CTkFrame):
    """扫雷游戏UI类"""
    
    def __init__(self, master, config_manager, **kwargs):
        """初始化扫雷游戏UI
        
        Args:
            master: 父容器
            config_manager: 配置管理器实例
        """
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger("左拾月.扫雷游戏UI")
        self.config_manager = config_manager
        
        # 初始化游戏模块
        self.minesweeper_module = MinesweeperModule()
        
        # 单元格尺寸
        self.cell_size = 30
        
        # 游戏状态
        self.game_time = 0
        self.timer_running = False
        self.timer_thread = None
        self.stop_timer = threading.Event()
        
        # 初始化UI
        self._init_ui()
        
        # 默认启动新游戏
        self._new_game()
        
        self.logger.info("扫雷游戏UI已初始化")
    
    def _init_ui(self):
        """初始化UI界面"""
        # 主容器
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 顶部信息区域
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        # 左侧：难度选择
        difficulty_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        difficulty_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            difficulty_frame,
            text="难度:",
            font=("Helvetica", 14)
        ).pack(side="left", padx=(0, 10))
        
        difficulty_var = ctk.StringVar(value="初级")
        self.difficulty_menu = ctk.CTkOptionMenu(
            difficulty_frame,
            values=["初级", "中级", "高级", "自定义"],
            variable=difficulty_var,
            width=80,
            command=self._change_difficulty
        )
        self.difficulty_menu.pack(side="left")
        
        # 中间：计数器
        counter_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        counter_frame.pack(side="left", expand=True)
        
        mines_frame = ctk.CTkFrame(counter_frame, fg_color="transparent")
        mines_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(
            mines_frame,
            text="地雷:",
            font=("Helvetica", 14)
        ).pack(side="left", padx=(0, 5))
        
        self.mines_label = ctk.CTkLabel(
            mines_frame,
            text="10",
            font=("Helvetica", 14, "bold")
        )
        self.mines_label.pack(side="left")
        
        time_frame = ctk.CTkFrame(counter_frame, fg_color="transparent")
        time_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(
            time_frame,
            text="时间:",
            font=("Helvetica", 14)
        ).pack(side="left", padx=(0, 5))
        
        self.timer_label = ctk.CTkLabel(
            time_frame,
            text="000",
            font=("Helvetica", 14, "bold")
        )
        self.timer_label.pack(side="left")
        
        # 右侧：新游戏按钮
        button_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=10)
        
        self.new_game_button = ctk.CTkButton(
            button_frame,
            text="新游戏",
            width=100,
            command=self._new_game,
            fg_color="#2A9D8F"
        )
        self.new_game_button.pack(side="right")
        
        # 游戏区域（带滚动条）
        game_container = ctk.CTkFrame(main_frame)
        game_container.pack(fill="both", expand=True)
        
        # 创建滚动区域
        self.scrollable_frame = ctk.CTkScrollableFrame(
            game_container,
            label_text="",
            label_fg_color="transparent"
        )
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # 创建游戏棋盘容器
        self.board_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.board_frame.pack(expand=True, padx=10, pady=10)
        
        # 底部状态栏
        status_frame = ctk.CTkFrame(main_frame, height=30)
        status_frame.pack(fill="x", pady=(20, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="左键点击揭开格子，右键标记地雷",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=5)
    
    def _create_board(self):
        """创建扫雷棋盘"""
        # 清除现有棋盘
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        # 获取棋盘尺寸
        rows = self.minesweeper_module.rows
        cols = self.minesweeper_module.cols
        
        # 调整单元格大小，确保大棋盘也能显示
        if cols > 16:
            self.cell_size = 25
        else:
            self.cell_size = 30
        
        # 创建单元格
        self.cell_buttons = []
        for i in range(rows):
            row_buttons = []
            for j in range(cols):
                cell_frame = ctk.CTkFrame(
                    self.board_frame,
                    width=self.cell_size,
                    height=self.cell_size,
                    fg_color="#E0E0E0",
                    border_width=1,
                    border_color="#808080"
                )
                cell_frame.grid(row=i, column=j, padx=1, pady=1)
                cell_frame.grid_propagate(False)
                
                # 确保单元格大小固定
                cell_frame.columnconfigure(0, weight=1)
                cell_frame.rowconfigure(0, weight=1)
                
                # 创建单元格按钮
                cell_button = ctk.CTkButton(
                    cell_frame,
                    text="",
                    width=self.cell_size,
                    height=self.cell_size,
                    fg_color="#CCCCCC",
                    hover_color="#BBBBBB",
                    text_color="black",
                    corner_radius=0,
                    font=("Helvetica", 12, "bold"),
                    border_width=1,
                    border_color="#808080"
                )
                cell_button.grid(row=0, column=0, sticky="nsew")
                
                # 绑定鼠标事件
                cell_button.bind("<Button-1>", lambda e, r=i, c=j: self._on_left_click(r, c))
                cell_button.bind("<Button-3>", lambda e, r=i, c=j: self._on_right_click(r, c))
                cell_button.bind("<Button-2>", lambda e, r=i, c=j: self._on_middle_click(r, c))
                
                row_buttons.append(cell_button)
            self.cell_buttons.append(row_buttons)
        
        # 更新地雷计数
        self._update_mine_counter()
    
    def _on_left_click(self, row, col):
        """响应左键点击
        
        Args:
            row: 行坐标
            col: 列坐标
        """
        # 如果游戏未开始，启动计时器
        if self.minesweeper_module.game_state == GameState.NOT_STARTED:
            self._start_timer()
        
        # 揭开单元格
        success, revealed_cells, hit_mine = self.minesweeper_module.reveal_cell(row, col)
        
        if success:
            # 更新界面
            for r, c, value in revealed_cells:
                self._update_cell_display(r, c, value)
            
            # 如果触发地雷，显示所有地雷
            if hit_mine:
                self._game_over(False)
            
            # 如果获胜，显示胜利
            if self.minesweeper_module.game_state == GameState.WON:
                self._game_over(True)
    
    def _on_right_click(self, row, col):
        """响应右键点击
        
        Args:
            row: 行坐标
            col: 列坐标
        """
        # 如果游戏未开始，不响应
        if self.minesweeper_module.game_state == GameState.NOT_STARTED:
            return
        
        # 切换标记
        success, new_state = self.minesweeper_module.toggle_flag(row, col)
        
        if success:
            # 更新界面
            cell_button = self.cell_buttons[row][col]
            
            if new_state == CellState.FLAGGED:
                cell_button.configure(text="🚩", fg_color="#FF5252", text_color="white")
            elif new_state == CellState.QUESTION:
                cell_button.configure(text="?", fg_color="#CCCCCC", text_color="black")
            else:  # COVERED
                cell_button.configure(text="", fg_color="#CCCCCC", text_color="black")
            
            # 更新地雷计数
            self._update_mine_counter()
    
    def _on_middle_click(self, row, col):
        """响应中键点击
        
        Args:
            row: 行坐标
            col: 列坐标
        """
        # 如果游戏未开始，不响应
        if self.minesweeper_module.game_state == GameState.NOT_STARTED:
            return
        
        # 执行和弦操作
        success, revealed_cells, hit_mine = self.minesweeper_module.chord(row, col)
        
        if success:
            # 更新界面
            for r, c, value in revealed_cells:
                self._update_cell_display(r, c, value)
            
            # 如果触发地雷，显示所有地雷
            if hit_mine:
                self._game_over(False)
            
            # 如果获胜，显示胜利
            if self.minesweeper_module.game_state == GameState.WON:
                self._game_over(True)
    
    def _update_cell_display(self, row, col, value):
        """更新单元格显示
        
        Args:
            row: 行坐标
            col: 列坐标
            value: 单元格值
        """
        cell_button = self.cell_buttons[row][col]
        
        # 地雷
        if value == -1:
            cell_button.configure(text="💣", fg_color="#FF5252", text_color="black")
            return
        
        # 空白单元格
        if value == 0:
            cell_button.configure(text="", fg_color="#EEEEEE", text_color="black")
            return
        
        # 数字单元格
        text_colors = [
            "",           # 0: 空白
            "#0000FF",    # 1: 蓝色
            "#008000",    # 2: 绿色
            "#FF0000",    # 3: 红色
            "#000080",    # 4: 深蓝色
            "#800000",    # 5: 深红色
            "#008080",    # 6: 青色
            "#000000",    # 7: 黑色
            "#808080"     # 8: 灰色
        ]
        
        cell_button.configure(
            text=str(value),
            fg_color="#EEEEEE",
            text_color=text_colors[value]
        )
    
    def _game_over(self, win):
        """游戏结束
        
        Args:
            win: 是否获胜
        """
        # 停止计时器
        self._stop_timer()
        
        # 如果失败，显示所有地雷
        if not win:
            mines = self.minesweeper_module.get_all_mines()
            for row, col in mines:
                if self.minesweeper_module.get_cell_state(row, col)["state"] != CellState.FLAGGED:
                    self.cell_buttons[row][col].configure(text="💣", fg_color="#FF5252", text_color="black")
        
        # 显示游戏结束对话框
        self._show_game_over_dialog(win)
    
    def _show_game_over_dialog(self, win):
        """显示游戏结束对话框
        
        Args:
            win: 是否获胜
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("游戏结束")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # 使对话框居中于主窗口
        self._center_dialog(dialog, 300, 200)
        
        # 标题
        title_text = "恭喜！你赢了" if win else "很遗憾！你输了"
        title_color = "#2A9D8F" if win else "#E76F51"
        
        ctk.CTkLabel(
            dialog,
            text=title_text,
            font=("Helvetica", 18, "bold"),
            text_color=title_color
        ).pack(pady=(20, 10))
        
        # 游戏信息
        info_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        info_frame.pack(pady=10)
        
        difficulty_map = {
            MinesweeperDifficulty.BEGINNER: "初级",
            MinesweeperDifficulty.INTERMEDIATE: "中级",
            MinesweeperDifficulty.EXPERT: "高级",
            MinesweeperDifficulty.CUSTOM: "自定义"
        }
        
        difficulty = difficulty_map[self.minesweeper_module.current_difficulty]
        board_size = f"{self.minesweeper_module.rows}x{self.minesweeper_module.cols}"
        mines = self.minesweeper_module.mine_count
        
        ctk.CTkLabel(
            info_frame,
            text=f"难度: {difficulty} ({board_size}, {mines}颗地雷)",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(
            info_frame,
            text=f"用时: {self.game_time}秒",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=2)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="关闭",
            width=80,
            command=dialog.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="新游戏",
            width=80,
            fg_color="#2A9D8F",
            command=lambda: [dialog.destroy(), self._new_game()]
        ).pack(side="left", padx=10)
    
    def _new_game(self):
        """开始新游戏"""
        # 获取当前难度
        difficulty_text = self.difficulty_menu.get()
        
        if difficulty_text == "自定义":
            self._show_custom_dialog()
            return
        
        # 映射难度
        difficulty_map = {
            "初级": MinesweeperDifficulty.BEGINNER,
            "中级": MinesweeperDifficulty.INTERMEDIATE,
            "高级": MinesweeperDifficulty.EXPERT
        }
        
        difficulty = difficulty_map[difficulty_text]
        
        # 开始新游戏
        self.minesweeper_module.new_game(difficulty)
        
        # 重置计时器
        self._reset_timer()
        
        # 创建棋盘
        self._create_board()
        
        # 调整窗口大小
        self._adjust_window_size()
        
        # 更新状态
        self.status_label.configure(text=f"开始新游戏，难度：{difficulty_text}")
    
    def _show_custom_dialog(self):
        """显示自定义游戏对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("自定义游戏")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # 使对话框居中于主窗口
        self._center_dialog(dialog, 300, 200)
        
        # 标题
        ctk.CTkLabel(
            dialog,
            text="自定义游戏设置",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(20, 10))
        
        # 设置项
        settings_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        settings_frame.pack(pady=10)
        
        # 行
        row_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            row_frame,
            text="行数:",
            width=60
        ).pack(side="left", padx=(0, 10))
        
        row_var = ctk.StringVar(value="16")
        row_entry = ctk.CTkEntry(
            row_frame,
            width=60,
            textvariable=row_var
        )
        row_entry.pack(side="left")
        
        # 列
        col_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        col_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            col_frame,
            text="列数:",
            width=60
        ).pack(side="left", padx=(0, 10))
        
        col_var = ctk.StringVar(value="16")
        col_entry = ctk.CTkEntry(
            col_frame,
            width=60,
            textvariable=col_var
        )
        col_entry.pack(side="left")
        
        # 地雷数
        mines_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        mines_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(
            mines_frame,
            text="地雷数:",
            width=60
        ).pack(side="left", padx=(0, 10))
        
        mines_var = ctk.StringVar(value="40")
        mines_entry = ctk.CTkEntry(
            mines_frame,
            width=60,
            textvariable=mines_var
        )
        mines_entry.pack(side="left")
        
        # 按钮区域
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="取消",
            width=80,
            command=dialog.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="开始",
            width=80,
            fg_color="#2A9D8F",
            command=lambda: self._start_custom_game(dialog, row_var.get(), col_var.get(), mines_var.get())
        ).pack(side="left", padx=10)
    
    def _start_custom_game(self, dialog, rows_str, cols_str, mines_str):
        """开始自定义游戏
        
        Args:
            dialog: 对话框
            rows_str: 行数字符串
            cols_str: 列数字符串
            mines_str: 地雷数字符串
        """
        try:
            rows = int(rows_str)
            cols = int(cols_str)
            mines = int(mines_str)
            
            # 验证输入
            if not (5 <= rows <= 30):
                self._show_error_message(dialog, "行数必须在5到30之间")
                return
            
            if not (5 <= cols <= 30):
                self._show_error_message(dialog, "列数必须在5到30之间")
                return
            
            max_mines = (rows * cols) // 3
            if not (1 <= mines <= max_mines):
                self._show_error_message(dialog, f"地雷数必须在1到{max_mines}之间")
                return
            
            # 配置自定义游戏
            custom_config = {
                "rows": rows,
                "cols": cols,
                "mines": mines
            }
            
            # 开始新游戏
            self.minesweeper_module.new_game(MinesweeperDifficulty.CUSTOM, custom_config)
            
            # 重置计时器
            self._reset_timer()
            
            # 创建棋盘
            self._create_board()
            
            # 调整窗口大小
            self._adjust_window_size()
            
            # 更新状态
            self.status_label.configure(text=f"开始自定义游戏 ({rows}x{cols}, {mines}颗地雷)")
            
            # 关闭对话框
            dialog.destroy()
            
        except ValueError:
            self._show_error_message(dialog, "请输入有效的数字")
    
    def _show_error_message(self, parent, message):
        """显示错误消息
        
        Args:
            parent: 父窗口
            message: 错误消息
        """
        error_dialog = ctk.CTkToplevel(parent)
        error_dialog.title("错误")
        error_dialog.geometry("300x120")
        error_dialog.resizable(False, False)
        error_dialog.grab_set()
        
        # 使对话框居中于主窗口
        self._center_dialog(error_dialog, 300, 120)
        
        ctk.CTkLabel(
            error_dialog,
            text=message,
            font=("Helvetica", 14)
        ).pack(pady=(30, 15))
        
        ctk.CTkButton(
            error_dialog,
            text="确定",
            width=80,
            command=error_dialog.destroy
        ).pack(pady=10)
    
    def _change_difficulty(self, difficulty_text):
        """改变游戏难度
        
        Args:
            difficulty_text: 难度文本
        """
        # 询问是否开始新游戏
        message_box = ctk.CTkToplevel(self)
        message_box.title("开始新游戏")
        message_box.geometry("300x150")
        message_box.resizable(False, False)
        message_box.lift()
        message_box.grab_set()
        
        # 使对话框居中于主窗口
        self._center_dialog(message_box, 300, 150)
        
        ctk.CTkLabel(
            message_box,
            text=f"是否开始新的{difficulty_text}难度游戏？",
            font=("Helvetica", 14)
        ).pack(pady=(20, 10))
        
        button_frame = ctk.CTkFrame(message_box, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # 取消按钮
        ctk.CTkButton(
            button_frame,
            text="取消",
            width=80,
            command=message_box.destroy
        ).pack(side="left", padx=10)
        
        # 确认按钮
        ctk.CTkButton(
            button_frame,
            text="确认",
            width=80,
            fg_color="#2A9D8F",
            command=lambda: self._confirm_new_game(message_box)
        ).pack(side="left", padx=10)
    
    def _confirm_new_game(self, dialog):
        """确认开始新游戏
        
        Args:
            dialog: 对话框
        """
        dialog.destroy()
        self._new_game()
        
        # 调整窗口大小以适应游戏难度
        self._adjust_window_size()
    
    def _adjust_window_size(self):
        """根据游戏难度调整窗口大小"""
        # 获取游戏空间UI
        game_space = self.winfo_toplevel()
        
        # 根据难度调整窗口大小
        difficulty = self.minesweeper_module.current_difficulty
        
        if difficulty == MinesweeperDifficulty.BEGINNER:
            # 初级难度 (9x9)
            new_width = 1200
            new_height = 800
        elif difficulty == MinesweeperDifficulty.INTERMEDIATE:
            # 中级难度 (16x16)
            new_width = 1200
            new_height = 800
        elif difficulty == MinesweeperDifficulty.EXPERT:
            # 高级难度 (16x30)
            new_width = 1300
            new_height = 800
        elif difficulty == MinesweeperDifficulty.CUSTOM:
            # 自定义难度，根据行列数计算
            rows = self.minesweeper_module.rows
            cols = self.minesweeper_module.cols
            
            # 基础大小
            new_width = 1200 + (cols - 16) * 15
            new_height = 800 + (rows - 16) * 15
            
            # 限制最大尺寸
            new_width = min(new_width, 1500)
            new_height = min(new_height, 900)
        else:
            # 默认大小
            new_width = 1200
            new_height = 800
        
        # 获取屏幕尺寸
        screen_width = game_space.winfo_screenwidth()
        screen_height = game_space.winfo_screenheight()
        
        # 确保窗口不会超出屏幕
        new_width = min(new_width, screen_width - 100)
        new_height = min(new_height, screen_height - 100)
        
        # 计算窗口位置，使其居中
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        
        # 设置窗口大小和位置
        game_space.geometry(f"{new_width}x{new_height}+{x}+{y}")
        
        self.logger.info(f"已调整窗口大小为 {new_width}x{new_height}")
    
    def _update_mine_counter(self):
        """更新地雷计数器"""
        remaining = self.minesweeper_module.mine_count - self.minesweeper_module.flagged_count
        self.mines_label.configure(text=str(remaining))
    
    def _start_timer(self):
        """启动计时器"""
        self.timer_running = True
        self.stop_timer.clear()
        
        # 创建并启动计时器线程
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
    
    def _stop_timer(self):
        """停止计时器"""
        self.timer_running = False
        self.stop_timer.set()
        
        if self.timer_thread:
            self.timer_thread.join(timeout=1.0)
    
    def _reset_timer(self):
        """重置计时器"""
        self._stop_timer()
        self.game_time = 0
        self.timer_label.configure(text="000")
    
    def _timer_loop(self):
        """计时器循环"""
        start_time = time.time()
        
        while self.timer_running and not self.stop_timer.is_set():
            # 每0.5秒更新一次
            time.sleep(0.5)
            
            # 计算经过的时间
            self.game_time = int(time.time() - start_time)
            
            # 限制显示最大为999
            display_time = min(self.game_time, 999)
            
            # 更新显示
            self.timer_label.configure(text=f"{display_time:03d}")
    
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
        # 停止计时器
        self._stop_timer()
        
        self.logger.info("扫雷游戏已关闭") 