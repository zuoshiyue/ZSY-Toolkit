#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
Todo模块实现
"""

import json
import sqlite3
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

class Priority(Enum):
    """任务优先级枚举"""
    LOW = 0      # 不重要不紧急
    MEDIUM = 1   # 重要不紧急
    HIGH = 2     # 不重要紧急
    CRITICAL = 3 # 重要紧急

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    ARCHIVED = 3

class Task:
    """任务类"""
    def __init__(
        self, 
        title: str, 
        priority: Priority = Priority.MEDIUM,
        tags: List[str] = None,
        due_date: Optional[datetime] = None,
        description: str = "",
        status: TaskStatus = TaskStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        task_id: Optional[int] = None
    ):
        self.task_id = task_id
        self.title = title
        self.priority = priority
        self.tags = tags or []
        self.due_date = due_date
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """将任务转换为字典"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "priority": self.priority.value,
            "tags": ",".join(self.tags),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建任务"""
        return cls(
            task_id=data.get("task_id"),
            title=data["title"],
            priority=Priority(data["priority"]),
            tags=data["tags"].split(",") if data.get("tags") else [],
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            description=data.get("description", ""),
            status=TaskStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

class TodoModule:
    """Todo模块主类"""
    def __init__(self, data_dir: Path):
        self.logger = logging.getLogger("左拾月.TodoModule")
        self.data_dir = data_dir
        self.db_path = data_dir / "todo.db"
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        # 创建任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority INTEGER NOT NULL,
            tags TEXT,
            due_date TEXT,
            description TEXT,
            status INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # 创建标签表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT "#2A9D8F"
        )
        ''')
        
        self.conn.commit()
        self.logger.info("Todo数据库初始化完成")
    
    def add_task(self, task: Task) -> int:
        """添加任务"""
        task_dict = task.to_dict()
        cursor = self.conn.cursor()
        
        # 过滤掉task_id，因为这是自动生成的
        if "task_id" in task_dict:
            del task_dict["task_id"]
            
        columns = ", ".join(task_dict.keys())
        placeholders = ", ".join(["?"] * len(task_dict))
        values = list(task_dict.values())
        
        cursor.execute(
            f"INSERT INTO tasks ({columns}) VALUES ({placeholders})",
            values
        )
        self.conn.commit()
        
        # 更新任务ID
        task.task_id = cursor.lastrowid
        self.logger.info(f"添加任务成功: {task.title}")
        
        # 确保所有标签都存在
        for tag in task.tags:
            self._ensure_tag_exists(tag)
            
        return task.task_id
    
    def update_task(self, task: Task) -> bool:
        """更新任务"""
        if not task.task_id:
            self.logger.error("无法更新没有ID的任务")
            return False
            
        task.updated_at = datetime.now()
        task_dict = task.to_dict()
        
        # 移除task_id，不需要更新它
        task_id = task_dict.pop("task_id")
        
        # 构建UPDATE语句
        set_clause = ", ".join([f"{key} = ?" for key in task_dict.keys()])
        values = list(task_dict.values())
        values.append(task_id)  # WHERE子句的值
        
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE tasks SET {set_clause} WHERE task_id = ?",
            values
        )
        self.conn.commit()
        
        # 确保所有标签都存在
        for tag in task.tags:
            self._ensure_tag_exists(tag)
            
        self.logger.info(f"更新任务成功: {task.title}")
        return True
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        self.conn.commit()
        
        deleted = cursor.rowcount > 0
        if deleted:
            self.logger.info(f"删除任务成功: ID={task_id}")
        else:
            self.logger.warning(f"尝试删除不存在的任务: ID={task_id}")
            
        return deleted
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """获取单个任务"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            return Task.from_dict(dict(row))
        return None
    
    def get_tasks_by_quadrant(self, quadrant: int) -> List[Task]:
        """按四象限获取任务
        
        象限定义:
        0 - 不重要不紧急
        1 - 重要不紧急
        2 - 不重要紧急
        3 - 重要紧急
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE priority = ? AND status != ?", 
                      (quadrant, TaskStatus.ARCHIVED.value))
        rows = cursor.fetchall()
        return [Task.from_dict(dict(row)) for row in rows]
    
    def get_all_tasks(self, include_archived: bool = False) -> List[Task]:
        """获取所有任务"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM tasks"
        if not include_archived:
            query += f" WHERE status != {TaskStatus.ARCHIVED.value}"
        query += " ORDER BY priority DESC, updated_at DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        return [Task.from_dict(dict(row)) for row in rows]
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """按标签获取任务"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE tags LIKE ? AND status != ?", 
                      (f"%{tag}%", TaskStatus.ARCHIVED.value))
        rows = cursor.fetchall()
        return [Task.from_dict(dict(row)) for row in rows]
    
    def _ensure_tag_exists(self, tag_name: str) -> None:
        """确保标签存在"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        self.conn.commit()
    
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """获取所有标签"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT tag_id, name, color FROM tags ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_tag(self, tag_id: int, new_name: str, new_color: str) -> bool:
        """更新标签"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE tags SET name = ?, color = ? WHERE tag_id = ?",
            (new_name, new_color, tag_id)
        )
        self.conn.commit()
        
        # 如果标签名称发生变化，需要更新所有任务中的标签引用
        # 这里采用简单方法，可能需要更复杂的实现来处理精确匹配
        if cursor.rowcount > 0:
            self.logger.info(f"标签更新成功: {new_name}")
            return True
        return False
    
    def export_tasks_markdown(self) -> str:
        """导出任务为Markdown格式"""
        tasks = self.get_all_tasks(include_archived=True)
        quadrants = {
            Priority.LOW: "不重要不紧急",
            Priority.MEDIUM: "重要不紧急", 
            Priority.HIGH: "不重要紧急",
            Priority.CRITICAL: "重要紧急"
        }
        
        md_content = "# 左拾月任务列表\n\n"
        md_content += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 按象限分组
        for priority in Priority:
            quadrant_tasks = [t for t in tasks if t.priority == priority]
            if not quadrant_tasks:
                continue
                
            md_content += f"## {quadrants[priority]} (共{len(quadrant_tasks)}项)\n\n"
            
            for task in quadrant_tasks:
                status_mark = "✓" if task.status == TaskStatus.COMPLETED else "□"
                md_content += f"- [{status_mark}] {task.title}\n"
                
                if task.description:
                    md_content += f"  - 描述: {task.description}\n"
                    
                if task.tags:
                    md_content += f"  - 标签: {', '.join(task.tags)}\n"
                    
                if task.due_date:
                    md_content += f"  - 截止: {task.due_date.strftime('%Y-%m-%d')}\n"
                    
                md_content += "\n"
            
        return md_content
    
    def import_tasks_from_markdown(self, md_content: str) -> Tuple[int, int]:
        """从Markdown导入任务
        
        返回: (成功导入数, 失败数)
        """
        # 此方法需要更复杂的解析逻辑，这里仅提供基本框架
        # 实际实现可能需要更强大的Markdown解析库
        
        added = 0
        failed = 0
        
        # 简单示例实现
        lines = md_content.split("\n")
        current_quadrant = Priority.MEDIUM  # 默认优先级
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 解析象限
            if line.startswith("## "):
                quadrant_name = line[3:].lower()
                if "重要" in quadrant_name and "紧急" in quadrant_name:
                    current_quadrant = Priority.CRITICAL
                elif "重要" in quadrant_name:
                    current_quadrant = Priority.MEDIUM
                elif "紧急" in quadrant_name:
                    current_quadrant = Priority.HIGH
                else:
                    current_quadrant = Priority.LOW
                continue
                
            # 解析任务
            if line.startswith("- [") and "]" in line:
                status_mark = line[3]
                status = TaskStatus.COMPLETED if status_mark in ("✓", "x", "X") else TaskStatus.PENDING
                
                title_start = line.find("]") + 2
                title = line[title_start:].strip()
                
                if not title:
                    failed += 1
                    continue
                    
                task = Task(
                    title=title,
                    priority=current_quadrant,
                    status=status
                )
                
                try:
                    self.add_task(task)
                    added += 1
                except Exception as e:
                    self.logger.error(f"导入任务失败: {str(e)}")
                    failed += 1
        
        return added, failed
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.logger.info("Todo数据库连接已关闭") 