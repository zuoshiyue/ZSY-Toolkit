#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
番茄时钟模块核心功能
"""

import os
import json
import time
import logging
import threading
from enum import Enum
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path

class TimerState(Enum):
    """计时器状态枚举"""
    IDLE = 0      # 空闲状态
    WORKING = 1   # 工作状态
    RESTING = 2   # 休息状态
    PAUSED = 3    # 暂停状态

class PomodoroModule:
    """番茄时钟模块主类"""
    
    def __init__(self, data_dir: Path):
        """初始化番茄时钟模块
        
        Args:
            data_dir: 数据存储目录
        """
        self.logger = logging.getLogger("左拾月.番茄时钟")
        
        # 确保数据目录存在
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.config_file = self.data_dir / "pomodoro_config.json"
        
        # 默认配置
        self.default_config = {
            "work_duration": 25 * 60,    # 工作时长（秒）
            "short_break": 5 * 60,       # 短休息时长（秒）
            "long_break": 15 * 60,       # 长休息时长（秒）
            "cycles_before_long_break": 4,  # 长休息前的工作周期数
            "auto_start_breaks": True,   # 自动开始休息
            "auto_start_work": False,    # 自动开始工作
            "sound_enabled": True,       # 声音提醒
            "notification_enabled": True # 通知提醒
        }
        
        # 加载配置
        self.config = self._load_config()
        
        # 统计数据
        self.stats_file = self.data_dir / "pomodoro_stats.json"
        self.stats = self._load_stats()
        
        # 计时器状态
        self.state = TimerState.IDLE
        self.current_cycle = 0
        self.time_left = 0
        self.timer_thread = None
        self.stop_timer = threading.Event()
        
        # 回调函数
        self.on_tick = None
        self.on_complete = None
        self.on_state_change = None
        
        self.logger.info("番茄时钟模块已初始化")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # 确保所有默认配置项都存在
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                self.logger.error(f"加载配置失败: {str(e)}")
        
        # 如果配置文件不存在或加载失败，创建默认配置
        self._save_config(self.default_config)
        return self.default_config.copy()
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """更新配置"""
        # 更新配置
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value
        
        # 保存配置
        return self._save_config(self.config)
    
    def _load_stats(self) -> Dict[str, Any]:
        """加载统计数据"""
        default_stats = {
            "total_work_sessions": 0,
            "total_work_time": 0,
            "completed_cycles": 0,
            "daily_stats": {},
            "last_updated": datetime.now().isoformat()
        }
        
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    stats = json.load(f)
                    # 确保所有默认统计项都存在
                    for key, value in default_stats.items():
                        if key not in stats:
                            stats[key] = value
                    return stats
            except Exception as e:
                self.logger.error(f"加载统计数据失败: {str(e)}")
        
        # 如果统计文件不存在或加载失败，创建默认统计
        self._save_stats(default_stats)
        return default_stats.copy()
    
    def _save_stats(self, stats: Dict[str, Any]) -> bool:
        """保存统计数据"""
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"保存统计数据失败: {str(e)}")
            return False
    
    def _update_stats(self, session_type: str, duration: int) -> None:
        """更新统计数据
        
        Args:
            session_type: 会话类型 ('work', 'short_break', 'long_break')
            duration: 持续时间（秒）
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 更新每日统计
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {
                "work_sessions": 0,
                "work_time": 0,
                "short_breaks": 0,
                "long_breaks": 0
            }
        
        if session_type == "work":
            self.stats["total_work_sessions"] += 1
            self.stats["total_work_time"] += duration
            self.stats["daily_stats"][today]["work_sessions"] += 1
            self.stats["daily_stats"][today]["work_time"] += duration
            
            # 如果完成了一个完整的工作周期
            if self.current_cycle % self.config["cycles_before_long_break"] == 0:
                self.stats["completed_cycles"] += 1
        
        elif session_type == "short_break":
            self.stats["daily_stats"][today]["short_breaks"] += 1
        
        elif session_type == "long_break":
            self.stats["daily_stats"][today]["long_breaks"] += 1
        
        # 更新最后更新时间
        self.stats["last_updated"] = datetime.now().isoformat()
        
        # 保存统计数据
        self._save_stats(self.stats)
    
    def start_work(self) -> bool:
        """开始工作计时"""
        if self.state != TimerState.IDLE and self.state != TimerState.PAUSED:
            return False
        
        # 设置工作时长
        self.time_left = self.config["work_duration"]
        
        # 更新状态
        old_state = self.state
        self.state = TimerState.WORKING
        
        # 如果是从暂停状态恢复，不增加周期计数
        if old_state != TimerState.PAUSED:
            self.current_cycle += 1
        
        # 启动计时器
        self._start_timer()
        
        # 通知状态变化
        if self.on_state_change:
            self.on_state_change(self.state)
        
        self.logger.info(f"开始工作计时，周期 {self.current_cycle}")
        return True
    
    def start_break(self, force_long: bool = False) -> bool:
        """开始休息计时
        
        Args:
            force_long: 是否强制使用长休息
        """
        if self.state != TimerState.IDLE and self.state != TimerState.PAUSED:
            return False
        
        # 确定是短休息还是长休息
        is_long_break = force_long or (self.current_cycle % self.config["cycles_before_long_break"] == 0)
        
        # 设置休息时长
        if is_long_break:
            self.time_left = self.config["long_break"]
            break_type = "long_break"
        else:
            self.time_left = self.config["short_break"]
            break_type = "short_break"
        
        # 更新状态
        self.state = TimerState.RESTING
        
        # 启动计时器
        self._start_timer(break_type)
        
        # 通知状态变化
        if self.on_state_change:
            self.on_state_change(self.state)
        
        self.logger.info(f"开始{'长' if is_long_break else '短'}休息计时")
        return True
    
    def pause(self) -> bool:
        """暂停计时"""
        if self.state != TimerState.WORKING and self.state != TimerState.RESTING:
            return False
        
        # 停止计时器
        self.stop_timer.set()
        if self.timer_thread:
            self.timer_thread.join()
            self.timer_thread = None
        
        # 更新状态
        old_state = self.state
        self._last_state = old_state  # 保存当前状态，以便恢复时使用
        self.state = TimerState.PAUSED
        
        # 通知状态变化
        if self.on_state_change:
            self.on_state_change(self.state, old_state)
        
        self.logger.info("暂停计时")
        return True
    
    def resume(self) -> bool:
        """恢复计时"""
        if self.state != TimerState.PAUSED:
            return False
        
        # 确定恢复到哪种状态
        if hasattr(self, '_last_state') and self._last_state:
            new_state = self._last_state
            
            # 根据状态启动相应的计时器
            if new_state == TimerState.WORKING:
                # 恢复工作状态
                self.state = TimerState.WORKING
                session_type = "work"
            else:
                # 恢复休息状态
                self.state = TimerState.RESTING
                # 判断是长休息还是短休息
                if self.current_cycle % self.config["cycles_before_long_break"] == 0:
                    session_type = "long_break"
                else:
                    session_type = "short_break"
            
            # 启动计时器
            self._start_timer(session_type)
            
            # 通知状态变化
            if self.on_state_change:
                self.on_state_change(self.state)
            
            self.logger.info(f"恢复计时，状态: {self.state}")
            return True
        else:
            # 如果没有保存之前的状态，默认恢复到工作状态
            return self.start_work()
    
    def stop(self) -> bool:
        """停止计时"""
        # 停止计时器
        self.stop_timer.set()
        if self.timer_thread:
            self.timer_thread.join()
            self.timer_thread = None
        
        # 更新状态
        old_state = self.state
        self.state = TimerState.IDLE
        
        # 通知状态变化
        if self.on_state_change:
            self.on_state_change(self.state, old_state)
        
        self.logger.info("停止计时")
        return True
    
    def reset(self) -> bool:
        """重置计时器"""
        # 停止计时
        self.stop()
        
        # 重置状态
        self.current_cycle = 0
        self.time_left = 0
        
        self.logger.info("重置计时器")
        return True
    
    def _start_timer(self, session_type: str = "work") -> None:
        """启动计时器线程
        
        Args:
            session_type: 会话类型 ('work', 'short_break', 'long_break')
        """
        # 停止现有计时器
        self.stop_timer.set()
        if self.timer_thread:
            self.timer_thread.join()
        
        # 重置停止标志
        self.stop_timer.clear()
        
        # 创建新的计时器线程
        self.timer_thread = threading.Thread(
            target=self._timer_loop,
            args=(session_type,),
            daemon=True
        )
        self.timer_thread.start()
    
    def _timer_loop(self, session_type: str) -> None:
        """计时器循环
        
        Args:
            session_type: 会话类型 ('work', 'short_break', 'long_break')
        """
        start_time = time.time()
        original_duration = self.time_left
        
        while self.time_left > 0 and not self.stop_timer.is_set():
            # 使用非阻塞的方式等待，每0.1秒检查一次停止标志
            if self.stop_timer.wait(0.1):
                break
            
            # 计算经过的时间
            elapsed = time.time() - start_time
            self.time_left = max(0, original_duration - int(elapsed))
            
            # 通知时间变化
            if self.on_tick:
                self.on_tick(self.time_left)
        
        # 如果不是被中断的，则完成计时
        if not self.stop_timer.is_set():
            # 更新统计数据
            self._update_stats(session_type, original_duration)
            
            # 通知完成
            if self.on_complete:
                self.on_complete(session_type)
            
            # 自动开始下一个阶段
            if session_type == "work":
                # 工作结束后，如果启用了自动开始休息
                if self.config["auto_start_breaks"]:
                    self.start_break()
                else:
                    self.state = TimerState.IDLE
                    if self.on_state_change:
                        self.on_state_change(self.state)
            else:
                # 休息结束后，如果启用了自动开始工作
                if self.config["auto_start_work"]:
                    self.start_work()
                else:
                    self.state = TimerState.IDLE
                    if self.on_state_change:
                        self.on_state_change(self.state)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据"""
        return self.stats.copy()
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config.copy()
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "state": self.state,
            "current_cycle": self.current_cycle,
            "time_left": self.time_left
        }
    
    def format_time(self, seconds: int) -> str:
        """格式化时间
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化后的时间字符串 (MM:SS)
        """
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def close(self) -> None:
        """关闭模块"""
        # 停止计时器
        self.stop()
        self.logger.info("番茄时钟模块已关闭") 