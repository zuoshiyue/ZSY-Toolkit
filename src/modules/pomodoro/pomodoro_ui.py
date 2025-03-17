#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
番茄时钟模块UI
"""

import customtkinter as ctk
import logging
import time
from typing import Optional, Callable

class PomodoroUI(ctk.CTkFrame):
    """番茄时钟模块UI类"""
    
    def __init__(self, master, platform_adapter, config_manager):
        super().__init__(master)
        self.logger = logging.getLogger("左拾月.番茄时钟")
        self.platform_adapter = platform_adapter
        self.config_manager = config_manager
        
        # 初始化变量
        self.is_running = False
        self.remaining_time = 25 * 60  # 默认25分钟
        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.long_break_time = 15 * 60
        self.pomodoro_count = 0
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建计时器框架
        timer_frame = ctk.CTkFrame(self)
        timer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        timer_frame.grid_columnconfigure(0, weight=1)
        
        # 计时器显示
        self.time_label = ctk.CTkLabel(
            timer_frame,
            text="25:00",
            font=ctk.CTkFont(size=48, weight="bold")
        )
        self.time_label.grid(row=0, column=0, padx=10, pady=20)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            timer_frame,
            text="准备开始",
            font=ctk.CTkFont(size=16)
        )
        self.status_label.grid(row=1, column=0, padx=10, pady=5)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(timer_frame)
        button_frame.grid(row=2, column=0, padx=10, pady=10)
        
        # 开始/暂停按钮
        self.start_button = ctk.CTkButton(
            button_frame,
            text="开始",
            command=self._toggle_timer,
            font=("微软雅黑", 12)
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        # 重置按钮
        reset_button = ctk.CTkButton(
            button_frame,
            text="重置",
            command=self._reset_timer,
            font=("微软雅黑", 12)
        )
        reset_button.grid(row=0, column=1, padx=5, pady=5)
        
        # 设置框架
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        settings_frame.grid_columnconfigure(0, weight=1)
        
        # 设置标题
        settings_label = ctk.CTkLabel(
            settings_frame,
            text="设置",
            font=("微软雅黑", 16, "bold")
        )
        settings_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 工作时间设置
        work_frame = ctk.CTkFrame(settings_frame)
        work_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        work_label = ctk.CTkLabel(
            work_frame,
            text="工作时间(分钟):",
            font=("微软雅黑", 12)
        )
        work_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.work_entry = ctk.CTkEntry(
            work_frame,
            width=60,
            font=("微软雅黑", 12)
        )
        self.work_entry.grid(row=0, column=1, padx=5, pady=5)
        self.work_entry.insert(0, "25")
        
        # 休息时间设置
        break_frame = ctk.CTkFrame(settings_frame)
        break_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        break_label = ctk.CTkLabel(
            break_frame,
            text="休息时间(分钟):",
            font=("微软雅黑", 12)
        )
        break_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.break_entry = ctk.CTkEntry(
            break_frame,
            width=60,
            font=("微软雅黑", 12)
        )
        self.break_entry.grid(row=0, column=1, padx=5, pady=5)
        self.break_entry.insert(0, "5")
        
        # 长休息时间设置
        long_break_frame = ctk.CTkFrame(settings_frame)
        long_break_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        long_break_label = ctk.CTkLabel(
            long_break_frame,
            text="长休息时间(分钟):",
            font=("微软雅黑", 12)
        )
        long_break_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.long_break_entry = ctk.CTkEntry(
            long_break_frame,
            width=60,
            font=("微软雅黑", 12)
        )
        self.long_break_entry.grid(row=0, column=1, padx=5, pady=5)
        self.long_break_entry.insert(0, "15")
        
        # 应用设置按钮
        apply_button = ctk.CTkButton(
            settings_frame,
            text="应用设置",
            command=self._apply_settings,
            font=("微软雅黑", 12)
        )
        apply_button.grid(row=4, column=0, padx=10, pady=10)
        
    def _toggle_timer(self):
        """切换计时器状态"""
        if self.is_running:
            self._pause_timer()
        else:
            self._start_timer()
            
    def _start_timer(self):
        """开始计时"""
        self.is_running = True
        self.start_button.configure(text="暂停")
        self._update_timer()
        
    def _pause_timer(self):
        """暂停计时"""
        self.is_running = False
        self.start_button.configure(text="开始")
        
    def _reset_timer(self):
        """重置计时器"""
        self.is_running = False
        self.start_button.configure(text="开始")
        self.remaining_time = self.work_time
        self.status_label.configure(text="工作时间")
        self._update_display()
        
    def _update_timer(self):
        """更新计时器"""
        if self.is_running and self.remaining_time > 0:
            self.remaining_time -= 1
            self._update_display()
            self.after(1000, self._update_timer)
        elif self.remaining_time == 0:
            self._on_timer_complete()
            
    def _update_display(self):
        """更新显示"""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")
        
    def _on_timer_complete(self):
        """计时完成处理"""
        self.is_running = False
        self.start_button.configure(text="开始")
        
        # 播放提示音
        self._play_notification()
        
        # 更新番茄钟计数
        self.pomodoro_count += 1
        
        # 根据计数决定休息时间
        if self.pomodoro_count % 4 == 0:
            self.remaining_time = self.long_break_time
            self.status_label.configure(text="长休息时间")
        else:
            self.remaining_time = self.break_time
            self.status_label.configure(text="休息时间")
            
        self._update_display()
        
        # 自动开始下一个阶段
        self._start_timer()
        
    def _play_notification(self):
        """播放提示音"""
        try:
            platform = self.platform_adapter.platform
            if platform == "windows":
                import winsound
                winsound.Beep(1000, 1000)  # 频率1000Hz，持续1秒
            elif platform == "macos":
                import os
                os.system("afplay /System/Library/Sounds/Glass.aiff")
            elif platform == "linux":
                import os
                os.system("aplay /usr/share/sounds/freedesktop/stereo/complete.oga")
        except Exception as e:
            self.logger.error(f"播放提示音失败: {str(e)}")
            
    def _apply_settings(self):
        """应用设置"""
        try:
            # 获取设置值
            work_time = int(self.work_entry.get()) * 60
            break_time = int(self.break_entry.get()) * 60
            long_break_time = int(self.long_break_entry.get()) * 60
            
            # 更新设置
            self.work_time = work_time
            self.break_time = break_time
            self.long_break_time = long_break_time
            
            # 如果当前是工作时间，更新剩余时间
            if self.status_label.cget("text") == "工作时间":
                self.remaining_time = work_time
                self._update_display()
                
            self.logger.info("设置已应用")
        except ValueError:
            self.logger.error("设置值无效")
        except Exception as e:
            self.logger.error(f"应用设置失败: {str(e)}") 