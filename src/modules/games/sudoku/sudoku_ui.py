#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
数独游戏界面实现
"""

import logging
import time
import threading
from typing import List, Tuple, Dict, Any, Optional, Set

import customtkinter as ctk
from PIL import Image, ImageTk

from src.modules.games.sudoku.sudoku_module import SudokuModule, SudokuDifficulty

class SudokuUI(ctk.CTkFrame):
    """数独游戏UI类"""
    
    def __init__(self, master, config_manager, **kwargs):
        """初始化数独游戏UI
        
        Args:
            master: 父容器
            config_manager: 配置管理器实例
        """
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger("左拾月.数独游戏UI")
        self.config_manager = config_manager
        
        # 初始化游戏模块
        self.sudoku_module = SudokuModule()
        
        # 游戏状态
        self.selected_cell = None
        self.note_mode = False
        self.game_time = 0
        self.timer_running = False
        self.timer_thread = None
        self.stop_timer = threading.Event()
        
        # 单元格按钮
        self.cell_buttons = [[None for _ in range(9)] for _ in range(9)]
        
        # 初始化UI
        self._init_ui()
        
        # 默认启动新游戏
        self._new_game()
        
        self.logger.info("数独游戏UI已初始化")
    
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
        
        difficulty_var = ctk.StringVar(value="简单")
        self.difficulty_menu = ctk.CTkOptionMenu(
            difficulty_frame,
            values=["简单", "中等", "困难"],
            variable=difficulty_var,
            width=80,
            command=self._change_difficulty
        )
        self.difficulty_menu.pack(side="left")
        
        # 中间：计时器
        timer_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        timer_frame.pack(side="left", expand=True)
        
        self.timer_label = ctk.CTkLabel(
            timer_frame,
            text="时间: 00:00",
            font=("Helvetica", 14, "bold")
        )
        self.timer_label.pack()
        
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
        
        # 游戏区域
        game_frame = ctk.CTkFrame(main_frame)
        game_frame.pack(pady=10)
        
        # 创建数独棋盘
        self.board_frame = ctk.CTkFrame(game_frame, fg_color="transparent")
        self.board_frame.pack(padx=10, pady=10)
        
        # 创建单元格
        self._create_board()
        
        # 底部控制区域
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", pady=(20, 0))
        
        # 数字按钮区域
        number_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        number_frame.pack(pady=10)
        
        # 创建数字按钮
        for num in range(1, 10):
            btn = ctk.CTkButton(
                number_frame,
                text=str(num),
                width=40,
                height=40,
                command=lambda n=num: self._input_number(n),
                font=("Helvetica", 16, "bold")
            )
            btn.pack(side="left", padx=5)
        
        # 清除按钮
        clear_btn = ctk.CTkButton(
            number_frame,
            text="清除",
            width=60,
            height=40,
            command=lambda: self._input_number(0),
            fg_color="#E76F51"
        )
        clear_btn.pack(side="left", padx=5)
        
        # 功能按钮区域
        function_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        function_frame.pack(pady=10)
        
        # 笔记模式切换
        self.note_button = ctk.CTkButton(
            function_frame,
            text="笔记模式: 关闭",
            width=120,
            command=self._toggle_note_mode,
            fg_color="#6C757D"
        )
        self.note_button.pack(side="left", padx=10)
        
        # 自动笔记
        ctk.CTkButton(
            function_frame,
            text="自动笔记",
            width=100,
            command=self._auto_notes,
            fg_color="#6C757D"
        ).pack(side="left", padx=10)
        
        # 检查
        ctk.CTkButton(
            function_frame,
            text="检查",
            width=100,
            command=self._check_board,
            fg_color="#6C757D"
        ).pack(side="left", padx=10)
        
        # 提示
        ctk.CTkButton(
            function_frame,
            text="提示",
            width=100,
            command=self._get_hint,
            fg_color="#6C757D"
        ).pack(side="left", padx=10)
        
        # 重置
        ctk.CTkButton(
            function_frame,
            text="重置",
            width=100,
            command=self._reset_game,
            fg_color="#6C757D"
        ).pack(side="left", padx=10)
        
        # 状态栏
        status_frame = ctk.CTkFrame(main_frame, height=30)
        status_frame.pack(fill="x", pady=(20, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="选择一个单元格，然后输入数字",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=5)
    
    def _create_board(self):
        """创建数独棋盘"""
        # 清除现有棋盘
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        # 创建单元格
        for i in range(9):
            for j in range(9):
                # 计算边框宽度
                border_width = 1
                if i % 3 == 0 and i > 0:
                    border_width_top = 3
                else:
                    border_width_top = 1
                
                if j % 3 == 0 and j > 0:
                    border_width_left = 3
                else:
                    border_width_left = 1
                
                # 创建单元格框架
                cell_frame = ctk.CTkFrame(
                    self.board_frame,
                    width=50,
                    height=50,
                    fg_color="#F8F9FA",
                    border_width=border_width,
                    border_color="#343A40"
                )
                cell_frame.grid(
                    row=i, 
                    column=j, 
                    padx=(border_width_left, 0), 
                    pady=(border_width_top, 0)
                )
                
                # 确保单元格大小固定
                cell_frame.grid_propagate(False)
                
                # 创建单元格按钮
                cell_button = ctk.CTkButton(
                    cell_frame,
                    text="",
                    width=48,
                    height=48,
                    fg_color="#F8F9FA",
                    hover_color="#E9ECEF",
                    text_color="#212529",
                    corner_radius=0,
                    font=("Helvetica", 16, "bold"),
                    border_width=0
                )
                cell_button.grid(row=0, column=0)
                
                # 绑定点击事件
                cell_button.configure(command=lambda r=i, c=j: self._select_cell(r, c))
                
                # 存储按钮引用
                self.cell_buttons[i][j] = cell_button
        
        # 添加额外的边框
        for i in range(3):
            for j in range(3):
                box_frame = ctk.CTkFrame(
                    self.board_frame,
                    width=153,
                    height=153,
                    fg_color="transparent",
                    border_width=2,
                    border_color="#343A40"
                )
                box_frame.grid(
                    row=i*3, 
                    column=j*3, 
                    rowspan=3, 
                    columnspan=3
                )
                box_frame.lower()  # 将框架放到底层
    
    def _update_board(self):
        """更新棋盘显示"""
        board = self.sudoku_module.board
        original_board = self.sudoku_module.original_board
        notes = self.sudoku_module.notes
        
        for i in range(9):
            for j in range(9):
                cell_button = self.cell_buttons[i][j]
                
                # 获取单元格值
                value = board[i][j]
                is_original = original_board[i][j] != 0
                cell_notes = notes[i][j]
                
                # 更新单元格显示
                if value != 0:
                    # 显示数字
                    cell_button.configure(
                        text=str(value),
                        font=("Helvetica", 16, "bold"),
                        text_color="#212529" if is_original else "#2A9D8F"
                    )
                elif cell_notes:
                    # 显示笔记
                    notes_text = self._format_notes(cell_notes)
                    cell_button.configure(
                        text=notes_text,
                        font=("Helvetica", 9),
                        text_color="#6C757D"
                    )
                else:
                    # 空单元格
                    cell_button.configure(
                        text="",
                        font=("Helvetica", 16, "bold")
                    )
    
    def _format_notes(self, notes: Set[int]) -> str:
        """格式化笔记显示
        
        Args:
            notes: 笔记集合
        
        Returns:
            str: 格式化后的笔记文本
        """
        if not notes:
            return ""
        
        # 创建3x3网格
        grid = [["" for _ in range(3)] for _ in range(3)]
        
        # 填充数字
        for num in range(1, 10):
            row, col = (num - 1) // 3, (num - 1) % 3
            grid[row][col] = str(num) if num in notes else " "
        
        # 合并为文本
        return "\n".join(" ".join(row) for row in grid)
    
    def _select_cell(self, row: int, col: int):
        """选择单元格
        
        Args:
            row: 行坐标
            col: 列坐标
        """
        # 取消之前的选择
        if self.selected_cell:
            prev_row, prev_col = self.selected_cell
            self.cell_buttons[prev_row][prev_col].configure(fg_color="#F8F9FA")
        
        # 更新选择
        self.selected_cell = (row, col)
        self.cell_buttons[row][col].configure(fg_color="#ADB5BD")
        
        # 更新状态栏
        value = self.sudoku_module.board[row][col]
        is_original = self.sudoku_module.original_board[row][col] != 0
        
        if is_original:
            self.status_label.configure(text=f"单元格 ({row+1},{col+1}) 是原始数字，不能修改")
        elif value != 0:
            self.status_label.configure(text=f"单元格 ({row+1},{col+1}) 当前值为 {value}")
        else:
            self.status_label.configure(text=f"单元格 ({row+1},{col+1}) 已选中，请输入数字")
    
    def _input_number(self, num: int):
        """输入数字
        
        Args:
            num: 要输入的数字
        """
        if not self.selected_cell:
            self.status_label.configure(text="请先选择一个单元格")
            return
        
        row, col = self.selected_cell
        
        # 检查是否是原始单元格
        if self.sudoku_module.original_board[row][col] != 0:
            self.status_label.configure(text="不能修改原始数字")
            return
        
        # 根据模式处理输入
        if self.note_mode and num != 0:
            # 笔记模式
            success = self.sudoku_module.toggle_note(row, col, num)
            if success:
                self.status_label.configure(text=f"在单元格 ({row+1},{col+1}) 添加/移除笔记 {num}")
        else:
            # 普通模式
            success = self.sudoku_module.place_number(row, col, num)
            if success:
                if num == 0:
                    self.status_label.configure(text=f"清除了单元格 ({row+1},{col+1})")
                else:
                    self.status_label.configure(text=f"在单元格 ({row+1},{col+1}) 放置数字 {num}")
        
        # 更新棋盘
        self._update_board()
        
        # 检查游戏是否完成
        if self.sudoku_module.game_completed:
            self._stop_timer()
            self._show_game_completed_dialog()
    
    def _toggle_note_mode(self):
        """切换笔记模式"""
        self.note_mode = not self.note_mode
        
        if self.note_mode:
            self.note_button.configure(
                text="笔记模式: 开启",
                fg_color="#2A9D8F"
            )
            self.status_label.configure(text="笔记模式已开启，点击数字将添加/移除笔记")
        else:
            self.note_button.configure(
                text="笔记模式: 关闭",
                fg_color="#6C757D"
            )
            self.status_label.configure(text="笔记模式已关闭，点击数字将直接填入")
    
    def _auto_notes(self):
        """自动填充笔记"""
        success = self.sudoku_module.auto_notes()
        
        if success:
            self.status_label.configure(text="已自动填充所有可能的笔记")
            self._update_board()
    
    def _check_board(self):
        """检查棋盘"""
        errors = self.sudoku_module.check_board()
        
        if not errors:
            self.status_label.configure(text="棋盘检查通过，没有发现错误")
        else:
            # 高亮错误单元格
            for row, col in errors:
                self.cell_buttons[row][col].configure(fg_color="#E76F51")
            
            self.status_label.configure(text=f"发现 {len(errors)} 个错误，已用红色标记")
            
            # 定时恢复单元格颜色
            self.after(2000, self._restore_cell_colors, errors)
    
    def _restore_cell_colors(self, cells):
        """恢复单元格颜色
        
        Args:
            cells: 需要恢复颜色的单元格坐标列表
        """
        for row, col in cells:
            # 如果是当前选中的单元格，保持选中状态
            if self.selected_cell and self.selected_cell == (row, col):
                self.cell_buttons[row][col].configure(fg_color="#ADB5BD")
            else:
                self.cell_buttons[row][col].configure(fg_color="#F8F9FA")
    
    def _get_hint(self):
        """获取提示"""
        hint = self.sudoku_module.get_hint()
        
        if hint:
            row, col, value = hint
            
            # 放置数字
            self.sudoku_module.place_number(row, col, value)
            
            # 更新棋盘
            self._update_board()
            
            # 选择提示的单元格
            self._select_cell(row, col)
            
            # 高亮提示单元格
            self.cell_buttons[row][col].configure(fg_color="#2A9D8F")
            
            self.status_label.configure(text=f"提示：在单元格 ({row+1},{col+1}) 放置数字 {value}")
            
            # 定时恢复单元格颜色
            self.after(2000, lambda: self._restore_cell_colors([(row, col)]))
            
            # 检查游戏是否完成
            if self.sudoku_module.game_completed:
                self._stop_timer()
                self._show_game_completed_dialog()
        else:
            self.status_label.configure(text="没有可用的提示")
    
    def _reset_game(self):
        """重置游戏"""
        # 显示确认对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("确认重置")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # 使对话框居中于主窗口
        self._center_dialog(dialog, 300, 150)
        
        ctk.CTkLabel(
            dialog,
            text="确定要重置游戏吗？",
            font=("Helvetica", 14, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text="所有进度将会丢失",
            font=("Helvetica", 12)
        ).pack(pady=5)
        
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
            text="确定",
            width=80,
            fg_color="#E76F51",
            command=lambda: self._confirm_reset(dialog)
        ).pack(side="left", padx=10)
    
    def _confirm_reset(self, dialog):
        """确认重置游戏
        
        Args:
            dialog: 对话框
        """
        dialog.destroy()
        
        # 重置游戏
        self.sudoku_module.reset_game()
        
        # 重置计时器
        self._reset_timer()
        
        # 更新棋盘
        self._update_board()
        
        # 清除选择
        if self.selected_cell:
            row, col = self.selected_cell
            self.cell_buttons[row][col].configure(fg_color="#F8F9FA")
            self.selected_cell = None
        
        # 更新状态栏
        self.status_label.configure(text="游戏已重置")
    
    def _new_game(self):
        """开始新游戏"""
        # 获取当前难度
        difficulty_text = self.difficulty_menu.get()
        
        # 映射难度
        difficulty_map = {
            "简单": SudokuDifficulty.EASY,
            "中等": SudokuDifficulty.MEDIUM,
            "困难": SudokuDifficulty.HARD
        }
        
        difficulty = difficulty_map[difficulty_text]
        
        # 开始新游戏
        self.sudoku_module.new_game(difficulty)
        
        # 重置计时器
        self._reset_timer()
        
        # 启动计时器
        self._start_timer()
        
        # 更新棋盘
        self._update_board()
        
        # 调整窗口大小
        self._adjust_window_size()
        
        # 清除选择
        if self.selected_cell:
            row, col = self.selected_cell
            self.cell_buttons[row][col].configure(fg_color="#F8F9FA")
            self.selected_cell = None
        
        # 关闭笔记模式
        self.note_mode = False
        self.note_button.configure(
            text="笔记模式: 关闭",
            fg_color="#6C757D"
        )
        
        # 更新状态栏
        self.status_label.configure(text=f"开始新游戏，难度：{difficulty_text}")
    
    def _adjust_window_size(self):
        """调整窗口大小"""
        # 获取游戏空间UI
        game_space = self.winfo_toplevel()
        
        # 设置适合的窗口大小
        new_width = 1200
        new_height = 800
        
        # 获取屏幕尺寸
        screen_width = game_space.winfo_screenwidth()
        screen_height = game_space.winfo_screenheight()
        
        # 确保窗口不会超出屏幕
        new_width = min(new_width, screen_width - 100)
        new_height = min(new_height, screen_height - 100)
        
        # 调整窗口大小
        game_space.geometry(f"{new_width}x{new_height}")
        
        # 计算窗口居中的位置
        x_position = (screen_width - new_width) // 2
        y_position = (screen_height - new_height) // 2
        
        # 设置窗口位置
        game_space.geometry(f"{new_width}x{new_height}+{x_position}+{y_position}")
        logging.info(f"窗口大小已调整为 {new_width}x{new_height}")
    
    def _change_difficulty(self, difficulty_text):
        """改变游戏难度
        
        Args:
            difficulty_text: 难度文本
        """
        # 询问是否开始新游戏
        dialog = ctk.CTkToplevel(self)
        dialog.title("开始新游戏")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # 使对话框居中于主窗口
        self._center_dialog(dialog, 300, 150)
        
        ctk.CTkLabel(
            dialog,
            text=f"是否开始新的{difficulty_text}难度游戏？",
            font=("Helvetica", 14, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text="当前游戏进度将会丢失",
            font=("Helvetica", 12)
        ).pack(pady=5)
        
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
            text="确定",
            width=80,
            fg_color="#2A9D8F",
            command=lambda: self._confirm_new_game(dialog)
        ).pack(side="left", padx=10)
    
    def _confirm_new_game(self, dialog):
        """确认开始新游戏
        
        Args:
            dialog: 对话框
        """
        dialog.destroy()
        self._new_game()
    
    def _show_game_completed_dialog(self):
        """显示游戏完成对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("恭喜")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # 使对话框居中于主窗口
        self._center_dialog(dialog, 300, 250)
        
        ctk.CTkLabel(
            dialog,
            text="恭喜！你完成了数独游戏",
            font=("Helvetica", 16, "bold"),
            text_color="#2A9D8F"
        ).pack(pady=(20, 10))
        
        # 游戏统计信息
        stats = self.sudoku_module.get_game_stats()
        
        stats_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        stats_frame.pack(pady=10)
        
        difficulty_map = {
            "EASY": "简单",
            "MEDIUM": "中等",
            "HARD": "困难"
        }
        
        ctk.CTkLabel(
            stats_frame,
            text=f"难度: {difficulty_map[stats['difficulty']]}",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(
            stats_frame,
            text=f"用时: {self._format_time(self.game_time)}",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(
            stats_frame,
            text=f"使用提示: {stats['hints_used']} 次",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(
            stats_frame,
            text=f"错误次数: {stats['mistakes_made']} 次",
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
        self.timer_label.configure(text="时间: 00:00")
    
    def _timer_loop(self):
        """计时器循环"""
        start_time = time.time()
        
        while self.timer_running and not self.stop_timer.is_set():
            # 每秒更新一次
            time.sleep(1)
            
            # 计算经过的时间
            self.game_time = int(time.time() - start_time)
            
            # 更新显示
            self.timer_label.configure(text=f"时间: {self._format_time(self.game_time)}")
    
    def _format_time(self, seconds: int) -> str:
        """格式化时间
        
        Args:
            seconds: 秒数
        
        Returns:
            str: 格式化后的时间字符串
        """
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
    
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
        
        self.logger.info("数独游戏已关闭") 