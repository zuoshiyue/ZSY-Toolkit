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
            
    def get_system_info(self):
        """获取系统信息
        
        Returns:
            dict: 包含系统信息的字典
        """
        try:
            info = {
                "platform": self.get_platform_name(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "memory": self._get_memory_info(),
                "disk": self._get_disk_info(),
                "cpu": self._get_cpu_info(),
                "network": self._get_network_info()
            }
            return info
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {str(e)}")
            return None
    
    def _get_memory_info(self):
        """获取内存信息"""
        try:
            if self.platform == "windows":
                import psutil
                memory = psutil.virtual_memory()
                return {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                }
            elif self.platform == "macos":
                import psutil
                memory = psutil.virtual_memory()
                return {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                }
            elif self.platform == "linux":
                import psutil
                memory = psutil.virtual_memory()
                return {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                }
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取内存信息失败: {str(e)}")
            return None
    
    def _get_disk_info(self):
        """获取磁盘信息"""
        try:
            if self.platform == "windows":
                import psutil
                disks = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disks.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent
                        })
                    except Exception:
                        continue
                return disks
            elif self.platform == "macos":
                import psutil
                disks = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disks.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent
                        })
                    except Exception:
                        continue
                return disks
            elif self.platform == "linux":
                import psutil
                disks = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disks.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent
                        })
                    except Exception:
                        continue
                return disks
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取磁盘信息失败: {str(e)}")
            return None
    
    def _get_cpu_info(self):
        """获取CPU信息"""
        try:
            if self.platform == "windows":
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                return {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current,
                        "min": cpu_freq.min,
                        "max": cpu_freq.max
                    } if cpu_freq else None
                }
            elif self.platform == "macos":
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                return {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current,
                        "min": cpu_freq.min,
                        "max": cpu_freq.max
                    } if cpu_freq else None
                }
            elif self.platform == "linux":
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                return {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current,
                        "min": cpu_freq.min,
                        "max": cpu_freq.max
                    } if cpu_freq else None
                }
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取CPU信息失败: {str(e)}")
            return None
    
    def _get_network_info(self):
        """获取网络信息"""
        try:
            if self.platform == "windows":
                import psutil
                net_io = psutil.net_io_counters()
                net_if = psutil.net_if_stats()
                net_addrs = psutil.net_if_addrs()
                return {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "interfaces": {
                        iface: {
                            "stats": {
                                "isup": stats.isup,
                                "speed": stats.speed,
                                "mtu": stats.mtu
                            },
                            "addresses": [
                                {
                                    "family": addr.family,
                                    "address": addr.address,
                                    "netmask": addr.netmask,
                                    "broadcast": addr.broadcast
                                }
                                for addr in net_addrs.get(iface, [])
                            ]
                        }
                        for iface, stats in net_if.items()
                    }
                }
            elif self.platform == "macos":
                import psutil
                net_io = psutil.net_io_counters()
                net_if = psutil.net_if_stats()
                net_addrs = psutil.net_if_addrs()
                return {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "interfaces": {
                        iface: {
                            "stats": {
                                "isup": stats.isup,
                                "speed": stats.speed,
                                "mtu": stats.mtu
                            },
                            "addresses": [
                                {
                                    "family": addr.family,
                                    "address": addr.address,
                                    "netmask": addr.netmask,
                                    "broadcast": addr.broadcast
                                }
                                for addr in net_addrs.get(iface, [])
                            ]
                        }
                        for iface, stats in net_if.items()
                    }
                }
            elif self.platform == "linux":
                import psutil
                net_io = psutil.net_io_counters()
                net_if = psutil.net_if_stats()
                net_addrs = psutil.net_if_addrs()
                return {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "interfaces": {
                        iface: {
                            "stats": {
                                "isup": stats.isup,
                                "speed": stats.speed,
                                "mtu": stats.mtu
                            },
                            "addresses": [
                                {
                                    "family": addr.family,
                                    "address": addr.address,
                                    "netmask": addr.netmask,
                                    "broadcast": addr.broadcast
                                }
                                for addr in net_addrs.get(iface, [])
                            ]
                        }
                        for iface, stats in net_if.items()
                    }
                }
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取网络信息失败: {str(e)}")
            return None
    
    def get_display_info(self):
        """获取显示器信息
        
        Returns:
            list: 显示器信息列表，每个元素包含显示器名称、分辨率、位置等信息
        """
        try:
            if self.platform == "windows":
                import win32api
                import win32con
                
                monitors = []
                i = 0
                while True:
                    try:
                        # 获取显示设备信息
                        device = win32api.EnumDisplayDevices(None, i)
                        if device.StateFlags & win32con.DISPLAY_DEVICE_ACTIVE:
                            # 获取显示设置
                            settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                            monitors.append({
                                "name": device.DeviceName,
                                "primary": bool(device.StateFlags & win32con.DISPLAY_DEVICE_PRIMARY_DEVICE),
                                "resolution": f"{settings.PelsWidth}x{settings.PelsHeight}",
                                "position": (settings.Position_x, settings.Position_y),
                                "rotation": settings.DisplayOrientation
                            })
                        i += 1
                    except:
                        break
                
                if len(monitors) > 0:
                    return monitors
                return None
                
            elif self.platform == "macos":
                import subprocess
                try:
                    # 使用system_profiler获取显示器信息
                    cmd = ["system_profiler", "SPDisplaysDataType", "-xml"]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        import plistlib
                        import io
                        plist_data = plistlib.loads(result.stdout.encode())
                        displays = []
                        for display in plist_data[0]["_items"]:
                            displays.append({
                                "name": display.get("_name", "Unknown"),
                                "resolution": display.get("spdisplays_resolution", "Unknown"),
                                "primary": display.get("spdisplays_main", False)
                            })
                        return displays
                except Exception as e:
                    self.logger.error(f"获取macOS显示器信息失败: {str(e)}")
                return None
                
            elif self.platform == "linux":
                import subprocess
                try:
                    # 使用xrandr获取显示器信息
                    cmd = ["xrandr", "--query"]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        displays = []
                        current_display = None
                        for line in result.stdout.split("\n"):
                            if " connected" in line:
                                name = line.split()[0]
                                primary = "primary" in line
                                current_display = {
                                    "name": name,
                                    "primary": primary,
                                    "resolution": None,
                                    "position": None
                                }
                                displays.append(current_display)
                            elif current_display and "x" in line:
                                parts = line.strip().split()
                                if len(parts) >= 1:
                                    current_display["resolution"] = parts[0]
                                    if len(parts) >= 4:
                                        current_display["position"] = (parts[2], parts[3])
                        return displays
                except Exception as e:
                    self.logger.error(f"获取Linux显示器信息失败: {str(e)}")
                return None
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取显示器信息失败: {str(e)}")
            return None
    
    def toggle_display_mode(self):
        """切换显示器模式（扩展/镜像）
        
        Returns:
            bool: 是否成功切换
        """
        try:
            monitors = self.get_display_info()
            if not monitors or len(monitors) < 2:
                self.logger.error("未检测到多个显示器")
                return False
            
            if self.platform == "windows":
                import win32api
                import win32con
                
                # 获取主显示器和第二显示器
                primary = next((m for m in monitors if m["primary"]), None)
                secondary = next((m for m in monitors if not m["primary"]), None)
                
                if not primary or not secondary:
                    self.logger.error("无法识别主显示器和第二显示器")
                    return False
                    
                # 获取当前显示器设置
                settings = win32api.EnumDisplaySettings(secondary["name"], win32con.ENUM_CURRENT_SETTINGS)
                
                # 切换模式
                if settings.Position_x == 0 and settings.Position_y == 0:
                    # 当前是镜像模式，切换到扩展模式
                    settings.Position_x = int(primary["resolution"].split("x")[0])  # 主显示器宽度
                    settings.Position_y = 0
                else:
                    # 当前是扩展模式，切换到镜像模式
                    settings.Position_x = 0
                    settings.Position_y = 0
                
                # 应用设置
                result = win32api.ChangeDisplaySettingsEx(
                    secondary["name"],
                    settings,
                    win32con.CDS_UPDATEREGISTRY | win32con.CDS_GLOBAL
                )
                
                if result == win32con.DISP_CHANGE_SUCCESSFUL:
                    self.logger.info("显示器模式切换成功")
                    return True
                else:
                    self.logger.error(f"显示器模式切换失败，错误代码: {result}")
                    return False
            
            elif self.platform == "macos":
                import subprocess
                try:
                    # 使用displayplacer切换模式
                    cmd = ["displayplacer", "list"]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        # 解析当前配置
                        current_config = result.stdout
                        if "Mirror" in current_config:
                            # 当前是镜像模式，切换到扩展模式
                            cmd = ["displayplacer", "extend"]
                        else:
                            # 当前是扩展模式，切换到镜像模式
                            cmd = ["displayplacer", "mirror"]
                        
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            self.logger.info("显示器模式切换成功")
                            return True
                        else:
                            self.logger.error(f"显示器模式切换失败: {result.stderr}")
                            return False
                except Exception as e:
                    self.logger.error(f"切换macOS显示器模式失败: {str(e)}")
                    return False
            
            elif self.platform == "linux":
                import subprocess
                try:
                    # 获取主显示器和第二显示器
                    primary = next((d for d in monitors if d["primary"]), None)
                    secondary = next((d for d in monitors if not d["primary"]), None)
                    
                    if not primary or not secondary:
                        self.logger.error("无法识别主显示器和第二显示器")
                        return False
                    
                    # 检查当前模式
                    if secondary["position"][0] == "0":
                        # 当前是镜像模式，切换到扩展模式
                        cmd = [
                            "xrandr",
                            "--output", secondary["name"],
                            "--mode", secondary["resolution"],
                            "--pos", f"{primary['resolution'].split('x')[0]}x0"
                        ]
                    else:
                        # 当前是扩展模式，切换到镜像模式
                        cmd = [
                            "xrandr",
                            "--output", secondary["name"],
                            "--mode", secondary["resolution"],
                            "--pos", "0x0"
                        ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.logger.info("显示器模式切换成功")
                        return True
                    else:
                        self.logger.error(f"显示器模式切换失败: {result.stderr}")
                        return False
                except Exception as e:
                    self.logger.error(f"切换Linux显示器模式失败: {str(e)}")
                    return False
            else:
                self.logger.error("当前平台不支持显示器模式切换")
                return False
            
        except Exception as e:
            self.logger.error(f"切换显示器模式失败: {str(e)}")
            return False
    
    def rotate_display(self):
        """旋转第二显示器（顺时针旋转90度）
        
        Returns:
            bool: 是否成功旋转
        """
        try:
            monitors = self.get_display_info()
            if not monitors or len(monitors) < 2:
                self.logger.error("未检测到多个显示器")
                return False
            
            if self.platform == "windows":
                import win32api
                import win32con
                
                # 获取第二显示器
                secondary = next((m for m in monitors if not m["primary"]), None)
                if not secondary:
                    self.logger.error("无法识别第二显示器")
                    return False
                    
                # 获取当前显示器设置
                settings = win32api.EnumDisplaySettings(secondary["name"], win32con.ENUM_CURRENT_SETTINGS)
                
                # 计算新的旋转角度（顺时针旋转90度）
                new_rotation = (secondary["rotation"] + 1) % 4
                
                # 设置新的旋转角度
                settings.DisplayOrientation = new_rotation
                
                # 应用设置
                result = win32api.ChangeDisplaySettingsEx(
                    secondary["name"],
                    settings,
                    win32con.CDS_UPDATEREGISTRY | win32con.CDS_GLOBAL
                )
                
                if result == win32con.DISP_CHANGE_SUCCESSFUL:
                    self.logger.info("显示器旋转成功")
                    return True
                else:
                    self.logger.error(f"显示器旋转失败，错误代码: {result}")
                    return False
            
            elif self.platform == "macos":
                import subprocess
                try:
                    # 获取第二显示器
                    secondary = next((d for d in monitors if not d["primary"]), None)
                    if not secondary:
                        self.logger.error("无法识别第二显示器")
                        return False
                    
                    # 使用displayplacer旋转显示器
                    cmd = ["displayplacer", f"rotate:{secondary['name']}:90"]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.logger.info("显示器旋转成功")
                        return True
                    else:
                        self.logger.error(f"显示器旋转失败: {result.stderr}")
                        return False
                except Exception as e:
                    self.logger.error(f"旋转macOS显示器失败: {str(e)}")
                    return False
            
            elif self.platform == "linux":
                import subprocess
                try:
                    # 获取第二显示器
                    secondary = next((d for d in monitors if not d["primary"]), None)
                    if not secondary:
                        self.logger.error("无法识别第二显示器")
                        return False
                    
                    # 使用xrandr旋转显示器
                    cmd = ["xrandr", "--output", secondary["name"], "--rotate", "right"]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.logger.info("显示器旋转成功")
                        return True
                    else:
                        self.logger.error(f"显示器旋转失败: {result.stderr}")
                        return False
                except Exception as e:
                    self.logger.error(f"旋转Linux显示器失败: {str(e)}")
                    return False
            else:
                self.logger.error("当前平台不支持显示器旋转")
                return False
            
        except Exception as e:
            self.logger.error(f"旋转显示器失败: {str(e)}")
            return False
    
    def get_volume(self):
        """获取当前系统音量
        
        Returns:
            int: 音量级别(0-100)，如果获取失败则返回None
        """
        try:
            if self.platform == "windows":
                try:
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = interface.QueryInterface(IAudioEndpointVolume)
                    # 从分贝值转换为百分比
                    return int(volume.GetMasterVolumeLevelScalar() * 100)
                except ImportError:
                    self.logger.error("缺少pycaw库，无法获取Windows音量")
                    return None
                
            elif self.platform == "macos":
                try:
                    import applescript
                    script = 'output volume of (get volume settings)'
                    result = applescript.AppleScript(script).run()
                    return int(result)
                except ImportError:
                    self.logger.error("缺少applescript库，无法获取macOS音量")
                    return None
                
            elif self.platform == "linux":
                try:
                    import pulsectl
                    with pulsectl.Pulse('左拾月音量控制') as pulse:
                        sinks = pulse.sink_list()
                        if sinks:
                            sink = sinks[0]  # 使用默认音频输出
                            volume = pulse.volume_get_all_chans(sink)
                            return int(volume * 100)
                        else:
                            self.logger.error("未找到音频输出设备")
                            return None
                except ImportError:
                    self.logger.error("缺少pulsectl库，无法获取Linux音量")
                    return None
            else:
                self.logger.error("当前平台不支持获取音量")
                return None
                
        except Exception as e:
            self.logger.error(f"获取音量失败: {str(e)}")
            return None
            
    def open_volume_mixer(self) -> bool:
        """打开系统音量合成器
        
        Returns:
            bool: 是否成功打开
        """
        try:
            if self.platform == "windows":
                # Windows: 使用sndvol.exe打开音量合成器
                subprocess.Popen("sndvol.exe")
                return True
            elif self.platform == "macos":
                # macOS: 打开系统偏好设置的声音面板
                subprocess.Popen(["open", "x-apple.systempreferences:com.apple.preference.sound"])
                return True
            elif self.platform == "linux":
                # Linux: 尝试打开常见的音量控制程序
                volume_controls = [
                    "pavucontrol",  # PulseAudio音量控制
                    "alsamixer",    # ALSA音量控制
                    "gnome-control-center sound"  # GNOME声音设置
                ]
                
                for control in volume_controls:
                    try:
                        subprocess.Popen(control.split())
                        return True
                    except FileNotFoundError:
                        continue
                
                self.logger.error("未找到可用的音量控制程序")
                return False
            else:
                self.logger.error(f"不支持的操作系统：{self.platform}")
                return False
                
        except Exception as e:
            self.logger.error(f"打开音量合成器失败：{str(e)}")
            return False
    
    def handle_command(self, command, params=None):
        """处理系统命令
        
        Args:
            command: 命令名称
            params: 命令参数
            
        Returns:
            bool: 命令执行是否成功
        """
        try:
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
                if app_path:
                    return self.launch_application(app_path)
                return False
            elif command == "get_system_info":
                return self.get_system_info()
            elif command == "get_display_info":
                return self.get_display_info()
            elif command == "toggle_display_mode":
                return self.toggle_display_mode()
            elif command == "rotate_display":
                return self.rotate_display()
            elif command == "get_volume":
                return self.get_volume()
            elif command == "open_volume_mixer":
                return self.open_volume_mixer()
            else:
                self.logger.error(f"未知的命令: {command}")
                return False
        except Exception as e:
            self.logger.error(f"执行命令失败: {command}, 错误: {str(e)}")
            return False 