#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
番茄时钟模块UI实现
"""

import os
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from src.modules.pomodoro.pomodoro_module import PomodoroModule, TimerState

class SettingsDialog(ctk.CTkToplevel):
    """番茄时钟设置对话框"""
    def __init__(self, parent, pomodoro_module: PomodoroModule, callback: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.pomodoro_module = pomodoro_module
        self.callback = callback
        self.config = pomodoro_module.get_config()
        
        # 设置对话框属性
        self.title("番茄时钟设置")
        self.geometry("500x450")
        self.resizable(True, True)
        self.lift()  # 置于顶层
        self.grab_set()  # 模态对话框
        
        # 设置最小尺寸
        self.minsize(500, 450)
        
        # 创建UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 主容器
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="番茄时钟设置",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 设置项容器
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 时间设置
        time_frame = ctk.CTkFrame(settings_frame)
        time_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(time_frame, text="时间设置", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # 工作时长
        work_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        work_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(work_frame, text="工作时长 (分钟):").pack(side="left", padx=5)
        
        self.work_duration_var = ctk.StringVar(value=str(self.config["work_duration"] // 60))
        work_duration_entry = ctk.CTkEntry(work_frame, width=60, textvariable=self.work_duration_var)
        work_duration_entry.pack(side="left", padx=5)
        
        # 短休息时长
        short_break_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        short_break_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(short_break_frame, text="短休息时长 (分钟):").pack(side="left", padx=5)
        
        self.short_break_var = ctk.StringVar(value=str(self.config["short_break"] // 60))
        short_break_entry = ctk.CTkEntry(short_break_frame, width=60, textvariable=self.short_break_var)
        short_break_entry.pack(side="left", padx=5)
        
        # 长休息时长
        long_break_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        long_break_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(long_break_frame, text="长休息时长 (分钟):").pack(side="left", padx=5)
        
        self.long_break_var = ctk.StringVar(value=str(self.config["long_break"] // 60))
        long_break_entry = ctk.CTkEntry(long_break_frame, width=60, textvariable=self.long_break_var)
        long_break_entry.pack(side="left", padx=5)
        
        # 长休息前的工作周期数
        cycles_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        cycles_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(cycles_frame, text="长休息前的工作周期数:").pack(side="left", padx=5)
        
        self.cycles_var = ctk.StringVar(value=str(self.config["cycles_before_long_break"]))
        cycles_entry = ctk.CTkEntry(cycles_frame, width=60, textvariable=self.cycles_var)
        cycles_entry.pack(side="left", padx=5)
        
        # 自动化设置
        auto_frame = ctk.CTkFrame(settings_frame)
        auto_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(auto_frame, text="自动化设置", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # 自动开始休息
        self.auto_start_breaks_var = ctk.BooleanVar(value=self.config["auto_start_breaks"])
        auto_start_breaks_cb = ctk.CTkCheckBox(
            auto_frame,
            text="工作结束后自动开始休息",
            variable=self.auto_start_breaks_var
        )
        auto_start_breaks_cb.pack(anchor="w", padx=20, pady=5)
        
        # 自动开始工作
        self.auto_start_work_var = ctk.BooleanVar(value=self.config["auto_start_work"])
        auto_start_work_cb = ctk.CTkCheckBox(
            auto_frame,
            text="休息结束后自动开始工作",
            variable=self.auto_start_work_var
        )
        auto_start_work_cb.pack(anchor="w", padx=20, pady=5)
        
        # 通知设置
        notify_frame = ctk.CTkFrame(settings_frame)
        notify_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(notify_frame, text="通知设置", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # 声音提醒
        self.sound_enabled_var = ctk.BooleanVar(value=self.config["sound_enabled"])
        sound_enabled_cb = ctk.CTkCheckBox(
            notify_frame,
            text="启用声音提醒",
            variable=self.sound_enabled_var
        )
        sound_enabled_cb.pack(anchor="w", padx=20, pady=5)
        
        # 桌面通知
        self.notification_enabled_var = ctk.BooleanVar(value=self.config["notification_enabled"])
        notification_enabled_cb = ctk.CTkCheckBox(
            notify_frame,
            text="启用桌面通知",
            variable=self.notification_enabled_var
        )
        notification_enabled_cb.pack(anchor="w", padx=20, pady=5)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=15)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self.destroy,
            fg_color="#E76F51",
            width=100
        )
        cancel_button.pack(side="left", padx=10)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="保存",
            command=self._save_settings,
            fg_color="#2A9D8F",
            width=100
        )
        save_button.pack(side="right", padx=10)
    
    def _save_settings(self):
        """保存设置"""
        try:
            # 验证并获取输入值
            work_duration = int(self.work_duration_var.get()) * 60
            short_break = int(self.short_break_var.get()) * 60
            long_break = int(self.long_break_var.get()) * 60
            cycles = int(self.cycles_var.get())
            
            # 验证值的合法性
            if work_duration <= 0 or short_break <= 0 or long_break <= 0 or cycles <= 0:
                self._show_error("所有时间和周期数必须大于0")
                return
            
            # 创建新配置
            new_config = {
                "work_duration": work_duration,
                "short_break": short_break,
                "long_break": long_break,
                "cycles_before_long_break": cycles,
                "auto_start_breaks": self.auto_start_breaks_var.get(),
                "auto_start_work": self.auto_start_work_var.get(),
                "sound_enabled": self.sound_enabled_var.get(),
                "notification_enabled": self.notification_enabled_var.get()
            }
            
            # 更新配置
            if self.pomodoro_module.update_config(new_config):
                # 如果有回调函数，通知配置已更新
                if self.callback:
                    self.callback()
                
                # 关闭对话框
                self.destroy()
            else:
                self._show_error("保存配置失败")
                
        except ValueError:
            self._show_error("请输入有效的数字")
    
    def _show_error(self, message: str):
        """显示错误消息"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("错误")
        error_dialog.geometry("300x150")
        error_dialog.resizable(False, False)
        error_dialog.lift()
        error_dialog.grab_set()
        
        ctk.CTkLabel(
            error_dialog,
            text=message,
            font=("Helvetica", 12)
        ).pack(padx=20, pady=20)
        
        ctk.CTkButton(
            error_dialog,
            text="确定",
            command=error_dialog.destroy,
            width=80
        ).pack(pady=10)

class StatsDialog(ctk.CTkToplevel):
    """番茄时钟统计对话框"""
    def __init__(self, parent, pomodoro_module: PomodoroModule, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.pomodoro_module = pomodoro_module
        self.stats = pomodoro_module.get_stats()
        
        # 设置对话框属性
        self.title("番茄时钟统计")
        self.geometry("500x400")
        self.resizable(True, True)
        self.lift()  # 置于顶层
        self.grab_set()  # 模态对话框
        
        # 设置最小尺寸
        self.minsize(500, 400)
        
        # 创建UI
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 主容器
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="番茄时钟统计",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 统计信息容器
        stats_frame = ctk.CTkScrollableFrame(main_frame)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 总体统计
        overall_frame = ctk.CTkFrame(stats_frame)
        overall_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(overall_frame, text="总体统计", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # 总工作时间
        total_work_time = self.stats["total_work_time"]
        hours, remainder = divmod(total_work_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours}小时{minutes}分钟"
        
        ctk.CTkLabel(
            overall_frame,
            text=f"总工作时间: {time_str}"
        ).pack(anchor="w", padx=20, pady=2)
        
        # 总工作次数
        ctk.CTkLabel(
            overall_frame,
            text=f"总工作次数: {self.stats['total_work_sessions']}次"
        ).pack(anchor="w", padx=20, pady=2)
        
        # 完成的周期数
        ctk.CTkLabel(
            overall_frame,
            text=f"完成的周期数: {self.stats['completed_cycles']}个"
        ).pack(anchor="w", padx=20, pady=2)
        
        # 每日统计
        daily_frame = ctk.CTkFrame(stats_frame)
        daily_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(daily_frame, text="每日统计", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # 获取最近7天的日期
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        dates.reverse()  # 从最早的日期开始
        
        # 显示每日统计
        for date in dates:
            date_frame = ctk.CTkFrame(daily_frame, fg_color="transparent")
            date_frame.pack(fill="x", padx=10, pady=5)
            
            if date in self.stats["daily_stats"]:
                day_stats = self.stats["daily_stats"][date]
                
                # 计算当天工作时间
                work_time = day_stats["work_time"]
                hours, remainder = divmod(work_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours}小时{minutes}分钟"
                
                # 构建显示文本
                display_text = f"{date}: 工作{day_stats['work_sessions']}次 ({time_str}), "
                display_text += f"短休息{day_stats['short_breaks']}次, 长休息{day_stats['long_breaks']}次"
                
                ctk.CTkLabel(
                    date_frame,
                    text=display_text
                ).pack(anchor="w")
            else:
                ctk.CTkLabel(
                    date_frame,
                    text=f"{date}: 无记录",
                    text_color="gray"
                ).pack(anchor="w")
        
        # 按钮区域
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=15)
        
        close_button = ctk.CTkButton(
            button_frame,
            text="关闭",
            command=self.destroy,
            width=100
        )
        close_button.pack(side="right", padx=10)

class PomodoroUI(ctk.CTkFrame):
    """番茄时钟模块主UI类"""
    def __init__(self, master, config_manager, **kwargs):
        super().__init__(master, **kwargs)
        
        self.logger = logging.getLogger("左拾月.番茄时钟UI")
        
        # 初始化数据模块
        data_dir = Path(config_manager.get_app_data_dir()) / "pomodoro"
        self.pomodoro_module = PomodoroModule(data_dir)
        
        # 设置回调函数
        self.pomodoro_module.on_tick = self._on_tick
        self.pomodoro_module.on_complete = self._on_complete
        self.pomodoro_module.on_state_change = self._on_state_change
        
        # 创建UI布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI布局"""
        # 设置最小尺寸，确保窗口有足够的空间
        self.configure(width=800, height=600)
        
        # 主容器
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 顶部标题区域
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="左拾月番茄时钟",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # 设置按钮
        settings_button = ctk.CTkButton(
            header_frame,
            text="设置",
            width=80,
            command=self._open_settings
        )
        settings_button.pack(side="right", padx=10)
        
        # 统计按钮
        stats_button = ctk.CTkButton(
            header_frame,
            text="统计",
            width=80,
            command=self._open_stats
        )
        stats_button.pack(side="right", padx=10)
        
        # 计时器区域
        timer_frame = ctk.CTkFrame(main_frame)
        timer_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 状态标签
        self.state_label = ctk.CTkLabel(
            timer_frame,
            text="准备开始",
            font=("Helvetica", 18)
        )
        self.state_label.pack(pady=(20, 10))
        
        # 时间显示
        self.time_label = ctk.CTkLabel(
            timer_frame,
            text="25:00",
            font=("Helvetica", 72, "bold")
        )
        self.time_label.pack(pady=20)
        
        # 周期指示器
        self.cycle_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        self.cycle_frame.pack(pady=10)
        
        self.cycle_indicators = []
        for i in range(4):  # 默认显示4个周期指示器
            indicator = ctk.CTkLabel(
                self.cycle_frame,
                text="○",  # 空心圆表示未完成
                font=("Helvetica", 18),
                text_color="gray"
            )
            indicator.pack(side="left", padx=5)
            self.cycle_indicators.append(indicator)
        
        # 控制按钮区域
        control_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        control_frame.pack(pady=30)
        
        # 开始工作按钮
        self.start_work_button = ctk.CTkButton(
            control_frame,
            text="开始工作",
            width=120,
            height=40,
            fg_color="#2A9D8F",
            command=self._start_work
        )
        self.start_work_button.pack(side="left", padx=10)
        
        # 开始休息按钮
        self.start_break_button = ctk.CTkButton(
            control_frame,
            text="开始休息",
            width=120,
            height=40,
            fg_color="#E9C46A",
            text_color="black",
            command=self._start_break
        )
        self.start_break_button.pack(side="left", padx=10)
        
        # 暂停/继续按钮
        self.pause_resume_button = ctk.CTkButton(
            control_frame,
            text="暂停",
            width=120,
            height=40,
            fg_color="#E76F51",
            command=self._pause_resume
        )
        self.pause_resume_button.pack(side="left", padx=10)
        
        # 重置按钮
        self.reset_button = ctk.CTkButton(
            control_frame,
            text="重置",
            width=120,
            height=40,
            fg_color="#264653",
            command=self._reset
        )
        self.reset_button.pack(side="left", padx=10)
        
        # 提示区域
        tip_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        tip_frame.pack(fill="x", pady=10)
        
        self.tip_label = ctk.CTkLabel(
            tip_frame,
            text="提示: 番茄工作法是一种时间管理方法，使用番茄时钟来分割工作和休息时间。",
            font=("Helvetica", 12),
            text_color="gray"
        )
        self.tip_label.pack(pady=5)
        
        # 更新UI状态
        self._update_ui_state()
    
    def _update_ui_state(self):
        """根据当前状态更新UI"""
        state = self.pomodoro_module.state
        config = self.pomodoro_module.get_config()
        
        # 更新状态标签
        if state == TimerState.IDLE:
            self.state_label.configure(text="准备开始")
            self.time_label.configure(text=self.pomodoro_module.format_time(config["work_duration"]))
        elif state == TimerState.WORKING:
            self.state_label.configure(text="工作中")
        elif state == TimerState.RESTING:
            self.state_label.configure(text="休息中")
        elif state == TimerState.PAUSED:
            if hasattr(self, '_last_state') and self._last_state == TimerState.WORKING:
                self.state_label.configure(text="工作已暂停")
            else:
                self.state_label.configure(text="休息已暂停")
        
        # 更新按钮状态
        if state == TimerState.IDLE:
            self.start_work_button.configure(state="normal")
            self.start_break_button.configure(state="normal")
            self.pause_resume_button.configure(state="disabled", text="暂停")
            self.reset_button.configure(state="disabled")
        elif state == TimerState.WORKING or state == TimerState.RESTING:
            self.start_work_button.configure(state="disabled")
            self.start_break_button.configure(state="disabled")
            self.pause_resume_button.configure(state="normal", text="暂停")
            self.reset_button.configure(state="normal")
        elif state == TimerState.PAUSED:
            self.start_work_button.configure(state="disabled")
            self.start_break_button.configure(state="disabled")
            self.pause_resume_button.configure(state="normal", text="继续")
            self.reset_button.configure(state="normal")
        
        # 更新周期指示器
        current_cycle = self.pomodoro_module.current_cycle
        cycles_before_long_break = config["cycles_before_long_break"]
        
        # 确保有足够的指示器
        while len(self.cycle_indicators) < cycles_before_long_break:
            indicator = ctk.CTkLabel(
                self.cycle_frame,
                text="○",  # 空心圆表示未完成
                font=("Helvetica", 18),
                text_color="gray"
            )
            indicator.pack(side="left", padx=5)
            self.cycle_indicators.append(indicator)
        
        # 更新指示器状态
        for i, indicator in enumerate(self.cycle_indicators):
            if i < current_cycle:
                indicator.configure(text="●", text_color="#2A9D8F")  # 实心圆表示已完成
            else:
                indicator.configure(text="○", text_color="gray")  # 空心圆表示未完成
    
    def _on_tick(self, time_left: int):
        """计时器滴答回调"""
        self.time_label.configure(text=self.pomodoro_module.format_time(time_left))
    
    def _on_complete(self, session_type: str):
        """计时完成回调"""
        if session_type == "work":
            self.tip_label.configure(text="工作时间结束！休息一下吧。")
        elif session_type == "short_break":
            self.tip_label.configure(text="短休息结束！准备开始新的工作周期。")
        elif session_type == "long_break":
            self.tip_label.configure(text="长休息结束！你已完成一个完整的番茄周期，做得很好！")
        
        # 更新UI状态
        self._update_ui_state()
    
    def _on_state_change(self, new_state: TimerState, old_state: TimerState = None):
        """状态变化回调"""
        self._last_state = old_state
        
        # 更新提示
        if new_state == TimerState.WORKING:
            self.tip_label.configure(text="专注工作中，避免分心...")
        elif new_state == TimerState.RESTING:
            self.tip_label.configure(text="休息时间，放松一下...")
        elif new_state == TimerState.PAUSED:
            self.tip_label.configure(text="计时已暂停，随时可以继续...")
        elif new_state == TimerState.IDLE:
            self.tip_label.configure(text="准备好了吗？点击\"开始工作\"按钮开始一个新的番茄周期。")
        
        # 更新UI状态
        self._update_ui_state()
    
    def _start_work(self):
        """开始工作"""
        self.pomodoro_module.start_work()
    
    def _start_break(self):
        """开始休息"""
        self.pomodoro_module.start_break()
    
    def _pause_resume(self):
        """暂停/继续"""
        if self.pomodoro_module.state == TimerState.PAUSED:
            self.pomodoro_module.resume()
        else:
            self.pomodoro_module.pause()
    
    def _reset(self):
        """重置"""
        self.pomodoro_module.reset()
    
    def _open_settings(self):
        """打开设置对话框"""
        SettingsDialog(self, self.pomodoro_module, self._on_settings_updated)
    
    def _on_settings_updated(self):
        """设置更新回调"""
        # 更新UI状态
        self._update_ui_state()
        
        # 更新提示
        self.tip_label.configure(text="设置已更新！")
    
    def _open_stats(self):
        """打开统计对话框"""
        StatsDialog(self, self.pomodoro_module)
    
    def on_close(self):
        """关闭时调用"""
        if hasattr(self, 'pomodoro_module'):
            self.pomodoro_module.close() 