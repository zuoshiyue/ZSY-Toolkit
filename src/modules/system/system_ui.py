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
        
        # 获取当前系统音量
        try:
            current_volume = self.platform_adapter.handle_command("get_volume")
            self.initial_volume = current_volume if current_volume is not None else 50
        except Exception as e:
            self.logger.error(f"获取系统音量时发生错误: {str(e)}")
            self.initial_volume = 50
        
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI界面"""
        # 主容器
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # 系统信息区域
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 30))
        
        # 系统信息标题
        ctk.CTkLabel(
            info_frame,
            text="系统信息",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 5))
        
        # 系统信息文本框
        self.info_text = ctk.CTkTextbox(
            info_frame,
            height=200,
            font=("Consolas", 12)
        )
        self.info_text.pack(fill="x", padx=20, pady=(0, 10))
        
        # 刷新按钮
        ctk.CTkButton(
            info_frame,
            text="刷新",
            width=100,
            command=self._refresh_system_info
        ).pack(pady=(0, 10))
        
        # 系统控制区域
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", pady=(0, 30))
        
        # 系统控制标题
        ctk.CTkLabel(
            control_frame,
            text="系统控制",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 5))
        
        # 音量控制区域
        volume_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        volume_frame.pack(fill="x", padx=20, pady=5)
        
        # 音量控制标题行
        volume_title_frame = ctk.CTkFrame(volume_frame, fg_color="transparent")
        volume_title_frame.pack(fill="x", pady=(0, 5))
        
        # 音量标签
        ctk.CTkLabel(
            volume_title_frame,
            text="音量控制",
            font=("Helvetica", 14)
        ).pack(side="left", padx=(0, 10))
        
        # 音量合成器按钮
        mixer_button = ctk.CTkButton(
            volume_title_frame,
            text="音量合成器",
            width=120,
            command=self._open_volume_mixer,
            font=("Helvetica", 12)
        )
        mixer_button.pack(side="right", padx=(10, 0))
        
        # 音量滑块行
        volume_slider_frame = ctk.CTkFrame(volume_frame, fg_color="transparent")
        volume_slider_frame.pack(fill="x", pady=(0, 5))
        
        # 音量滑块
        self.volume_slider = ctk.CTkSlider(
            volume_slider_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._set_volume
        )
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 音量值显示
        self.volume_label = ctk.CTkLabel(
            volume_slider_frame,
            text="50%",
            font=("Helvetica", 14)
        )
        self.volume_label.pack(side="right")
        
        # 系统操作区域
        system_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        system_frame.pack(fill="x", padx=20, pady=5)
        
        # 关机按钮
        ctk.CTkButton(
            system_frame,
            text="关机",
            width=100,
            fg_color="#E76F51",
            hover_color="#C65D42",
            command=self._shutdown
        ).pack(side="left", padx=5)
        
        # 重启按钮
        ctk.CTkButton(
            system_frame,
            text="重启",
            width=100,
            fg_color="#E76F51",
            hover_color="#C65D42",
            command=self._restart
        ).pack(side="left", padx=5)
        
        # 睡眠按钮
        ctk.CTkButton(
            system_frame,
            text="睡眠",
            width=100,
            fg_color="#E76F51",
            hover_color="#C65D42",
            command=self._sleep
        ).pack(side="left", padx=5)
        
        # 显示器控制区域
        display_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        display_frame.pack(fill="x", padx=20, pady=5)
        
        # 显示器控制标题
        ctk.CTkLabel(
            display_frame,
            text="显示器控制",
            font=("Helvetica", 14)
        ).pack(side="left", padx=(0, 10))
        
        # 显示器模式按钮
        ctk.CTkButton(
            display_frame,
            text="切换显示器模式",
            width=120,
            command=self._toggle_display_mode
        ).pack(side="left", padx=5)
        
        # 显示器旋转按钮
        ctk.CTkButton(
            display_frame,
            text="旋转显示器",
            width=120,
            command=self._rotate_display
        ).pack(side="left", padx=5)
        
        # 初始化系统信息
        self._refresh_system_info()
        
        # 获取当前系统音量
        try:
            current_volume = self.platform_adapter.handle_command("get_volume")
            if current_volume is not None:
                self.volume_slider.set(current_volume)
                self.volume_label.configure(text=f"{current_volume}%")
        except Exception as e:
            self.logger.error(f"获取系统音量失败：{str(e)}")
        
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
            
    def _open_volume_mixer(self):
        """打开系统音量合成器"""
        try:
            if self.platform_adapter.open_volume_mixer():
                self.logger.info("已打开系统音量合成器")
            else:
                self.logger.error("打开系统音量合成器失败")
        except Exception as e:
            self.logger.error(f"打开系统音量合成器时发生错误：{str(e)}") 