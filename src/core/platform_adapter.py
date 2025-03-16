#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
平台适配器模块
负责处理不同操作系统平台的差异化实现
"""

import os
import sys
import platform
import subprocess
import logging

class PlatformAdapter:
    """跨平台适配器，处理不同操作系统的特定功能"""
    
    def __init__(self):
        self.logger = logging.getLogger("左拾月.平台适配器")
        self.platform = self._detect_platform()
        self.logger.info(f"平台适配器已初始化: {self.get_platform_name()}")
        
    def _detect_platform(self):
        """检测当前运行平台"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            return "linux"
        else:
            self.logger.warning(f"未识别的操作系统: {system}，将使用通用适配")
            return "generic"
    
    def get_platform_name(self):
        """获取平台名称"""
        return {
            "windows": "Windows",
            "macos": "macOS",
            "linux": "Linux",
            "generic": "通用平台"
        }.get(self.platform, "未知平台")
    
    # 电源管理相关方法
    def shutdown(self, delay=0):
        """关闭系统
        
        Args:
            delay: 延迟关机时间（秒）
        """
        try:
            if self.platform == "windows":
                cmd = f"shutdown /s /t {delay}"
                subprocess.run(cmd, shell=True)
            elif self.platform == "macos" or self.platform == "linux":
                cmd = f"shutdown -h +{delay//60}"
                subprocess.run(cmd, shell=True)
            else:
                self.logger.error("当前平台不支持关机操作")
                return False
            return True
        except Exception as e:
            self.logger.error(f"关机操作失败: {str(e)}")
            return False
    
    def restart(self, delay=0):
        """重启系统
        
        Args:
            delay: 延迟重启时间（秒）
        """
        try:
            if self.platform == "windows":
                cmd = f"shutdown /r /t {delay}"
                subprocess.run(cmd, shell=True)
            elif self.platform == "macos" or self.platform == "linux":
                cmd = f"shutdown -r +{delay//60}"
                subprocess.run(cmd, shell=True)
            else:
                self.logger.error("当前平台不支持重启操作")
                return False
            return True
        except Exception as e:
            self.logger.error(f"重启操作失败: {str(e)}")
            return False
    
    # 音频控制相关方法
    def set_volume(self, level):
        """设置系统音量
        
        Args:
            level: 音量级别(0-100)
        """
        try:
            level = max(0, min(100, level))  # 确保音量在0-100范围内
            
            if self.platform == "windows":
                # 使用pycaw处理Windows音量
                try:
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = interface.QueryInterface(IAudioEndpointVolume)
                    # 转换为-65.25到0的分贝值
                    volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                    return True
                except ImportError:
                    self.logger.error("缺少pycaw库，无法控制Windows音量")
                    return False
                
            elif self.platform == "macos":
                # 使用AppleScript控制macOS音量
                try:
                    import applescript
                    script = f'set volume output volume {level}'
                    applescript.AppleScript(script).run()
                    return True
                except ImportError:
                    self.logger.error("缺少applescript库，无法控制macOS音量")
                    return False
                
            elif self.platform == "linux":
                # 使用pulsectl控制Linux音量
                try:
                    import pulsectl
                    with pulsectl.Pulse('左拾月音量控制') as pulse:
                        sinks = pulse.sink_list()
                        if sinks:
                            sink = sinks[0]  # 使用默认音频输出
                            pulse.volume_set_all_chans(sink, level / 100.0)
                            return True
                        else:
                            self.logger.error("未找到音频输出设备")
                            return False
                except ImportError:
                    self.logger.error("缺少pulsectl库，无法控制Linux音量")
                    return False
            else:
                self.logger.error("当前平台不支持音量控制")
                return False
                
        except Exception as e:
            self.logger.error(f"设置音量失败: {str(e)}")
            return False
    
    def toggle_mute(self):
        """切换系统静音状态"""
        try:
            if self.platform == "windows":
                # 使用pycaw处理Windows静音
                try:
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = interface.QueryInterface(IAudioEndpointVolume)
                    current_mute = volume.GetMute()
                    volume.SetMute(not current_mute, None)
                    return True
                except ImportError:
                    self.logger.error("缺少pycaw库，无法控制Windows静音")
                    return False
                
            elif self.platform == "macos":
                # 使用AppleScript控制macOS静音
                try:
                    import applescript
                    script = 'set volume with output muted not (output muted of (get volume settings))'
                    applescript.AppleScript(script).run()
                    return True
                except ImportError:
                    self.logger.error("缺少applescript库，无法控制macOS静音")
                    return False
                
            elif self.platform == "linux":
                # 使用pulsectl控制Linux静音
                try:
                    import pulsectl
                    with pulsectl.Pulse('左拾月静音控制') as pulse:
                        sinks = pulse.sink_list()
                        if sinks:
                            sink = sinks[0]  # 使用默认音频输出
                            muted = sink.mute
                            pulse.mute(sink, not muted)
                            return True
                        else:
                            self.logger.error("未找到音频输出设备")
                            return False
                except ImportError:
                    self.logger.error("缺少pulsectl库，无法控制Linux静音")
                    return False
            else:
                self.logger.error("当前平台不支持静音控制")
                return False
                
        except Exception as e:
            self.logger.error(f"切换静音失败: {str(e)}")
            return False
    
    # 应用程序相关方法
    def discover_applications(self):
        """发现系统安装的应用程序
        
        Returns:
            list: 应用程序列表，每个元素包含应用名称和路径
        """
        apps = []
        try:
            if self.platform == "windows":
                # Windows应用发现逻辑
                import winreg
                
                # 检查开始菜单程序
                start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
                self._scan_directory_for_shortcuts(start_menu, apps)
                
                # 检查注册表中的已安装程序
                key_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
                ]
                
                for key_path in key_paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                        self._scan_registry_key(key, apps)
                    except Exception as e:
                        self.logger.warning(f"扫描注册表路径失败: {key_path}, 错误: {str(e)}")
                
            elif self.platform == "macos":
                # macOS应用发现逻辑
                applications_dir = "/Applications"
                for app in os.listdir(applications_dir):
                    if app.endswith(".app"):
                        app_path = os.path.join(applications_dir, app)
                        app_name = app.replace(".app", "")
                        apps.append({"name": app_name, "path": app_path})
                
            elif self.platform == "linux":
                # Linux应用发现逻辑
                application_dirs = [
                    "/usr/share/applications",
                    os.path.expanduser("~/.local/share/applications")
                ]
                
                for directory in application_dirs:
                    if os.path.exists(directory):
                        for file in os.listdir(directory):
                            if file.endswith(".desktop"):
                                desktop_file = os.path.join(directory, file)
                                app_info = self._parse_desktop_file(desktop_file)
                                if app_info:
                                    apps.append(app_info)
            
            return apps
        except Exception as e:
            self.logger.error(f"应用发现失败: {str(e)}")
            return []
    
    def _scan_directory_for_shortcuts(self, directory, apps):
        """扫描目录中的快捷方式(Windows专用)"""
        try:
            import pythoncom
            from win32com.shell import shell, shellcon
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".lnk"):
                        try:
                            shortcut_path = os.path.join(root, file)
                            shortcut = pythoncom.CoCreateInstance(
                                shell.CLSID_ShellLink,
                                None,
                                pythoncom.CLSCTX_INPROC_SERVER,
                                shell.IID_IShellLink
                            )
                            persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
                            persist_file.Load(shortcut_path)
                            target_path = shortcut.GetPath(shell.SLGP_SHORTPATH)[0]
                            
                            if target_path and os.path.exists(target_path):
                                app_name = os.path.splitext(file)[0]
                                apps.append({"name": app_name, "path": target_path})
                        except Exception as e:
                            self.logger.warning(f"处理快捷方式失败: {file}, 错误: {str(e)}")
        except ImportError:
            self.logger.error("缺少pywin32库，无法扫描Windows快捷方式")
    
    def _scan_registry_key(self, key, apps):
        """扫描注册表键中的应用程序(Windows专用)"""
        try:
            import winreg
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    try:
                        app_path, _ = winreg.QueryValueEx(subkey, "")
                        if app_path and os.path.exists(app_path):
                            apps.append({"name": subkey_name, "path": app_path})
                    except:
                        pass
                    
                    try:
                        app_path, _ = winreg.QueryValueEx(subkey, "Path")
                        if app_path and os.path.exists(app_path):
                            apps.append({"name": subkey_name, "path": app_path})
                    except:
                        pass
                    
                    i += 1
                except OSError:
                    break
        except ImportError:
            self.logger.error("缺少winreg库，无法扫描Windows注册表")
    
    def _parse_desktop_file(self, desktop_file):
        """解析Linux .desktop文件"""
        try:
            app_name = None
            app_exec = None
            app_icon = None
            
            with open(desktop_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.startswith("Name="):
                        app_name = line[5:].strip()
                    elif line.startswith("Exec="):
                        app_exec = line[5:].strip()
                        # 移除参数
                        if " %" in app_exec:
                            app_exec = app_exec[:app_exec.index(" %")]
                    elif line.startswith("Icon="):
                        app_icon = line[5:].strip()
                    
            if app_name and app_exec:
                return {
                    "name": app_name,
                    "path": app_exec,
                    "icon": app_icon
                }
            return None
        except Exception as e:
            self.logger.warning(f"解析Desktop文件失败: {desktop_file}, 错误: {str(e)}")
            return None
    
    def launch_application(self, app_path):
        """启动应用程序
        
        Args:
            app_path: 应用程序路径
        """
        try:
            if not os.path.exists(app_path):
                self.logger.error(f"应用程序路径不存在: {app_path}")
                return False
                
            if self.platform == "windows":
                os.startfile(app_path)
            elif self.platform == "macos":
                if app_path.endswith(".app"):
                    subprocess.Popen(["open", app_path])
                else:
                    subprocess.Popen(app_path, shell=True)
            elif self.platform == "linux":
                subprocess.Popen(app_path, shell=True)
            
            return True
        except Exception as e:
            self.logger.error(f"启动应用程序失败: {app_path}, 错误: {str(e)}")
            return False
            
    def handle_command(self, command, params=None):
        """处理系统命令
        
        Args:
            command: 命令名称
            params: 命令参数
            
        Returns:
            bool: 命令是否成功执行
        """
        self.logger.info(f"处理系统命令: {command}, 参数: {params}")
        
        if command == "shutdown":
            delay = params.get("delay", 0) if params else 0
            return self.shutdown(delay)
        
        elif command == "restart":
            delay = params.get("delay", 0) if params else 0
            return self.restart(delay)
        
        elif command == "set_volume":
            level = params.get("level", 50) if params else 50
            return self.set_volume(level)
        
        elif command == "toggle_mute":
            return self.toggle_mute()
        
        elif command == "launch_app":
            app_path = params.get("path") if params else None
            if not app_path:
                self.logger.error("缺少应用程序路径参数")
                return False
            return self.launch_application(app_path)
        
        else:
            self.logger.warning(f"未知系统命令: {command}")
            return False 