#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用管理器模块
负责协调各功能模块的运行和通信
"""

import os
import sys
import importlib
import logging
from pathlib import Path

class AppManager:
    """应用管理器，协调各功能模块的运行和通信"""
    
    def __init__(self, config_manager, platform_adapter):
        """初始化应用管理器
        
        Args:
            config_manager: 配置管理器实例
            platform_adapter: 平台适配器实例
        """
        self.logger = logging.getLogger("左拾月.应用管理器")
        self.config_manager = config_manager
        self.platform_adapter = platform_adapter
        self.modules = {}
        
        # 初始化模块
        self.initialize_modules()
        
        self.logger.info("应用管理器已初始化")
    
    def initialize_modules(self):
        """初始化所有启用的功能模块"""
        self.logger.info("开始初始化功能模块...")
        
        # 获取模块目录
        module_dir = Path(__file__).parent.parent / "modules"
        if not module_dir.exists():
            self.logger.error(f"模块目录不存在: {module_dir}")
            return False
        
        # 获取配置中启用的模块
        enabled_modules = []
        module_config = self.config_manager.get("modules", {})
        
        # 如果配置为空，默认启用所有模块
        if not module_config:
            # 扫描modules目录下的所有子目录
            for item in module_dir.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    module_name = item.name
                    # 检查是否有效模块(有__init__.py文件)
                    if (item / "__init__.py").exists():
                        enabled_modules.append(module_name)
                        # 添加到配置
                        if module_name not in module_config:
                            module_config[module_name] = {"enabled": True}
            
            # 更新配置
            self.config_manager.set("modules", module_config)
            self.config_manager.save()
        else:
            # 使用现有配置
            for module_name, module_info in module_config.items():
                if module_info.get("enabled", True):  # 默认启用
                    enabled_modules.append(module_name)
        
        # 初始化每个启用的模块
        for module_name in enabled_modules:
            try:
                # 构建模块路径
                module_path = f"src.modules.{module_name}"
                
                # 动态导入模块
                module = importlib.import_module(module_path)
                
                # 将模块实例添加到字典中
                self.modules[module_name] = module
                
                self.logger.info(f"已加载模块: {module_name}")
                
            except Exception as e:
                self.logger.error(f"加载模块 {module_name} 失败: {str(e)}")
        
        self.logger.info(f"共加载 {len(self.modules)} 个模块")
        return True
    
    def get_module(self, module_name):
        """获取指定名称的模块
        
        Args:
            module_name: 模块名称
            
        Returns:
            module: 模块实例，如果不存在则返回None
        """
        return self.modules.get(module_name)
    
    def get_all_modules(self):
        """获取所有已加载的模块
        
        Returns:
            dict: 模块名称到模块实例的映射
        """
        return self.modules.copy()
    
    def shutdown(self):
        """关闭应用管理器，清理资源"""
        self.logger.info("正在关闭应用管理器...")
        
        # 关闭所有模块
        for module_name, module in self.modules.items():
            try:
                # 如果模块有on_close方法，调用它
                if hasattr(module, 'on_close') and callable(module.on_close):
                    module.on_close()
                    self.logger.info(f"已关闭模块: {module_name}")
            except Exception as e:
                self.logger.error(f"关闭模块 {module_name} 时出错: {str(e)}")
        
        self.modules.clear()
        self.logger.info("应用管理器已关闭")
    
    def create_module_widget(self, parent, module_name):
        """创建指定模块的UI组件
        
        Args:
            parent: 父容器
            module_name: 模块名称
            
        Returns:
            widget: 模块UI组件，如果创建失败则返回None
        """
        module = self.get_module(module_name)
        if not module:
            self.logger.error(f"模块不存在: {module_name}")
            return None
        
        try:
            # 如果模块有create_widget函数，调用它
            if hasattr(module, 'create_widget') and callable(module.create_widget):
                return module.create_widget(parent, self.config_manager)
            else:
                self.logger.error(f"模块 {module_name} 没有create_widget函数")
                return None
        except Exception as e:
            self.logger.error(f"创建模块 {module_name} 的UI组件失败: {str(e)}")
            return None
    
    def handle_system_command(self, command, params=None):
        """处理系统命令
        
        Args:
            command: 命令名称
            params: 命令参数
            
        Returns:
            bool: 命令是否成功执行
        """
        try:
            # 委托给平台适配器处理
            return self.platform_adapter.handle_command(command, params)
        except Exception as e:
            self.logger.error(f"执行系统命令 {command} 失败: {str(e)}")
            return False 