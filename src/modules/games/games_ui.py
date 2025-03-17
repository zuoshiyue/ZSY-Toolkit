#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
游戏空间模块UI
"""

import customtkinter as ctk
import logging
import json
import os
from typing import Optional, Dict, List

class GamesUI(ctk.CTkFrame):
    """游戏空间模块UI类"""
    
    def __init__(self, master, platform_adapter, config_manager):
        super().__init__(master)
        self.logger = logging.getLogger("左拾月.游戏空间")
        self.platform_adapter = platform_adapter
        self.config_manager = config_manager
        
        # 游戏列表
        self.games: Dict[str, Dict] = {}
        
        self._init_ui()
        self._load_games()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建游戏列表框架
        games_frame = ctk.CTkFrame(self)
        games_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        games_frame.grid_columnconfigure(0, weight=1)
        
        # 游戏列表标题
        title_label = ctk.CTkLabel(
            games_frame,
            text="游戏列表",
            font=("微软雅黑", 16, "bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 游戏列表
        self.games_list = ctk.CTkScrollableFrame(
            games_frame,
            width=300,
            height=400
        )
        self.games_list.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # 添加游戏按钮
        add_button = ctk.CTkButton(
            games_frame,
            text="添加游戏",
            command=self._add_game,
            font=("微软雅黑", 12)
        )
        add_button.grid(row=2, column=0, padx=10, pady=10)
        
    def _load_games(self):
        """加载游戏列表"""
        try:
            games_file = os.path.join(
                self.config_manager.get_config_dir(),
                "games.json"
            )
            
            if os.path.exists(games_file):
                with open(games_file, "r", encoding="utf-8") as f:
                    self.games = json.load(f)
                    
            self._update_games_list()
        except Exception as e:
            self.logger.error(f"加载游戏列表失败: {str(e)}")
            
    def _save_games(self):
        """保存游戏列表"""
        try:
            games_file = os.path.join(
                self.config_manager.get_config_dir(),
                "games.json"
            )
            
            with open(games_file, "w", encoding="utf-8") as f:
                json.dump(self.games, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"保存游戏列表失败: {str(e)}")
            
    def _update_games_list(self):
        """更新游戏列表显示"""
        # 清空现有列表
        for widget in self.games_list.winfo_children():
            widget.destroy()
            
        # 添加游戏项
        for game_id, game_info in self.games.items():
            game_frame = ctk.CTkFrame(self.games_list)
            game_frame.pack(fill="x", padx=5, pady=2)
            
            # 游戏名称
            name_label = ctk.CTkLabel(
                game_frame,
                text=game_info["name"],
                font=("微软雅黑", 12)
            )
            name_label.pack(side="left", padx=5)
            
            # 启动按钮
            launch_button = ctk.CTkButton(
                game_frame,
                text="启动",
                command=lambda g=game_id: self._launch_game(g),
                font=("微软雅黑", 10)
            )
            launch_button.pack(side="right", padx=5)
            
            # 删除按钮
            delete_button = ctk.CTkButton(
                game_frame,
                text="删除",
                command=lambda g=game_id: self._delete_game(g),
                font=("微软雅黑", 10)
            )
            delete_button.pack(side="right", padx=5)
            
    def _add_game(self):
        """添加游戏"""
        dialog = AddGameDialog(self)
        if dialog.result:
            game_id = dialog.result["id"]
            self.games[game_id] = dialog.result
            self._save_games()
            self._update_games_list()
            
    def _delete_game(self, game_id: str):
        """删除游戏"""
        if game_id in self.games:
            del self.games[game_id]
            self._save_games()
            self._update_games_list()
            
    def _launch_game(self, game_id: str):
        """启动游戏"""
        if game_id in self.games:
            game_info = self.games[game_id]
            try:
                self.platform_adapter.run_command(game_info["path"])
                self.logger.info(f"启动游戏成功: {game_info['name']}")
            except Exception as e:
                self.logger.error(f"启动游戏失败: {str(e)}")
                
class AddGameDialog(ctk.CTkToplevel):
    """添加游戏对话框"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        
        # 设置窗口
        self.title("添加游戏")
        self.geometry("300x200")
        
        # 创建输入框
        name_label = ctk.CTkLabel(
            self,
            text="游戏名称:",
            font=("微软雅黑", 12)
        )
        name_label.pack(padx=10, pady=5)
        
        self.name_entry = ctk.CTkEntry(
            self,
            width=200,
            font=("微软雅黑", 12)
        )
        self.name_entry.pack(padx=10, pady=5)
        
        path_label = ctk.CTkLabel(
            self,
            text="游戏路径:",
            font=("微软雅黑", 12)
        )
        path_label.pack(padx=10, pady=5)
        
        self.path_entry = ctk.CTkEntry(
            self,
            width=200,
            font=("微软雅黑", 12)
        )
        self.path_entry.pack(padx=10, pady=5)
        
        # 浏览按钮
        browse_button = ctk.CTkButton(
            self,
            text="浏览",
            command=self._browse_file,
            font=("微软雅黑", 12)
        )
        browse_button.pack(padx=10, pady=5)
        
        # 确定按钮
        ok_button = ctk.CTkButton(
            self,
            text="确定",
            command=self._on_ok,
            font=("微软雅黑", 12)
        )
        ok_button.pack(padx=10, pady=10)
        
        # 等待窗口关闭
        self.wait_window()
        
    def _browse_file(self):
        """浏览文件"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择游戏程序",
            filetypes=[
                ("可执行文件", "*.exe"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file_path)
            
    def _on_ok(self):
        """确定按钮点击处理"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if name and path:
            self.result = {
                "id": f"game_{len(self.master.games)}",
                "name": name,
                "path": path
            }
            self.destroy() 