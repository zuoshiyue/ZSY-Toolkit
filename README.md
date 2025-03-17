# 左拾月 - 跨平台个人助手工具

一款具有品牌辨识度的模块化个人效率工具，实现系统管理、效率提升、娱乐休闲三位一体的跨平台解决方案，支持Windows/macOS/Linux系统。

## 功能特点

### 系统控制中枢
- **电源管理**：关机/重启、延迟执行、定时任务
- **音频控制**：全局静音切换、音量调节、多设备输出切换
- **显示器控制**：扩展/镜像模式切换、第二屏旋转（支持90度顺时针旋转）

### 效率工坊
- **Todo List**：四象限任务管理、任务标签系统、截止日期设置
- **番茄时钟**：可配置工作周期、智能休息建议、工作统计

### 应用速启中心
- **应用发现**：自动识别系统应用、支持手动配置
- **启动面板**：动态磁贴布局、最近使用应用置顶

### 左拾月游戏空间
- **数独挑战**：三级难度、实时错误检测、笔记功能
- **经典扫雷**：初级/中级/高级/自定义难度、智能窗口自适应
- **扩展接口**：支持第三方游戏模块加载

## 安装说明

### Windows
```bash
# 克隆项目
git clone https://github.com/yourusername/zsy-tools.git
cd zsy-tools

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python run.py
```

### macOS
```bash
# 克隆项目
git clone https://github.com/yourusername/zsy-tools.git
cd zsy-tools

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python run.py
```

### Linux
```bash
# 克隆项目
git clone https://github.com/yourusername/zsy-tools.git
cd zsy-tools

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python run.py
```

## 使用说明

详细使用说明请参考[用户手册](./docs/user_manual.md)。

## 开发者指南

开发者文档请参考[开发者指南](./docs/developer_guide.md)。

## 项目目录结构

```
zsy-tools/
├── src/                # 源代码目录
│   ├── core/           # 核心组件
│   │   ├── app_manager.py        # 应用管理器
│   │   ├── config_manager.py     # 配置管理器  
│   │   └── platform_adapter.py   # 平台适配器
│   ├── modules/        # 功能模块
│   │   ├── games/      # 游戏模块
│   │   │   ├── minesweeper/     # 扫雷游戏
│   │   │   └── sudoku/          # 数独游戏
│   │   ├── launcher/   # 应用启动器模块
│   │   ├── pomodoro/   # 番茄钟模块
│   │   └── todo/       # 待办事项模块
│   ├── ui/             # 用户界面
│   │   └── main_window.py        # 主窗口
│   └── main.py         # 主程序入口
├── requirements.txt    # 项目依赖
├── run.py              # 启动脚本
└── README.md           # 项目说明
```

## 完成状态

### 最近更新
- 🆕 2024-03-17：
  - 优化游戏窗口大小自适应功能，根据游戏难度自动调整
  - 改进扫雷游戏界面，支持更大尺寸的棋盘显示
  - 优化显示器控制功能，支持第二屏90度顺时针旋转
  - 完善系统控制模块的错误处理和日志记录
  - 改进UI布局，优化滚动条和窗口大小调整

### 已完成功能
- ✅ 核心框架搭建：
  - 应用管理器 (AppManager)
  - 配置管理器 (ConfigManager)
  - 平台适配器 (PlatformAdapter)
- ✅ 系统控制中枢：
  - 电源管理（关机/重启）
  - 延迟执行
  - 音频控制（静音切换、音量调节）
  - 显示器控制（模式切换、屏幕旋转）
- ✅ Todo模块：
  - 四象限任务管理（基于优先级和重要性）
  - 任务添加、编辑、删除功能
  - 任务标签系统
  - 任务状态跟踪
  - Markdown导入/导出功能
  - 可选的任务截止日期设置
  - 优化的导入/导出界面
  - 任务窗口高度自适应
- ✅ 番茄时钟模块：
  - 可配置的工作和休息时长
  - 工作/休息状态自动切换
  - 周期计数和长休息提醒
  - 优化的暂停/继续/重置功能，提高响应速度
  - 工作统计数据记录和查看
  - 自定义通知设置
  - 高精度计时器，确保计时准确性
- ✅ 游戏空间模块：
  - 游戏选择界面，支持多游戏切换
  - 数独游戏（三级难度、笔记功能、提示系统）
  - 扫雷游戏（初级/中级/高级/自定义难度）
  - 游戏统计和计时功能
  - 美观的游戏界面和交互效果
  - 智能窗口自适应，根据游戏类型和难度自动调整大小

### 待完成功能
- 🔄 应用速启中心：
  - 系统应用自动识别
  - 应用启动面板
  - 常用应用置顶
- 🔄 游戏空间：
  - 更多小游戏
  - 游戏成绩记录系统
  - 游戏模块扩展接口

### 待优化事项
- ⚠️ 平台适配：完善不同操作系统的特定功能支持
- ⚠️ UI/UX优化：提升用户界面美观度和交互体验
- ⚠️ 性能优化：提高应用启动速度和运行效率
- ⚠️ 本地化：支持多语言界面
- ⚠️ 自动更新：实现应用自动检查和安装更新

## 许可证

本项目基于MIT许可证开源。

## 自动构建和发布

本项目利用 GitHub Actions 自动构建和发布应用程序。当你推送代码到 `main` 或 `master` 分支，或者创建以 `v` 开头的标签（例如 `v1.0.0`）时，GitHub Actions 将自动触发构建流程。

### 构建流程

GitHub Actions 会在三个主要平台上构建应用程序：

1. **Windows**: 构建 `.exe` 可执行文件并打包为 `.zip` 文件
2. **macOS**: 构建 `.app` 应用程序并打包为 `.dmg` 文件
3. **Linux**: 构建可执行文件并打包为 `.tar.gz` 文件

### 如何发布新版本

1. 更新代码并确保一切正常工作
2. 更新版本号（如果适用）
3. 推送更改到 GitHub
4. 创建一个新的发布标签，例如：
   ```
   git tag -a v1.0.0 -m "发布版本 1.0.0"
   git push origin v1.0.0
   ```
5. GitHub Actions 将自动构建应用程序并创建发布

### 下载构建结果

构建完成后，你可以在以下位置找到构建结果：

1. GitHub Actions 的 "Artifacts" 部分（每次构建可用）
2. GitHub Releases 页面（仅当创建了发布标签时可用）

### 本地构建

如果你想在本地构建应用程序，可以使用以下命令：

```bash
# 安装必要的依赖
pip install pyinstaller
pip install -r requirements.txt

# 使用配置文件构建
pyinstaller zsy.spec
```

构建结果将在 `dist` 目录中生成。
