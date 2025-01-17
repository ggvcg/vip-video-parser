import os
import sys
import json
import requests
import webbrowser
from datetime import datetime
from tkinter import messagebox

class AutoUpdater:
    def __init__(self):
        self.current_version = self.get_current_version()
        self.base_url = "http://47.122.133.57"
        self.app_name = "vip-parser"
        # 使用正确的版本文件路径
        self.version_url = f"{self.base_url}/downloads/{self.app_name}/v1.0.2/version-1.0.2.json"
        self.download_url = None
        print(f"初始化 AutoUpdater，当前版本：{self.current_version}")
        
    def get_current_version(self):
        """获取当前安装的版本号"""
        try:
            # 首先尝试在当前目录查找version.json
            local_version_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'version.json')
            print(f"尝试在可执行文件目录读取版本文件：{local_version_path}")
            
            if not os.path.exists(local_version_path):
                # 如果在可执行文件目录找不到，尝试在脚本目录查找
                local_version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
                print(f"尝试在脚本目录读取版本文件：{local_version_path}")
            
            if os.path.exists(local_version_path):
                with open(local_version_path, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    version = version_data.get('version', '1.0.0')
                    print(f"成功读取本地版本：{version}")
                    return version
            else:
                print(f"未找到版本文件：{local_version_path}")
                
        except Exception as e:
            print(f"读取版本信息失败: {e}")
            
        print("使用默认版本：1.0.0")
        return "1.0.0"

    def verify_version_exists(self, version):
        """验证指定版本是否在服务器上存在"""
        try:
            version_file_url = f"{self.base_url}/downloads/vip-parser/v{version}/version-{version}.json"  # 修改为正确的路径
            print(f"正在验证版本文件是否存在：{version_file_url}")
            request_kwargs = {
                'timeout': 5,
                'verify': False
            }
            
            try:
                response = requests.head(
                    version_file_url,
                    **request_kwargs,
                    proxies={'http': None, 'https': None}
                )
            except requests.exceptions.RequestException:
                response = requests.head(version_file_url, **request_kwargs)
            
            exists = response.status_code == 200
            print(f"版本 {version} {'存在' if exists else '不存在'}")
            return exists
        except Exception as e:
            print(f"验证版本存在性失败: {e}")
            return False

    def check_update(self):
        """检查更新"""
        try:
            print(f"\n开始检查更新，当前版本: {self.current_version}")
            
            # 获取最新版本
            latest_version = self.get_latest_version()
            print(f"获取到最新版本: {latest_version}")
            
            # 比较版本号
            if self._compare_versions(latest_version, self.current_version):
                print("发现新版本，准备更新")
                
                # 获取版本信息
                try:
                    response = requests.get(self.version_url, timeout=5, verify=False)
                    if response.status_code == 200:
                        version_info = response.json()
                        changelog = version_info.get('changelog', [])
                        force_update = version_info.get('force_update', False)
                        download_url = version_info.get('download_url')
                        
                        if not download_url:
                            raise ValueError("无法获取下载链接")
                        
                        # 构建更新消息
                        changelog_text = "\n".join([f"- {change}" for change in changelog])
                        message = f"发现新版本 {latest_version}\n当前版本：{self.current_version}\n\n更新内容：\n{changelog_text}"
                        
                        if force_update:
                            message = f"发现重要更新 {latest_version}，需要强制更新才能继续使用。\n\n更新内容：\n{changelog_text}"
                            if messagebox.showwarning("强制更新", message):
                                return self.download_update(download_url)
                            sys.exit(0)
                        else:
                            if messagebox.askyesno("发现新版本", message + "\n\n是否立即更新？"):
                                return self.download_update(download_url)
                        
                    else:
                        print(f"获取版本信息失败，状态码：{response.status_code}")
                        return False
                        
                except Exception as e:
                    print(f"检查更新失败: {e}")
                    messagebox.showerror("更新检查失败", 
                        f"无法获取更新信息：{str(e)}\n请检查网络连接后重试。")
                    return False
            else:
                print("当前已是最新版本")
                return False
                
        except Exception as e:
            print(f"检查更新失败: {e}")
            messagebox.showerror("更新检查失败", 
                f"检查更新失败：{str(e)}\n请检查网络连接后重试。")
            return False

    def download_update(self, download_url):
        """下载更新"""
        try:
            if not download_url:
                print("错误：没有可用的下载链接")
                return False
            
            self.download_url = download_url
            
            # 获取新版本信息
            try:
                response = requests.get(self.version_url, timeout=5, verify=False)
                if response.status_code == 200:
                    version_info = response.json()
                    new_version = version_info.get('version')
                    changelog = version_info.get('changelog', [])
                    force_update = version_info.get('force_update', False)
                    
                    if not new_version:
                        raise ValueError("无法获取新版本号")
                    
                    # 构建更新消息
                    changelog_text = "\n".join([f"- {change}" for change in changelog])
                    base_msg = f"发现新版本 {new_version}\n当前版本：{self.current_version}"
                    if changelog_text:
                        base_msg += f"\n\n更新内容：\n{changelog_text}"
                    
                    if force_update:
                        update_msg = f"{base_msg}\n\n这是一个强制更新版本，必须更新才能继续使用。"
                    else:
                        update_msg = f"{base_msg}\n\n是否现在更新？"
                    
                    # 显示更新提示
                    if force_update:
                        should_update = messagebox.showwarning("强制更新", update_msg)
                    else:
                        should_update = messagebox.askyesno("发现新版本", update_msg)
                    
                    if should_update:
                        try:
                            # 使用默认浏览器打开下载链接
                            print(f"正在打开下载链接：{download_url}")
                            webbrowser.open(download_url)
                            
                            # 更新本地版本文件
                            self.update_local_version(
                                new_version,
                                changelog
                            )
                            
                            # 提示用户关闭程序
                            messagebox.showinfo("更新提示", 
                                "新版本已开始下载。\n\n" +
                                "请在下载完成后：\n" +
                                "1. 关闭当前程序\n" +
                                "2. 用新下载的文件替换当前程序\n" +
                                "3. 运行新版本程序")
                            
                            if force_update:
                                sys.exit(0)
                            
                        except Exception as e:
                            print(f"打开下载链接失败: {e}")
                            messagebox.showerror("下载失败", 
                                f"无法打开下载链接：{str(e)}\n" +
                                "请手动复制链接下载：\n" +
                                f"{download_url}")
                            return False
                            
                else:
                    raise ValueError(f"获取版本信息失败，状态码：{response.status_code}")
                    
            except Exception as e:
                print(f"更新版本信息失败: {e}")
                messagebox.showwarning("警告", "版本信息更新失败，请稍后重试")
                return False
            
        except Exception as e:
            print(f"下载更新失败: {e}")
            messagebox.showerror("下载失败", f"无法下载更新：{str(e)}")
            return False

    def _compare_versions(self, version1, version2):
        """比较版本号，如果version1大于version2返回True"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # 补齐版本号长度
            while len(v1_parts) < 3:
                v1_parts.append(0)
            while len(v2_parts) < 3:
                v2_parts.append(0)
                
            # 比较版本号
            for i in range(len(v1_parts)):
                if v1_parts[i] > v2_parts[i]:
                    return True
                elif v1_parts[i] < v2_parts[i]:
                    return False
            return False
        except Exception as e:
            print(f"版本号比较失败: {e}")
            return False

    def update_local_version(self, new_version: str, changelog: list = None):
        """更新本地版本信息"""
        try:
            version_data = {
                'version': new_version,
                'release_date': datetime.now().strftime('%Y-%m-%d'),
                'changelog': changelog or []
            }
            
            # 首先尝试在可执行文件目录更新版本文件
            exe_version_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'version.json')
            script_version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
            
            try:
                # 尝试写入可执行文件目录
                with open(exe_version_path, 'w', encoding='utf-8') as f:
                    json.dump(version_data, f, ensure_ascii=False, indent=4)
                print(f"已更新可执行文件目录的版本文件：{exe_version_path}")
                success = True
            except Exception as e:
                print(f"无法写入可执行文件目录的版本文件: {e}")
                success = False
            
            if not success:
                # 如果写入可执行文件目录失败，尝试写入脚本目录
                try:
                    with open(script_version_path, 'w', encoding='utf-8') as f:
                        json.dump(version_data, f, ensure_ascii=False, indent=4)
                    print(f"已更新脚本目录的版本文件：{script_version_path}")
                    success = True
                except Exception as e:
                    print(f"无法写入脚本目录的版本文件: {e}")
                    success = False
            
            if success:
                self.current_version = new_version
                return True
            else:
                print("无法更新版本文件")
                return False
                
        except Exception as e:
            print(f"更新本地版本信息失败: {e}")
            return False
        
    def get_latest_version(self):
        """获取服务器上的最新版本号"""
        try:
            print(f"\n开始获取最新版本信息...")
            request_kwargs = {
                'timeout': 5,
                'verify': False,
                'headers': {
                    'Cache-Control': 'no-cache',
                    'Accept': 'application/json'
                }
            }
            
            try:
                print(f"正在连接服务器：{self.version_url}")
                response = requests.get(
                    self.version_url,
                    **request_kwargs,
                    proxies={'http': None, 'https': None}
                )
                
                print(f"服务器响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        version_info = response.json()
                        print(f"服务器返回的版本信息：{json.dumps(version_info, ensure_ascii=False, indent=2)}")
                        latest_version = version_info.get('version', '1.0.0')
                        
                        # 优先使用version_download_url
                        self.download_url = version_info.get('version_download_url')
                        if not self.download_url:
                            self.download_url = version_info.get('download_url')
                            
                        print(f"解析到的最新版本: {latest_version}")
                        print(f"下载链接: {self.download_url}")
                        
                        # 比较版本号
                        if self._compare_versions(latest_version, self.current_version):
                            print(f"发现新版本：{latest_version}")
                            return latest_version
                        else:
                            print(f"当前版本（{self.current_version}）已是最新")
                            return self.current_version
                            
                    except json.JSONDecodeError as e:
                        print(f"解析版本信息失败: {e}")
                        print(f"响应内容: {response.text[:200]}...")  # 只打印前200个字符
                        return self.current_version
                else:
                    print(f"服务器返回错误状态码: {response.status_code}")
                    return self.current_version
                
            except requests.exceptions.RequestException as e:
                print(f"连接服务器失败: {e}")
                return self.current_version
            
        except Exception as e:
            print(f"获取最新版本失败: {e}")
            return self.current_version
            
    def get_download_url(self):
        """获取下载链接"""
        try:
            response = requests.get(self.version_url, timeout=5, verify=False)
            if response.status_code == 200:
                version_info = response.json()
                return version_info.get('download_url')
        except Exception as e:
            print(f"获取下载链接失败: {e}")
        return None

if __name__ == '__main__':
    updater = AutoUpdater()
    updater.check_update() 
