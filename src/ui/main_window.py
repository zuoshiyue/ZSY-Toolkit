#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块
实现应用程序的主界面
"""

import os
import sys
import logging
import platform
from pathlib import Path
from PIL import Image, ImageTk

try:
    import customtkinter as ctk
except ImportError:
    logging.error("缺少customtkinter库，请安装: pip install customtkinter")
    sys.exit(1)

class MainWindow:
    """应用程序主窗口类"""
    
    def __init__(self, app_manager):
        """初始化主窗口
        
        Args:
            app_manager: 应用管理器实例
        """
        self.logger = logging.getLogger("左拾月.主窗口")
        self.app_manager = app_manager
        self.config_manager = app_manager.config_manager
        
        # 设置主题
        self._setup_theme()
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("左拾月 - 个人助手工具")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # 设置图标
        self._setup_icon()
        
        # 创建UI组件
        self._create_widgets()
        
        # 绑定事件
        self._bind_events()
        
        # 初始化模块
        self.app_manager.initialize_modules()
        
        # 加载模块UI
        self._load_module_tabs()
        
        self.logger.info("主窗口已初始化")
    
    def _setup_theme(self):
        """设置应用主题"""
        theme = self.config_manager.get("theme", "light")
        if theme == "light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")  # 默认使用蓝色主题
    
    def _setup_icon(self):
        """设置应用图标"""
        try:
            icon_path = Path(__file__).parent / "assets" / "icon.png"
            if icon_path.exists():
                if platform.system() == "Windows":
                    self.root.iconbitmap(icon_path)
                else:
                    icon = ImageTk.PhotoImage(Image.open(icon_path))
                    self.root.iconphoto(True, icon)
        except Exception as e:
            self.logger.error(f"设置图标失败: {str(e)}")
    
    def _create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建标题栏
        self.title_frame = ctk.CTkFrame(self.main_frame, height=50)
        self.title_frame.pack(fill="x", padx=5, pady=5)
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="左拾月 - 个人助手工具", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(side="left", padx=10)
        
        # 主题切换按钮
        self.theme_button = ctk.CTkButton(
            self.title_frame,
            text="切换主题",
            width=100,
            command=self._toggle_theme
        )
        self.theme_button.pack(side="right", padx=10)
        
        # 创建选项卡控件
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 添加基本选项卡
        self.system_tab = self.tab_view.add("系统控制")
        self.todo_tab = self.tab_view.add("Todo清单")
        self.pomodoro_tab = self.tab_view.add("番茄时钟")
        self.launcher_tab = self.tab_view.add("应用启动")
        self.games_tab = self.tab_view.add("游戏空间")
        
        # 创建状态栏
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30)
        self.status_frame.pack(fill="x", padx=5, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)
        
        platform_name = self.app_manager.platform_adapter.get_platform_name()
        self.platform_label = ctk.CTkLabel(
            self.status_frame,
            text=f"平台: {platform_name}",
            font=ctk.CTkFont(size=12)
        )
        self.platform_label.pack(side="right", padx=10)
    
    def _bind_events(self):
        """绑定事件处理函数"""
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 其他事件绑定可以在这里添加
    
    def _load_module_tabs(self):
        """加载模块UI到对应的选项卡"""
        # 系统控制模块
        self._create_system_control_tab()
        
        # 加载其他模块
        modules = self.app_manager.get_all_modules()
        for module_name, module in modules.items():
            if module_name == "todo":
                self._load_module_to_tab(module, self.todo_tab)
            elif module_name == "pomodoro":
                self._load_module_to_tab(module, self.pomodoro_tab)
            elif module_name == "launcher":
                self._load_module_to_tab(module, self.launcher_tab)
            elif module_name == "games":
                self._load_module_to_tab(module, self.games_tab)
    
    def _load_module_to_tab(self, module, tab):
        """加载模块UI到指定选项卡
        
        Args:
            module: 模块实例
            tab: 目标选项卡
        """
        try:
            module_widget = module.create_widget(tab, self.config_manager)
            if module_widget:
                module_widget.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            self.logger.error(f"加载模块UI失败: {str(e)}")
            error_label = ctk.CTkLabel(
                tab,
                text=f"加载模块失败: {str(e)}",
                text_color="red"
            )
            error_label.pack(padx=20, pady=20)
    
    def _create_system_control_tab(self):
        """创建系统控制选项卡的UI"""
        # 创建框架容器
        frame = ctk.CTkFrame(self.system_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 电源管理部分
        power_frame = ctk.CTkFrame(frame)
        power_frame.pack(fill="x", padx=10, pady=10)
        
        power_label = ctk.CTkLabel(
            power_frame,
            text="电源管理",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        power_label.pack(anchor="w", padx=10, pady=5)
        
        # 电源按钮区域
        power_buttons_frame = ctk.CTkFrame(power_frame)
        power_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        shutdown_button = ctk.CTkButton(
            power_buttons_frame,
            text="关机",
            width=100,
            command=lambda: self._show_power_dialog("shutdown")
        )
        shutdown_button.pack(side="left", padx=10, pady=10)
        
        restart_button = ctk.CTkButton(
            power_buttons_frame,
            text="重启",
            width=100,
            command=lambda: self._show_power_dialog("restart")
        )
        restart_button.pack(side="left", padx=10, pady=10)
        
        # 定时任务部分
        scheduled_frame = ctk.CTkFrame(power_frame)
        scheduled_frame.pack(fill="x", padx=10, pady=5)
        
        scheduled_label = ctk.CTkLabel(
            scheduled_frame,
            text="定时任务",
            font=ctk.CTkFont(size=14)
        )
        scheduled_label.pack(anchor="w", padx=10, pady=5)
        
        self.time_entry = ctk.CTkEntry(
            scheduled_frame,
            placeholder_text="输入时间 (如 30m, 2h)"
        )
        self.time_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        schedule_button = ctk.CTkButton(
            scheduled_frame,
            text="设置定时",
            width=100,
            command=self._schedule_power_task
        )
        schedule_button.pack(side="right", padx=10, pady=10)
        
        # 音频控制部分
        audio_frame = ctk.CTkFrame(frame)
        audio_frame.pack(fill="x", padx=10, pady=10)
        
        audio_label = ctk.CTkLabel(
            audio_frame,
            text="音频控制",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        audio_label.pack(anchor="w", padx=10, pady=5)
        
        # 音量控制区域
        volume_frame = ctk.CTkFrame(audio_frame)
        volume_frame.pack(fill="x", padx=10, pady=5)
        
        mute_button = ctk.CTkButton(
            volume_frame,
            text="静音切换",
            width=100,
            command=self._toggle_mute
        )
        mute_button.pack(side="left", padx=10, pady=10)
        
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_volume_change
        )
        self.volume_slider.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.volume_label = ctk.CTkLabel(
            volume_frame,
            text="50%",
            width=50
        )
        self.volume_label.pack(side="right", padx=10, pady=10)
        
        # 系统信息部分
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="系统信息",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_label.pack(anchor="w", padx=10, pady=5)
        
        system_info = self._get_system_info()
        for key, value in system_info.items():
            info_item = ctk.CTkFrame(info_frame)
            info_item.pack(fill="x", padx=10, pady=2)
            
            key_label = ctk.CTkLabel(
                info_item,
                text=key,
                width=100,
                anchor="w"
            )
            key_label.pack(side="left", padx=10, pady=2)
            
            value_label = ctk.CTkLabel(
                info_item,
                text=value,
                anchor="w"
            )
            value_label.pack(side="left", padx=10, pady=2, fill="x", expand=True)
    
    def _get_system_info(self):
        """获取系统信息
        
        Returns:
            dict: 系统信息字典
        """
        info = {}
        try:
            import psutil
            import platform
            
            info["操作系统"] = platform.platform()
            info["处理器"] = platform.processor()
            info["Python版本"] = platform.python_version()
            
            # 内存信息
            memory = psutil.virtual_memory()
            info["内存总量"] = f"{memory.total / (1024**3):.2f} GB"
            info["内存使用率"] = f"{memory.percent}%"
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            info["磁盘总量"] = f"{disk.total / (1024**3):.2f} GB"
            info["磁盘使用率"] = f"{disk.percent}%"
            
        except ImportError:
            info["错误"] = "缺少psutil库，无法获取详细系统信息"
        
        return info
    
    def _toggle_theme(self):
        """切换应用主题"""
        current_theme = self.config_manager.get("theme", "light")
        if current_theme == "light":
            new_theme = "dark"
            ctk.set_appearance_mode("dark")
        else:
            new_theme = "light"
            ctk.set_appearance_mode("light")
        
        self.config_manager.set("theme", new_theme)
        self.config_manager.save()
        self.logger.info(f"主题已切换为: {new_theme}")
    
    def _on_volume_change(self, value):
        """音量滑块变化事件处理
        
        Args:
            value: 新的音量值
        """
        volume = int(value)
        self.volume_label.configure(text=f"{volume}%")
        self.app_manager.handle_system_command("set_volume", {"level": volume})
    
    def _toggle_mute(self):
        """切换静音状态"""
        self.app_manager.handle_system_command("toggle_mute")
    
    def _show_power_dialog(self, action):
        """显示电源操作确认对话框
        
        Args:
            action: 电源操作类型，"shutdown"或"restart"
        """
        action_name = "关机" if action == "shutdown" else "重启"
        
        dialog = ctk.CTkInputDialog(
            text=f"确定要{action_name}吗？\n输入延迟时间（秒），取消请留空:",
            title=f"确认{action_name}"
        )
        
        # 使对话框居中于主窗口
        self._center_dialog(dialog, 400, 200)
        
        result = dialog.get_input()
        
        if result:
            try:
                delay = int(result)
                self.app_manager.handle_system_command(action, {"delay": delay})
                self.status_label.configure(text=f"{delay}秒后{action_name}")
            except ValueError:
                self.status_label.configure(text=f"无效的延迟时间")
    
    def _schedule_power_task(self):
        """设置定时电源任务"""
        time_text = self.time_entry.get()
        if not time_text:
            return
        
        # 简单的时间解析，支持如"30m"、"2h"的格式
        try:
            value = int(time_text[:-1])
            unit = time_text[-1].lower()
            
            if unit == 'm':
                seconds = value * 60
            elif unit == 'h':
                seconds = value * 3600
            else:
                seconds = value
            
            # 显示确认对话框
            dialog = ctk.CTkDialog(
                text=f"选择定时操作:\n\n时间: {time_text}",
                title="定时任务设置"
            )
            
            # 使对话框居中于主窗口
            self._center_dialog(dialog, 300, 200)
            
            # 添加选项按钮
            shutdown_btn = ctk.CTkButton(
                dialog,
                text="定时关机",
                command=lambda: self._confirm_scheduled_task("shutdown", seconds, dialog)
            )
            shutdown_btn.pack(padx=20, pady=10, fill="x")
            
            restart_btn = ctk.CTkButton(
                dialog,
                text="定时重启",
                command=lambda: self._confirm_scheduled_task("restart", seconds, dialog)
            )
            restart_btn.pack(padx=20, pady=10, fill="x")
            
            cancel_btn = ctk.CTkButton(
                dialog,
                text="取消",
                command=dialog.destroy
            )
            cancel_btn.pack(padx=20, pady=10, fill="x")
            
        except (ValueError, IndexError):
            self.status_label.configure(text="无效的时间格式，请使用如：30m, 2h")
    
    def _confirm_scheduled_task(self, action, seconds, dialog):
        """确认定时任务
        
        Args:
            action: 操作类型
            seconds: 延迟秒数
            dialog: 对话框实例
        """
        action_name = "关机" if action == "shutdown" else "重启"
        dialog.destroy()
        
        self.app_manager.handle_system_command(action, {"delay": seconds})
        self.status_label.configure(text=f"已设置{seconds}秒后{action_name}")
    
    def _center_dialog(self, dialog, width, height):
        """使对话框居中于主窗口
        
        Args:
            dialog: 对话框
            width: 对话框宽度
            height: 对话框高度
        """
        # 等待主窗口完全加载
        self.root.update_idletasks()
        
        # 获取主窗口位置和大小
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        # 计算对话框应该出现的位置（相对于主窗口居中）
        x = main_x + (main_width - width) // 2
        y = main_y + (main_height - height) // 2
        
        # 设置对话框位置
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _on_close(self):
        """窗口关闭事件处理"""
        # 关闭应用前进行清理
        self.app_manager.shutdown()
        self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
