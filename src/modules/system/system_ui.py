#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统控制模块UI
"""

import customtkinter as ctk
import logging
from typing import Optional, Callable

class SystemUI(ctk.CTkFrame):
    """系统控制模块UI类"""
    
    def __init__(self, master, platform_adapter, config_manager):
        super().__init__(master)
        self.logger = logging.getLogger("左拾月.系统控制")
        self.platform_adapter = platform_adapter
        self.config_manager = config_manager
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建显示器控制框架
        display_frame = ctk.CTkFrame(self)
        display_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)
        
        # 显示器控制标题
        title_label = ctk.CTkLabel(display_frame, text="显示器控制", font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 显示器模式切换按钮
        mode_button = ctk.CTkButton(
            display_frame,
            text="切换显示器模式",
            command=self._toggle_display_mode,
            font=("微软雅黑", 12)
        )
        mode_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # 显示器旋转按钮
        rotate_button = ctk.CTkButton(
            display_frame,
            text="旋转第二屏",
            command=self._rotate_display,
            font=("微软雅黑", 12)
        )
        rotate_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # 创建电源控制框架
        power_frame = ctk.CTkFrame(self)
        power_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        power_frame.grid_columnconfigure(0, weight=1)
        
        # 电源控制标题
        title_label = ctk.CTkLabel(power_frame, text="电源控制", font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 关机按钮
        shutdown_button = ctk.CTkButton(
            power_frame,
            text="关机",
            command=self._shutdown,
            font=("微软雅黑", 12)
        )
        shutdown_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # 重启按钮
        restart_button = ctk.CTkButton(
            power_frame,
            text="重启",
            command=self._restart,
            font=("微软雅黑", 12)
        )
        restart_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # 创建音频控制框架
        audio_frame = ctk.CTkFrame(self)
        audio_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        audio_frame.grid_columnconfigure(0, weight=1)
        
        # 音频控制标题
        title_label = ctk.CTkLabel(audio_frame, text="音频控制", font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 音量控制滑块
        self.volume_slider = ctk.CTkSlider(
            audio_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._set_volume
        )
        self.volume_slider.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.volume_slider.set(50)  # 默认音量50%
        
        # 静音按钮
        mute_button = ctk.CTkButton(
            audio_frame,
            text="静音",
            command=self._toggle_mute,
            font=("微软雅黑", 12)
        )
        mute_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
    def _toggle_display_mode(self):
        """切换显示器模式"""
        try:
            if self.platform_adapter.handle_command("toggle_display_mode"):
                self.logger.info("显示器模式切换成功")
            else:
                self.logger.error("显示器模式切换失败")
        except Exception as e:
            self.logger.error(f"切换显示器模式时发生错误: {str(e)}")
            
    def _rotate_display(self):
        """旋转第二屏"""
        try:
            if self.platform_adapter.handle_command("rotate_display"):
                self.logger.info("显示器旋转成功")
            else:
                self.logger.error("显示器旋转失败")
        except Exception as e:
            self.logger.error(f"旋转显示器时发生错误: {str(e)}")
            
    def _shutdown(self):
        """关机"""
        try:
            if self.platform_adapter.handle_command("shutdown"):
                self.logger.info("关机命令已发送")
            else:
                self.logger.error("关机命令发送失败")
        except Exception as e:
            self.logger.error(f"发送关机命令时发生错误: {str(e)}")
            
    def _restart(self):
        """重启"""
        try:
            if self.platform_adapter.handle_command("restart"):
                self.logger.info("重启命令已发送")
            else:
                self.logger.error("重启命令发送失败")
        except Exception as e:
            self.logger.error(f"发送重启命令时发生错误: {str(e)}")
            
    def _set_volume(self, value):
        """设置音量"""
        try:
            if self.platform_adapter.handle_command("set_volume", {"level": int(value)}):
                self.logger.info(f"音量已设置为: {value}%")
            else:
                self.logger.error("设置音量失败")
        except Exception as e:
            self.logger.error(f"设置音量时发生错误: {str(e)}")
            
    def _toggle_mute(self):
        """切换静音状态"""
        try:
            if self.platform_adapter.handle_command("toggle_mute"):
                self.logger.info("静音状态已切换")
            else:
                self.logger.error("切换静音状态失败")
        except Exception as e:
            self.logger.error(f"切换静音状态时发生错误: {str(e)}") 