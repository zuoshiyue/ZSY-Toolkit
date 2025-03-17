#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
Todo模块UI实现
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from src.modules.todo.todo_module import TodoModule, Task, Priority, TaskStatus

class QuadrantView(ctk.CTkFrame):
    """四象限任务视图"""
    def __init__(self, master, title: str, priority: Priority, todo_module: TodoModule, 
                 add_callback: Callable, edit_callback: Callable, **kwargs):
        super().__init__(master, **kwargs)
        
        self.todo_module = todo_module
        self.priority = priority
        self.add_callback = add_callback
        self.edit_callback = edit_callback
        
        # 标题和操作区
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=title,
            font=("Helvetica", 14, "bold")
        )
        self.title_label.pack(side="left", padx=5)
        
        # 添加按钮
        self.add_button = ctk.CTkButton(
            self.header_frame,
            text="+",
            width=30,
            command=lambda: self.add_callback(self.priority)
        )
        self.add_button.pack(side="right", padx=5)
        
        # 任务列表区域
        self.task_frame = ctk.CTkScrollableFrame(self)
        self.task_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 设置最小高度，确保滚动区域有足够的空间
        self.configure(height=300)  # 设置象限视图的最小高度
        self.task_frame.configure(height=250)  # 设置滚动区域的最小高度
        
        # 刷新任务列表
        self.refresh_tasks()
    
    def refresh_tasks(self):
        """刷新任务列表"""
        # 清空现有任务
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        
        # 获取此象限的任务
        tasks = self.todo_module.get_tasks_by_quadrant(self.priority.value)
        
        if not tasks:
            empty_label = ctk.CTkLabel(
                self.task_frame,
                text="暂无任务",
                text_color="gray"
            )
            empty_label.pack(pady=20)
            return
        
        # 添加任务到视图
        for task in tasks:
            self._add_task_item(task)
    
    def _add_task_item(self, task: Task):
        """添加任务项到视图"""
        # 任务容器
        task_frame = ctk.CTkFrame(self.task_frame)
        task_frame.pack(fill="x", padx=2, pady=2, ipady=2)
        
        # 复选框
        is_completed = task.status == TaskStatus.COMPLETED
        checkbox_var = ctk.BooleanVar(value=is_completed)
        
        def on_status_change():
            task.status = TaskStatus.COMPLETED if checkbox_var.get() else TaskStatus.PENDING
            self.todo_module.update_task(task)
            # 更新视觉效果
            title_color = "gray" if checkbox_var.get() else "white"
            title_label.configure(text_color=title_color)
        
        checkbox = ctk.CTkCheckBox(
            task_frame, 
            text="",
            variable=checkbox_var,
            command=on_status_change,
            width=20
        )
        checkbox.pack(side="left", padx=5)
        
        # 任务标题
        title_color = "gray" if is_completed else "white"
        title_label = ctk.CTkLabel(
            task_frame,
            text=task.title,
            text_color=title_color,
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # 编辑按钮
        edit_button = ctk.CTkButton(
            task_frame,
            text="编辑",
            width=40,
            height=24,
            command=lambda: self.edit_callback(task)
        )
        edit_button.pack(side="right", padx=5)
        
        # 如果有截止日期，显示
        if task.due_date:
            days_left = (task.due_date.date() - datetime.now().date()).days
            due_text = f"{days_left}天" if days_left >= 0 else "已逾期"
            due_color = "#2A9D8F" if days_left >= 0 else "#E76F51"
            
            due_label = ctk.CTkLabel(
                task_frame,
                text=due_text,
                text_color=due_color,
                font=("Helvetica", 12)
            )
            due_label.pack(side="right", padx=5)
        
        # 如果有标签，显示第一个
        if task.tags:
            tag_frame = ctk.CTkFrame(
                task_frame, 
                fg_color="#2A9D8F", 
                corner_radius=4,
                height=20
            )
            tag_frame.pack(side="right", padx=5)
            
            tag_label = ctk.CTkLabel(
                tag_frame,
                text=task.tags[0],
                font=("Helvetica", 10),
                text_color="white",
                padx=4,
                pady=0
            )
            tag_label.pack()

class TaskDialog(ctk.CTkToplevel):
    """任务编辑对话框"""
    def __init__(self, parent, todo_module: TodoModule, task: Optional[Task] = None, 
                 initial_priority: Optional[Priority] = None, callback: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.todo_module = todo_module
        self.task = task  # 如果是None，表示新建任务
        self.callback = callback
        
        # 设置对话框属性
        self.title("编辑任务" if task else "新建任务")
        self.geometry("500x450")  # 增加高度
        self.resizable(True, True)  # 允许调整大小
        self.lift()  # 置于顶层
        self.grab_set()  # 模态对话框
        
        # 设置最小尺寸
        self.minsize(500, 450)
        
        # 基本信息区域
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # 标题
        ctk.CTkLabel(info_frame, text="标题:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ctk.CTkEntry(info_frame, width=350)
        self.title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        if task:
            self.title_entry.insert(0, task.title)
        
        # 描述
        ctk.CTkLabel(info_frame, text="描述:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.desc_text = ctk.CTkTextbox(info_frame, width=350, height=100)
        self.desc_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        if task and task.description:
            self.desc_text.insert("1.0", task.description)
        
        # 截止日期
        ctk.CTkLabel(info_frame, text="截止日期:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        date_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        date_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # 添加是否设置截止日期的复选框
        self.has_due_date = ctk.BooleanVar(value=task.due_date is not None if task else False)
        
        def toggle_due_date():
            # 启用或禁用日期选择器
            state = "normal" if self.has_due_date.get() else "disabled"
            year_dropdown.configure(state=state)
            month_dropdown.configure(state=state)
            day_dropdown.configure(state=state)
        
        due_date_checkbox = ctk.CTkCheckBox(
            date_frame,
            text="设置截止日期",
            variable=self.has_due_date,
            command=toggle_due_date,
            onvalue=True,
            offvalue=False
        )
        due_date_checkbox.pack(side="top", anchor="w", pady=(0, 5))
        
        # 简化版日期选择器 (实际应用中可能需要更复杂的日期选择控件)
        current_date = datetime.now().date()
        if task and task.due_date:
            current_date = task.due_date.date()
            
        self.year_var = ctk.StringVar(value=str(current_date.year))
        self.month_var = ctk.StringVar(value=str(current_date.month))
        self.day_var = ctk.StringVar(value=str(current_date.day))
        
        year_options = [str(year) for year in range(current_date.year, current_date.year + 5)]
        month_options = [str(month) for month in range(1, 13)]
        day_options = [str(day) for day in range(1, 32)]
        
        date_selector_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        date_selector_frame.pack(side="top", fill="x")
        
        year_dropdown = ctk.CTkOptionMenu(date_selector_frame, values=year_options, variable=self.year_var, width=70)
        month_dropdown = ctk.CTkOptionMenu(date_selector_frame, values=month_options, variable=self.month_var, width=60)
        day_dropdown = ctk.CTkOptionMenu(date_selector_frame, values=day_options, variable=self.day_var, width=60)
        
        year_dropdown.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(date_selector_frame, text="年").pack(side="left", padx=(0, 5))
        month_dropdown.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(date_selector_frame, text="月").pack(side="left", padx=(0, 5))
        day_dropdown.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(date_selector_frame, text="日").pack(side="left")
        
        # 初始化日期选择器状态
        toggle_due_date()
        
        # 优先级
        ctk.CTkLabel(info_frame, text="优先级:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        priority_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        priority_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        self.priority_var = ctk.IntVar(
            value=task.priority.value if task else 
            (initial_priority.value if initial_priority else Priority.MEDIUM.value)
        )
        
        priorities = [
            ("重要且紧急", Priority.CRITICAL.value),
            ("重要不紧急", Priority.MEDIUM.value),
            ("紧急不重要", Priority.HIGH.value),
            ("不重要不紧急", Priority.LOW.value)
        ]
        
        for text, value in priorities:
            radio = ctk.CTkRadioButton(
                priority_frame,
                text=text,
                variable=self.priority_var,
                value=value
            )
            radio.pack(anchor="w", padx=5, pady=2)
        
        # 标签
        ctk.CTkLabel(info_frame, text="标签:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.tags_entry = ctk.CTkEntry(info_frame, width=350, placeholder_text="多个标签用逗号分隔")
        self.tags_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        
        if task and task.tags:
            self.tags_entry.insert(0, ", ".join(task.tags))
        
        # 状态
        ctk.CTkLabel(info_frame, text="状态:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        
        status_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        status_frame.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        self.status_var = ctk.IntVar(
            value=task.status.value if task else TaskStatus.PENDING.value
        )
        
        statuses = [
            ("待处理", TaskStatus.PENDING.value),
            ("进行中", TaskStatus.IN_PROGRESS.value),
            ("已完成", TaskStatus.COMPLETED.value),
            ("已归档", TaskStatus.ARCHIVED.value)
        ]
        
        for i, (text, value) in enumerate(statuses):
            radio = ctk.CTkRadioButton(
                status_frame,
                text=text,
                variable=self.status_var,
                value=value
            )
            radio.grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=15)
        
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self.destroy,
            fg_color="#E76F51"
        )
        self.cancel_button.pack(side="left", padx=5)
        
        self.save_button = ctk.CTkButton(
            button_frame,
            text="保存",
            command=self._save_task,
            fg_color="#2A9D8F"
        )
        self.save_button.pack(side="right", padx=5)
        
        # 如果是编辑模式，显示删除按钮
        if task:
            self.delete_button = ctk.CTkButton(
                button_frame,
                text="删除",
                command=self._delete_task,
                fg_color="#E9C46A",
                text_color="black"
            )
            self.delete_button.pack(side="right", padx=5)
    
    def _save_task(self):
        """保存任务"""
        title = self.title_entry.get().strip()
        if not title:
            # 显示错误提示
            self.title_entry.configure(border_color="red")
            return
        
        try:
            # 获取截止日期
            due_date = None
            if self.has_due_date.get():  # 只有当复选框被选中时才设置截止日期
                try:
                    year = int(self.year_var.get())
                    month = int(self.month_var.get())
                    day = int(self.day_var.get())
                    due_date = datetime(year, month, day)
                except (ValueError, AttributeError):
                    # 日期无效，忽略
                    pass
                
            # 获取标签
            tags_text = self.tags_entry.get().strip()
            tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
            
            # 获取描述
            description = self.desc_text.get("1.0", "end-1c").strip()
            
            # 创建或更新任务
            if self.task:  # 更新现有任务
                self.task.title = title
                self.task.description = description
                self.task.priority = Priority(self.priority_var.get())
                self.task.status = TaskStatus(self.status_var.get())
                self.task.due_date = due_date
                self.task.tags = tags
                self.task.updated_at = datetime.now()
                
                self.todo_module.update_task(self.task)
            else:  # 创建新任务
                new_task = Task(
                    title=title,
                    description=description,
                    priority=Priority(self.priority_var.get()),
                    status=TaskStatus(self.status_var.get()),
                    due_date=due_date,
                    tags=tags
                )
                
                self.todo_module.add_task(new_task)
            
            # 回调通知
            if self.callback:
                self.callback()
                
            # 关闭对话框
            self.destroy()
            
        except Exception as e:
            logging.getLogger("左拾月.TodoUI").error(f"保存任务失败: {str(e)}", exc_info=True)
            # 显示错误提示 (实际应用中可能需要更好的错误提示UI)
    
    def _delete_task(self):
        """删除任务"""
        if not self.task or not self.task.task_id:
            return
            
        # 简单确认对话框
        confirm = ctk.CTkInputDialog(
            text="输入'删除'确认删除此任务", 
            title="确认删除"
        )
        result = confirm.get_input()
        
        if result == "删除":
            self.todo_module.delete_task(self.task.task_id)
            
            # 回调通知
            if self.callback:
                self.callback()
                
            # 关闭对话框
            self.destroy()

class ImportDialog(ctk.CTkToplevel):
    """任务导入对话框"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 设置对话框属性
        self.title("从Markdown导入任务")
        self.geometry("600x500")  # 更大的对话框
        self.resizable(True, True)
        self.lift()  # 置于顶层
        self.grab_set()  # 模态对话框
        
        # 设置最小尺寸
        self.minsize(600, 500)
        
        # 结果变量
        self.result = None
        
        # 创建UI
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 说明标签
        header_label = ctk.CTkLabel(
            self,
            text="将Markdown格式的任务粘贴到下方框中:",
            font=("Helvetica", 14)
        )
        header_label.pack(padx=20, pady=(20, 5), anchor="w")
        
        # 示例按钮
        example_button = ctk.CTkButton(
            self,
            text="显示示例",
            command=self._show_example,
            width=100
        )
        example_button.pack(padx=20, pady=(0, 10), anchor="w")
        
        # 文本输入框
        self.text_input = ctk.CTkTextbox(
            self,
            width=560,
            height=350,
            font=("Helvetica", 12)
        )
        self.text_input.pack(padx=20, pady=10, fill="both", expand=True)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self.destroy,
            fg_color="#E76F51",
            width=100
        )
        cancel_button.pack(side="left", padx=5)
        
        import_button = ctk.CTkButton(
            button_frame,
            text="导入",
            command=self._on_import,
            fg_color="#2A9D8F",
            width=100
        )
        import_button.pack(side="right", padx=5)
    
    def _show_example(self):
        """显示示例内容"""
        example = """# 左拾月任务列表

## 重要且紧急
- [ ] 完成项目报告
  - 描述: 需要在周五前完成季度项目总结报告
  - 标签: 工作, 文档
  - 截止: 2025-03-20

## 重要不紧急
- [ ] 学习Python高级编程
  - 描述: 提升编程技能，学习装饰器和元类
  - 标签: 学习, 编程

## 不重要紧急
- [ ] 回复邮件
  - 截止: 2025-03-18

## 不重要不紧急
- [ ] 整理书架
- [ ] 看电影
"""
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", example)
    
    def _on_import(self):
        """导入按钮点击事件"""
        self.result = self.text_input.get("1.0", "end-1c")
        self.destroy()
    
    def get_input(self) -> Optional[str]:
        """获取输入内容"""
        self.wait_window()  # 等待窗口关闭
        return self.result

class TodoUI(ctk.CTkFrame):
    """Todo模块主UI类"""
    def __init__(self, master, config_manager, **kwargs):
        super().__init__(master, **kwargs)
        
        self.logger = logging.getLogger("左拾月.TodoUI")
        
        # 初始化数据模块
        data_dir = Path(config_manager.get_app_data_dir()) / "todo"
        self.todo_module = TodoModule(data_dir)
        
        # 创建UI布局
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI布局"""
        # 设置最小尺寸，确保窗口有足够的空间
        self.configure(width=800, height=600)
        
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self, height=40)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))
        
        # 标题
        title_label = ctk.CTkLabel(
            toolbar, 
            text="左拾月任务管理",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # 工具按钮
        refresh_button = ctk.CTkButton(
            toolbar,
            text="刷新",
            width=80,
            command=self._refresh_all
        )
        refresh_button.pack(side="right", padx=5)
        
        export_button = ctk.CTkButton(
            toolbar,
            text="导出",
            width=80,
            command=self._export_tasks
        )
        export_button.pack(side="right", padx=5)
        
        import_button = ctk.CTkButton(
            toolbar,
            text="导入",
            width=80,
            command=self._import_tasks
        )
        import_button.pack(side="right", padx=5)
        
        # 四象限视图
        quadrants_frame = ctk.CTkFrame(self)
        quadrants_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 设置网格布局
        quadrants_frame.grid_columnconfigure(0, weight=1)
        quadrants_frame.grid_columnconfigure(1, weight=1)
        quadrants_frame.grid_rowconfigure(0, weight=1)
        quadrants_frame.grid_rowconfigure(1, weight=1)
        
        # 确保四象限框架有足够的高度
        quadrants_frame.configure(height=500)
        
        # 象限1：重要且紧急
        self.quadrant1 = QuadrantView(
            quadrants_frame,
            title="重要且紧急",
            priority=Priority.CRITICAL,
            todo_module=self.todo_module,
            add_callback=self._add_task,
            edit_callback=self._edit_task,
            fg_color="#E76F51",  # 红色背景
        )
        self.quadrant1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 象限2：重要不紧急
        self.quadrant2 = QuadrantView(
            quadrants_frame,
            title="重要不紧急",
            priority=Priority.MEDIUM,
            todo_module=self.todo_module,
            add_callback=self._add_task,
            edit_callback=self._edit_task,
            fg_color="#2A9D8F",  # 绿色背景
        )
        self.quadrant2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # 象限3：紧急不重要
        self.quadrant3 = QuadrantView(
            quadrants_frame,
            title="紧急不重要",
            priority=Priority.HIGH,
            todo_module=self.todo_module,
            add_callback=self._add_task,
            edit_callback=self._edit_task,
            fg_color="#E9C46A",  # 黄色背景
        )
        self.quadrant3.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 象限4：不重要不紧急
        self.quadrant4 = QuadrantView(
            quadrants_frame,
            title="不重要不紧急",
            priority=Priority.LOW,
            todo_module=self.todo_module,
            add_callback=self._add_task,
            edit_callback=self._edit_task,
            fg_color="#264653",  # 蓝色背景
        )
        self.quadrant4.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
    
    def _add_task(self, priority: Priority):
        """添加任务"""
        TaskDialog(self, self.todo_module, initial_priority=priority, callback=self._refresh_all)
    
    def _edit_task(self, task: Task):
        """编辑任务"""
        TaskDialog(self, self.todo_module, task=task, callback=self._refresh_all)
    
    def _refresh_all(self):
        """刷新所有象限"""
        self.quadrant1.refresh_tasks()
        self.quadrant2.refresh_tasks()
        self.quadrant3.refresh_tasks()
        self.quadrant4.refresh_tasks()
    
    def _export_tasks(self):
        """导出任务"""
        # 将任务导出为Markdown文件
        md_content = self.todo_module.export_tasks_markdown()
        
        # 保存对话框 (简化版，实际应用可能需要使用系统的文件对话框)
        export_dir = Path.home() / "Downloads"
        export_dir.mkdir(exist_ok=True)
        
        file_path = export_dir / f"左拾月任务导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            # 成功提示
            success_dialog = ctk.CTkToplevel(self)
            success_dialog.title("导出成功")
            success_dialog.geometry("400x150")
            success_dialog.resizable(False, False)
            success_dialog.lift()
            success_dialog.grab_set()
            
            ctk.CTkLabel(
                success_dialog,
                text=f"任务已导出到:\n{file_path}",
                font=("Helvetica", 12)
            ).pack(padx=20, pady=20)
            
            ctk.CTkButton(
                success_dialog,
                text="确定",
                command=success_dialog.destroy,
                width=80
            ).pack(pady=10)
            
        except Exception as e:
            self.logger.error(f"导出任务失败: {str(e)}", exc_info=True)
            # 错误提示
            error_dialog = ctk.CTkToplevel(self)
            error_dialog.title("导出失败")
            error_dialog.geometry("400x200")
            error_dialog.resizable(False, False)
            error_dialog.lift()
            error_dialog.grab_set()
            
            ctk.CTkLabel(
                error_dialog,
                text=f"导出任务时发生错误:\n{str(e)}",
                font=("Helvetica", 12)
            ).pack(padx=20, pady=20)
            
            ctk.CTkButton(
                error_dialog,
                text="确定",
                command=error_dialog.destroy,
                width=80
            ).pack(pady=10)
    
    def _import_tasks(self):
        """导入任务"""
        # 使用自定义导入对话框
        import_dialog = ImportDialog(self)
        md_content = import_dialog.get_input()
        
        if md_content:
            try:
                added, failed = self.todo_module.import_tasks_from_markdown(md_content)
                
                # 刷新任务列表
                self._refresh_all()
                
                # 成功提示
                # 使用普通的消息框替代 CTkMessagebox
                success_dialog = ctk.CTkToplevel(self)
                success_dialog.title("导入结果")
                success_dialog.geometry("300x150")
                success_dialog.resizable(False, False)
                success_dialog.lift()
                success_dialog.grab_set()
                
                ctk.CTkLabel(
                    success_dialog,
                    text=f"成功导入 {added} 个任务\n导入失败 {failed} 个任务",
                    font=("Helvetica", 12)
                ).pack(padx=20, pady=20)
                
                ctk.CTkButton(
                    success_dialog,
                    text="确定",
                    command=success_dialog.destroy,
                    width=80
                ).pack(pady=10)
                
            except Exception as e:
                self.logger.error(f"导入任务失败: {str(e)}", exc_info=True)
                # 错误提示
                error_dialog = ctk.CTkToplevel(self)
                error_dialog.title("导入失败")
                error_dialog.geometry("400x200")
                error_dialog.resizable(False, False)
                error_dialog.lift()
                error_dialog.grab_set()
                
                ctk.CTkLabel(
                    error_dialog,
                    text=f"导入任务时发生错误:\n{str(e)}",
                    font=("Helvetica", 12)
                ).pack(padx=20, pady=20)
                
                ctk.CTkButton(
                    error_dialog,
                    text="确定",
                    command=error_dialog.destroy,
                    width=80
                ).pack(pady=10)
    
    def on_close(self):
        """关闭时调用"""
        if hasattr(self, 'todo_module'):
            self.todo_module.close() 