#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
左拾月 - 跨平台个人助手工具
启动脚本
"""

import os
import sys
from pathlib import Path
from src.main import main

if __name__ == "__main__":
    # 确保当前目录是项目根目录
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    
    # 启动应用程序
    sys.exit(main()) 