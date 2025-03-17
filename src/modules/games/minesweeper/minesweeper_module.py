#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
扫雷游戏核心逻辑模块
"""

import random
import logging
from enum import Enum
from typing import List, Tuple, Dict, Any, Set

class MinesweeperDifficulty(Enum):
    """扫雷难度枚举"""
    BEGINNER = 0      # 初级: 9x9, 10颗地雷
    INTERMEDIATE = 1  # 中级: 16x16, 40颗地雷
    EXPERT = 2        # 高级: 16x30, 99颗地雷
    CUSTOM = 3        # 自定义

class CellState(Enum):
    """单元格状态枚举"""
    COVERED = 0    # 覆盖状态
    FLAGGED = 1    # 插旗状态
    QUESTION = 2   # 问号状态
    REVEALED = 3   # 已揭开状态

class GameState(Enum):
    """游戏状态枚举"""
    NOT_STARTED = 0  # 未开始
    RUNNING = 1      # 进行中
    FAILED = 2       # 失败
    WON = 3          # 胜利

class MinesweeperModule:
    """扫雷游戏模块主类"""
    
    def __init__(self):
        """初始化扫雷游戏模块"""
        self.logger = logging.getLogger("左拾月.扫雷游戏")
        
        # 默认配置
        self.difficulty_config = {
            MinesweeperDifficulty.BEGINNER: {
                "rows": 9,
                "cols": 9,
                "mines": 10
            },
            MinesweeperDifficulty.INTERMEDIATE: {
                "rows": 16,
                "cols": 16,
                "mines": 40
            },
            MinesweeperDifficulty.EXPERT: {
                "rows": 16,
                "cols": 30,
                "mines": 99
            }
        }
        
        # 游戏配置
        self.rows = 9
        self.cols = 9
        self.mine_count = 10
        self.current_difficulty = MinesweeperDifficulty.BEGINNER
        
        # 游戏状态
        self.board = []  # 地雷矩阵: -1代表地雷，0-8代表周围地雷数
        self.cell_states = []  # 单元格状态矩阵
        self.game_state = GameState.NOT_STARTED
        self.first_click = True
        self.revealed_count = 0
        self.flagged_count = 0
        
        # 初始化游戏
        self._init_game()
        
        self.logger.info("扫雷游戏模块已初始化")
    
    def _init_game(self):
        """初始化游戏状态"""
        # 创建空白棋盘
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cell_states = [[CellState.COVERED for _ in range(self.cols)] for _ in range(self.rows)]
        
        # 重置游戏状态
        self.game_state = GameState.NOT_STARTED
        self.first_click = True
        self.revealed_count = 0
        self.flagged_count = 0
    
    def new_game(self, difficulty: MinesweeperDifficulty = None, custom_config: Dict[str, int] = None) -> bool:
        """开始新游戏
        
        Args:
            difficulty: 游戏难度
            custom_config: 自定义配置 (适用于CUSTOM难度，需包含rows, cols, mines)
            
        Returns:
            bool: 是否成功开始新游戏
        """
        try:
            # 更新难度设置
            if difficulty is not None:
                self.current_difficulty = difficulty
            
            # 根据难度设置游戏参数
            if self.current_difficulty == MinesweeperDifficulty.CUSTOM:
                if custom_config is None or not self._validate_custom_config(custom_config):
                    self.logger.error("无效的自定义配置")
                    return False
                
                self.rows = custom_config["rows"]
                self.cols = custom_config["cols"]
                self.mine_count = custom_config["mines"]
            else:
                config = self.difficulty_config[self.current_difficulty]
                self.rows = config["rows"]
                self.cols = config["cols"]
                self.mine_count = config["mines"]
            
            # 初始化游戏
            self._init_game()
            
            self.logger.info(f"开始新游戏: {self.current_difficulty.name} ({self.rows}x{self.cols}, {self.mine_count}颗地雷)")
            return True
            
        except Exception as e:
            self.logger.error(f"开始新游戏失败：{str(e)}")
            return False
    
    def _validate_custom_config(self, config: Dict[str, int]) -> bool:
        """验证自定义配置
        
        Args:
            config: 自定义配置
            
        Returns:
            bool: 配置是否有效
        """
        # 确保所需字段存在
        if "rows" not in config or "cols" not in config or "mines" not in config:
            return False
        
        rows = config["rows"]
        cols = config["cols"]
        mines = config["mines"]
        
        # 验证范围
        if not (5 <= rows <= 30) or not (5 <= cols <= 30):
            return False
        
        # 验证地雷数量 (最少1个，最多占总格子数的1/3)
        max_mines = (rows * cols) // 3
        if not (1 <= mines <= max_mines):
            return False
        
        return True
    
    def _place_mines(self, first_row: int, first_col: int) -> None:
        """放置地雷，确保第一次点击的位置及其周围没有地雷
        
        Args:
            first_row: 第一次点击的行
            first_col: 第一次点击的列
        """
        # 确定禁止放置地雷的区域
        safe_cells = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = first_row + dr, first_col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    safe_cells.add((r, c))
        
        # 创建可以放置地雷的单元格列表
        available_cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in safe_cells:
                    available_cells.append((r, c))
        
        # 随机选择单元格放置地雷
        mine_positions = random.sample(available_cells, min(self.mine_count, len(available_cells)))
        
        # 在选定位置放置地雷
        for r, c in mine_positions:
            self.board[r][c] = -1
        
        # 计算每个单元格周围的地雷数
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != -1:  # 如果不是地雷
                    self.board[r][c] = self._count_adjacent_mines(r, c)
    
    def _count_adjacent_mines(self, row: int, col: int) -> int:
        """计算单元格周围的地雷数
        
        Args:
            row: 行坐标
            col: 列坐标
            
        Returns:
            int: 周围地雷数
        """
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == -1:
                    count += 1
        
        return count
    
    def reveal_cell(self, row: int, col: int) -> Tuple[bool, List[Tuple[int, int]], bool]:
        """揭开单元格
        
        Args:
            row: 行坐标
            col: 列坐标
            
        Returns:
            Tuple[bool, List[Tuple[int, int]], bool]:
                - 是否成功揭开
                - 揭开的单元格列表 [(row, col, value), ...]
                - 是否触发地雷
        """
        # 验证坐标是否有效
        if not self._is_valid_cell(row, col):
            return False, [], False
        
        # 检查单元格是否可以揭开
        if self.cell_states[row][col] != CellState.COVERED and self.cell_states[row][col] != CellState.QUESTION:
            return False, [], False
        
        # 如果游戏已经结束，不能继续揭开
        if self.game_state == GameState.FAILED or self.game_state == GameState.WON:
            return False, [], False
        
        # 如果是第一次点击，生成地雷
        if self.first_click:
            self._place_mines(row, col)
            self.first_click = False
            self.game_state = GameState.RUNNING
        
        # 如果点到地雷，游戏结束
        if self.board[row][col] == -1:
            self.cell_states[row][col] = CellState.REVEALED
            self.game_state = GameState.FAILED
            
            # 返回所有地雷位置
            mines = []
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board[r][c] == -1:
                        mines.append((r, c, -1))
            
            self.logger.info(f"游戏失败：触发地雷 ({row},{col})")
            return True, mines, True
        
        # 揭开单元格
        revealed_cells = []
        self._reveal_cell_recursive(row, col, revealed_cells)
        
        # 检查是否获胜
        if self._check_win():
            self.game_state = GameState.WON
            self.logger.info("游戏胜利！")
        
        return True, revealed_cells, False
    
    def _reveal_cell_recursive(self, row: int, col: int, revealed_cells: List[Tuple[int, int, int]]) -> None:
        """递归揭开单元格
        
        Args:
            row: 行坐标
            col: 列坐标
            revealed_cells: 已揭开的单元格列表，会被修改
        """
        # 检查单元格是否已经揭开
        if self.cell_states[row][col] == CellState.REVEALED:
            return
        
        # 只能揭开覆盖或问号状态的单元格
        if self.cell_states[row][col] != CellState.COVERED and self.cell_states[row][col] != CellState.QUESTION:
            return
        
        # 揭开单元格
        self.cell_states[row][col] = CellState.REVEALED
        self.revealed_count += 1
        revealed_cells.append((row, col, self.board[row][col]))
        
        # 如果是空白单元格(周围没有地雷)，递归揭开周围的单元格
        if self.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    
                    r, c = row + dr, col + dc
                    if self._is_valid_cell(r, c):
                        self._reveal_cell_recursive(r, c, revealed_cells)
    
    def toggle_flag(self, row: int, col: int) -> Tuple[bool, CellState]:
        """切换单元格标记状态
        
        Args:
            row: 行坐标
            col: 列坐标
            
        Returns:
            Tuple[bool, CellState]: (是否成功切换, 新状态)
        """
        # 验证坐标是否有效
        if not self._is_valid_cell(row, col):
            return False, CellState.COVERED
        
        # 已揭开的单元格不能标记
        if self.cell_states[row][col] == CellState.REVEALED:
            return False, CellState.REVEALED
        
        # 如果游戏已经结束，不能继续标记
        if self.game_state == GameState.FAILED or self.game_state == GameState.WON:
            return False, self.cell_states[row][col]
        
        # 切换状态：COVERED -> FLAGGED -> QUESTION -> COVERED
        current_state = self.cell_states[row][col]
        
        if current_state == CellState.COVERED:
            new_state = CellState.FLAGGED
            self.flagged_count += 1
        elif current_state == CellState.FLAGGED:
            new_state = CellState.QUESTION
            self.flagged_count -= 1
        else:  # QUESTION
            new_state = CellState.COVERED
        
        self.cell_states[row][col] = new_state
        
        return True, new_state
    
    def chord(self, row: int, col: int) -> Tuple[bool, List[Tuple[int, int, int]], bool]:
        """和弦操作（快速揭开已数字单元格周围未标记的单元格）
        
        Args:
            row: 行坐标
            col: 列坐标
            
        Returns:
            Tuple[bool, List[Tuple[int, int, int]], bool]:
                - 是否成功执行和弦操作
                - 揭开的单元格列表 [(row, col, value), ...]
                - 是否触发地雷
        """
        # 验证坐标是否有效
        if not self._is_valid_cell(row, col):
            return False, [], False
        
        # 检查是否是已揭开的数字单元格
        if self.cell_states[row][col] != CellState.REVEALED or self.board[row][col] <= 0:
            return False, [], False
        
        # 统计周围的旗子数量
        flag_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                r, c = row + dr, col + dc
                if self._is_valid_cell(r, c) and self.cell_states[r][c] == CellState.FLAGGED:
                    flag_count += 1
        
        # 如果旗子数量与数字相同，揭开周围未标记的单元格
        if flag_count == self.board[row][col]:
            revealed_cells = []
            hit_mine = False
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    
                    r, c = row + dr, col + dc
                    if self._is_valid_cell(r, c) and (self.cell_states[r][c] == CellState.COVERED or self.cell_states[r][c] == CellState.QUESTION):
                        success, cells, mine_hit = self.reveal_cell(r, c)
                        if success:
                            revealed_cells.extend(cells)
                            if mine_hit:
                                hit_mine = True
            
            return True, revealed_cells, hit_mine
        
        return False, [], False
    
    def _is_valid_cell(self, row: int, col: int) -> bool:
        """检查单元格坐标是否有效
        
        Args:
            row: 行坐标
            col: 列坐标
            
        Returns:
            bool: 是否有效
        """
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def _check_win(self) -> bool:
        """检查是否获胜
        
        Returns:
            bool: 是否获胜
        """
        # 所有非地雷单元格都已揭开
        return self.revealed_count == (self.rows * self.cols - self.mine_count)
    
    def get_board_state(self) -> Dict[str, Any]:
        """获取游戏状态
        
        Returns:
            Dict[str, Any]: 游戏状态数据
        """
        return {
            "rows": self.rows,
            "cols": self.cols,
            "mine_count": self.mine_count,
            "flagged_count": self.flagged_count,
            "game_state": self.game_state,
            "difficulty": self.current_difficulty
        }
    
    def get_cell_state(self, row: int, col: int) -> Dict[str, Any]:
        """获取单元格状态
        
        Args:
            row: 行坐标
            col: 列坐标
            
        Returns:
            Dict[str, Any]: 单元格状态数据
        """
        if not self._is_valid_cell(row, col):
            return None
        
        return {
            "state": self.cell_states[row][col],
            "value": self.board[row][col] if self.cell_states[row][col] == CellState.REVEALED else None
        }
    
    def get_all_mines(self) -> List[Tuple[int, int]]:
        """获取所有地雷位置
        
        Returns:
            List[Tuple[int, int]]: 地雷位置列表
        """
        mines = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == -1:
                    mines.append((r, c))
        
        return mines 