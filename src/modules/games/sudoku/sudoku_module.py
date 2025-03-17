#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
数独游戏核心逻辑模块
"""

import random
import copy
import enum
import logging
from typing import List, Tuple, Dict, Any, Optional, Set

class SudokuDifficulty(enum.Enum):
    """数独难度枚举"""
    EASY = 1
    MEDIUM = 2
    HARD = 3

class SudokuModule:
    """数独游戏核心逻辑类"""
    
    def __init__(self):
        """初始化数独游戏"""
        self.logger = logging.getLogger("左拾月.数独游戏")
        
        # 游戏数据
        self.board = [[0 for _ in range(9)] for _ in range(9)]  # 当前棋盘
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]  # 原始棋盘（不可修改的数字）
        self.solution = [[0 for _ in range(9)] for _ in range(9)]  # 解决方案
        
        # 游戏状态
        self.difficulty = SudokuDifficulty.EASY
        self.game_started = False
        self.game_completed = False
        self.hints_used = 0
        self.mistakes_made = 0
        
        # 玩家笔记
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        
        self.logger.info("数独游戏核心逻辑已初始化")
    
    def new_game(self, difficulty: SudokuDifficulty = SudokuDifficulty.EASY):
        """开始新游戏
        
        Args:
            difficulty: 游戏难度
        """
        self.difficulty = difficulty
        self.game_started = True
        self.game_completed = False
        self.hints_used = 0
        self.mistakes_made = 0
        
        # 清空笔记
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        
        # 生成新的数独谜题
        self._generate_puzzle(difficulty)
        
        self.logger.info(f"开始新游戏，难度：{difficulty.name}")
        
        return True
    
    def _generate_puzzle(self, difficulty: SudokuDifficulty):
        """生成数独谜题
        
        Args:
            difficulty: 游戏难度
        """
        # 生成完整解决方案
        self._generate_solution()
        
        # 复制解决方案到当前棋盘
        self.board = copy.deepcopy(self.solution)
        
        # 根据难度移除数字
        cells_to_remove = {
            SudokuDifficulty.EASY: 40,     # 保留41个数字
            SudokuDifficulty.MEDIUM: 50,   # 保留31个数字
            SudokuDifficulty.HARD: 60      # 保留21个数字
        }
        
        # 获取所有单元格位置
        all_positions = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(all_positions)
        
        # 移除指定数量的数字
        for r, c in all_positions[:cells_to_remove[difficulty]]:
            self.board[r][c] = 0
        
        # 保存原始棋盘
        self.original_board = copy.deepcopy(self.board)
    
    def _generate_solution(self):
        """生成完整的数独解决方案"""
        # 清空解决方案
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        
        # 填充对角线上的3个3x3方块
        for i in range(0, 9, 3):
            self._fill_box(i, i)
        
        # 填充剩余单元格
        self._solve_board()
    
    def _fill_box(self, row: int, col: int):
        """填充3x3方块
        
        Args:
            row: 起始行
            col: 起始列
        """
        nums = list(range(1, 10))
        random.shuffle(nums)
        
        index = 0
        for r in range(3):
            for c in range(3):
                self.solution[row + r][col + c] = nums[index]
                index += 1
    
    def _solve_board(self) -> bool:
        """解决数独棋盘
        
        Returns:
            bool: 是否成功解决
        """
        # 查找空单元格
        empty_cell = self._find_empty()
        if not empty_cell:
            return True  # 棋盘已填满
        
        row, col = empty_cell
        
        # 尝试填入1-9
        for num in range(1, 10):
            # 检查是否有效
            if self._is_valid(row, col, num):
                # 填入数字
                self.solution[row][col] = num
                
                # 递归解决剩余部分
                if self._solve_board():
                    return True
                
                # 如果无法解决，回溯
                self.solution[row][col] = 0
        
        return False  # 触发回溯
    
    def _find_empty(self) -> Optional[Tuple[int, int]]:
        """查找空单元格
        
        Returns:
            Optional[Tuple[int, int]]: 空单元格的坐标，如果没有则返回None
        """
        for r in range(9):
            for c in range(9):
                if self.solution[r][c] == 0:
                    return (r, c)
        return None
    
    def _is_valid(self, row: int, col: int, num: int) -> bool:
        """检查在指定位置放置数字是否有效
        
        Args:
            row: 行坐标
            col: 列坐标
            num: 要放置的数字
        
        Returns:
            bool: 是否有效
        """
        # 检查行
        for c in range(9):
            if self.solution[row][c] == num:
                return False
        
        # 检查列
        for r in range(9):
            if self.solution[r][col] == num:
                return False
        
        # 检查3x3方块
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.solution[r][c] == num:
                    return False
        
        return True
    
    def place_number(self, row: int, col: int, num: int) -> bool:
        """在指定位置放置数字
        
        Args:
            row: 行坐标
            col: 列坐标
            num: 要放置的数字
        
        Returns:
            bool: 是否成功放置
        """
        # 检查游戏是否已开始
        if not self.game_started:
            return False
        
        # 检查游戏是否已完成
        if self.game_completed:
            return False
        
        # 检查坐标是否有效
        if not (0 <= row < 9 and 0 <= col < 9):
            return False
        
        # 检查单元格是否为原始数字（不可修改）
        if self.original_board[row][col] != 0:
            return False
        
        # 检查数字是否有效
        if not (0 <= num <= 9):  # 0表示清除
            return False
        
        # 放置数字
        self.board[row][col] = num
        
        # 清除该单元格的笔记
        if num != 0:
            self.notes[row][col] = set()
        
        # 检查是否完成游戏
        if self._check_completion():
            self.game_completed = True
            self.logger.info("游戏完成！")
        
        return True
    
    def toggle_note(self, row: int, col: int, num: int) -> bool:
        """切换笔记中的数字
        
        Args:
            row: 行坐标
            col: 列坐标
            num: 要切换的数字
        
        Returns:
            bool: 是否成功切换
        """
        # 检查游戏是否已开始
        if not self.game_started:
            return False
        
        # 检查游戏是否已完成
        if self.game_completed:
            return False
        
        # 检查坐标是否有效
        if not (0 <= row < 9 and 0 <= col < 9):
            return False
        
        # 检查单元格是否为原始数字（不可修改）
        if self.original_board[row][col] != 0:
            return False
        
        # 检查单元格是否已填入数字
        if self.board[row][col] != 0:
            return False
        
        # 检查数字是否有效
        if not (1 <= num <= 9):
            return False
        
        # 切换笔记
        if num in self.notes[row][col]:
            self.notes[row][col].remove(num)
        else:
            self.notes[row][col].add(num)
        
        return True
    
    def get_hint(self) -> Optional[Tuple[int, int, int]]:
        """获取提示
        
        Returns:
            Optional[Tuple[int, int, int]]: (行, 列, 数字)的提示，如果没有可用提示则返回None
        """
        # 检查游戏是否已开始
        if not self.game_started:
            return None
        
        # 检查游戏是否已完成
        if self.game_completed:
            return None
        
        # 查找一个空单元格或错误单元格
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0 or self.board[r][c] != self.solution[r][c]:
                    # 增加提示使用计数
                    self.hints_used += 1
                    
                    # 返回正确的数字
                    return (r, c, self.solution[r][c])
        
        return None
    
    def check_board(self) -> List[Tuple[int, int]]:
        """检查棋盘，返回错误单元格的坐标
        
        Returns:
            List[Tuple[int, int]]: 错误单元格的坐标列表
        """
        errors = []
        
        for r in range(9):
            for c in range(9):
                # 跳过空单元格
                if self.board[r][c] == 0:
                    continue
                
                # 检查是否与解决方案匹配
                if self.board[r][c] != self.solution[r][c]:
                    errors.append((r, c))
                    
                    # 增加错误计数
                    self.mistakes_made += 1
        
        return errors
    
    def auto_notes(self) -> bool:
        """自动填充所有可能的笔记
        
        Returns:
            bool: 是否成功填充
        """
        # 检查游戏是否已开始
        if not self.game_started:
            return False
        
        # 检查游戏是否已完成
        if self.game_completed:
            return False
        
        # 清空所有笔记
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        
        # 为每个空单元格计算可能的数字
        for r in range(9):
            for c in range(9):
                # 跳过已填入数字的单元格
                if self.board[r][c] != 0:
                    continue
                
                # 计算可能的数字
                possible_nums = self._get_possible_numbers(r, c)
                
                # 填入笔记
                self.notes[r][c] = possible_nums
        
        return True
    
    def _get_possible_numbers(self, row: int, col: int) -> Set[int]:
        """获取指定位置可能的数字
        
        Args:
            row: 行坐标
            col: 列坐标
        
        Returns:
            Set[int]: 可能的数字集合
        """
        # 初始化为1-9
        possible = set(range(1, 10))
        
        # 移除行中已存在的数字
        for c in range(9):
            if self.board[row][c] != 0:
                possible.discard(self.board[row][c])
        
        # 移除列中已存在的数字
        for r in range(9):
            if self.board[r][col] != 0:
                possible.discard(self.board[r][col])
        
        # 移除3x3方块中已存在的数字
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.board[r][c] != 0:
                    possible.discard(self.board[r][c])
        
        return possible
    
    def _check_completion(self) -> bool:
        """检查游戏是否完成
        
        Returns:
            bool: 是否完成
        """
        # 检查是否有空单元格
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return False
        
        # 检查是否与解决方案匹配
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != self.solution[r][c]:
                    return False
        
        return True
    
    def reset_game(self) -> bool:
        """重置游戏到初始状态
        
        Returns:
            bool: 是否成功重置
        """
        # 检查游戏是否已开始
        if not self.game_started:
            return False
        
        # 重置棋盘到原始状态
        self.board = copy.deepcopy(self.original_board)
        
        # 重置游戏状态
        self.game_completed = False
        self.hints_used = 0
        self.mistakes_made = 0
        
        # 清空笔记
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        
        self.logger.info("游戏已重置")
        
        return True
    
    def get_game_stats(self) -> Dict[str, Any]:
        """获取游戏统计信息
        
        Returns:
            Dict[str, Any]: 游戏统计信息
        """
        # 计算完成百分比
        total_cells = 81
        filled_cells = sum(1 for r in range(9) for c in range(9) if self.board[r][c] != 0)
        original_cells = sum(1 for r in range(9) for c in range(9) if self.original_board[r][c] != 0)
        player_filled = filled_cells - original_cells
        to_fill = total_cells - original_cells
        
        completion_percentage = (player_filled / to_fill * 100) if to_fill > 0 else 0
        
        return {
            "difficulty": self.difficulty.name,
            "completion_percentage": completion_percentage,
            "hints_used": self.hints_used,
            "mistakes_made": self.mistakes_made,
            "game_completed": self.game_completed
        } 