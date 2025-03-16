#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器模块
负责管理应用程序的配置信息
"""

import os
import json
import logging
from pathlib import Path

class ConfigManager:
    """配置管理器，处理应用程序配置的读取和保存"""
    
    def __init__(self):
        self.logger = logging.getLogger("左拾月.配置管理器")
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
        self.logger.info("配置管理器已初始化")
    
    def _get_config_dir(self):
        """获取配置目录，根据不同操作系统返回适当的路径"""
        if os.name == "nt":  # Windows
            app_data = os.getenv("APPDATA")
            config_dir = Path(app_data) / "左拾月"
        else:  # macOS 和 Linux
            home = os.path.expanduser("~")
            config_dir = Path(home) / ".config" / "左拾月"
        
        # 确保配置目录存在
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        default_config = {
            "theme": "light",
            "language": "zh_CN",
            "first_run": True,
            "modules": {
                "todo": {
                    "enabled": True,
                    "default_view": "quadrant"
                },
                "pomodoro": {
                    "enabled": True,
                    "work_duration": 25,
                    "short_break": 5,
                    "long_break": 15,
                    "cycles_before_long_break": 4
                },
                "launcher": {
                    "enabled": True,
                    "show_recent": True,
                    "max_recent": 5
                },
                "games": {
                    "enabled": True,
                    "sudoku": {
                        "difficulty": "medium",
                        "auto_save": True
                    },
                    "minesweeper": {
                        "difficulty": "beginner",
                        "custom_size": {
                            "width": 10,
                            "height": 10,
                            "mines": 10
                        }
                    }
                }
            },
            "system": {
                "startup": False,
                "minimize_to_tray": True,
                "check_updates": True
            },
            "shortcuts": {
                "global": {
                    "show_app": "Alt+Z"
                }
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # 更新配置，确保所有默认值都存在
                    self._update_config_recursively(default_config, config)
                    self.logger.info("配置已加载")
                    return config
            else:
                # 配置文件不存在，创建默认配置
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
                self.logger.info("已创建默认配置文件")
                return default_config
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
            return default_config
    
    def _update_config_recursively(self, default, current):
        """递归更新配置，确保所有默认值都存在"""
        for key, value in default.items():
            if key not in current:
                current[key] = value
            elif isinstance(value, dict) and isinstance(current[key], dict):
                self._update_config_recursively(value, current[key])
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            self.logger.info("配置已保存")
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """获取配置值
        
        Args:
            key: 配置键，支持点号分隔的路径，如 "modules.todo.enabled"
            default: 如果配置不存在，返回的默认值
        
        Returns:
            配置值或默认值
        """
        try:
            parts = key.split(".")
            value = self.config
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """设置配置值
        
        Args:
            key: 配置键，支持点号分隔的路径，如 "modules.todo.enabled"
            value: 要设置的值
        
        Returns:
            bool: 是否设置成功
        """
        try:
            parts = key.split(".")
            config = self.config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
            return self.save()
        except Exception as e:
            self.logger.error(f"设置配置失败: {key}={value}, 错误: {str(e)}")
            return False
    
    def get_theme_path(self):
        """获取当前主题的路径"""
        theme = self.get("theme", "light")
        theme_dir = Path(__file__).parent.parent / "ui" / "themes"
        return theme_dir / f"{theme}.json"
    
    def get_language_file(self):
        """获取当前语言文件的路径"""
        language = self.get("language", "zh_CN")
        lang_dir = Path(__file__).parent.parent / "ui" / "languages"
        return lang_dir / f"{language}.json"
    
    def get_app_data_dir(self):
        """获取应用数据存储目录
        
        Returns:
            str: 应用数据存储目录路径
        """
        # 确保数据目录存在
        data_dir = self.config_dir / "data"
        data_dir.mkdir(exist_ok=True, parents=True)
        return str(data_dir) 