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
        self.version_url = f"{self.base_url}/version.json"
        self.app_name = "vip_parser"
        print(f"初始化 AutoUpdater，当前版本：{self.current_version}")
        
    def get_current_version(self):
        """获取当前安装的版本号"""
        try:
            local_version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
            print(f"尝试读取版本文件：{local_version_path}")
            if os.path.exists(local_version_path):
                with open(local_version_path, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    version = version_data.get('version', '1.0.0')
                    print(f"成功读取本地版本：{version}")
                    return version
        except Exception as e:
            print(f"读取版本信息失败: {e}")
        print("使用默认版本：1.0.0")
        return "1.0.0"

    def verify_version_exists(self, version):
        """验证指定版本是否在服务器上存在"""
        try:
            version_file_url = f"{self.base_url}/versions/v{version}.json"
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
            
            request_kwargs = {
                'timeout': 5,
                'verify': False
            }
            
            try:
                print(f"正在获取版本信息：{self.version_url}")
                response = requests.get(
                    self.version_url,
                    **request_kwargs,
                    proxies={'http': None, 'https': None}
                )
            except requests.exceptions.RequestException as e:
                print(f"直接连接失败，错误: {e}")
                response = requests.get(self.version_url, **request_kwargs)
                
            print(f"服务器响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                version_info = response.json()
                print(f"服务器返回的版本信息：{json.dumps(version_info, ensure_ascii=False, indent=2)}")
                latest_version = version_info.get('version', '1.0.0')
                print(f"服务器声明的最新版本: {latest_version}")
                
                # 验证最新版本文件是否实际存在
                found_version = None
                if not self.verify_version_exists(latest_version):
                    print(f"版本 {latest_version} 不存在，寻找最近的可用版本")
                    # 如果最新版本不存在，尝试找到最近的可用版本
                    version_parts = [int(x) for x in latest_version.split('.')]
                    while version_parts[-1] >= 0:
                        test_version = '.'.join(map(str, version_parts))
                        if self.verify_version_exists(test_version):
                            found_version = test_version
                            print(f"找到可用版本: {found_version}")
                            break
                        version_parts[-1] -= 1
                        print(f"尝试检查版本: {test_version}")
                else:
                    found_version = latest_version
                
                if not found_version:
                    print("未找到任何可用版本")
                    return False
                    
                print(f"最终确定的最新版本: {found_version}")
                print(f"当前版本: {self.current_version}")
                
                # 如果版本号相同，直接返回 False
                if found_version == self.current_version:
                    print("当前已是最新版本")
                    return False
                
                # 检查是否需要更新
                need_update = self._compare_versions(found_version, self.current_version)
                print(f"是否需要更新: {need_update}")
                
                if need_update:
                    changelog = version_info.get('changelog', [])
                    force_update = version_info.get('force_update', False)
                    
                    # 更新版本信息中的版本号
                    version_info['version'] = found_version
                    
                    changelog_text = "\n".join([f"- {change}" for change in changelog])
                    message = f"发现新版本 {found_version}\n当前版本：{self.current_version}\n\n更新内容：\n{changelog_text}\n\n是否立即更新？"
                    
                    if force_update:
                        message = f"发现重要更新 {found_version}，需要强制更新才能继续使用。\n\n更新内容：\n{changelog_text}"
                        result = messagebox.showwarning("强制更新", message)
                        if result == 'ok':
                            self.download_update(version_info.get('download_url'))
                        sys.exit(0)
                    else:
                        result = messagebox.askyesno("发现新版本", message)
                        if result:
                            self.download_update(version_info.get('download_url'))
                    return True
                else:
                    print("当前已是最新版本")
                    return False
        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {e}")
            raise Exception(f"网络连接失败: {str(e)}\n请检查网络连接或关闭代理后重试。")
        except Exception as e:
            print(f"检查更新失败: {e}")
            raise

    def download_update(self, download_url):
        """下载更新"""
        try:
            if not download_url:
                raise ValueError("下载链接无效")
                
            # 使用默认浏览器打开下载链接
            webbrowser.open(download_url)
            messagebox.showinfo("下载更新", "已打开下载页面，请下载并安装新版本。\n安装完成后需要重启应用。")
        except Exception as e:
            messagebox.showerror("下载失败", f"无法下载更新：{str(e)}")

    def _compare_versions(self, new_version: str, current_version: str) -> bool:
        """比较版本号，返回是否需要更新"""
        try:
            print(f"正在比较版本：新版本 {new_version} vs 当前版本 {current_version}")
            if new_version == current_version:
                print("版本号完全相同")
                return False
                
            new_parts = [int(x) for x in new_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            # 补齐版本号长度
            while len(new_parts) < 3:
                new_parts.append(0)
            while len(current_parts) < 3:
                current_parts.append(0)
            
            print(f"版本号分解：新版本 {new_parts} vs 当前版本 {current_parts}")
            
            # 逐位比较
            for new, current in zip(new_parts, current_parts):
                if new > current:
                    print(f"新版本较新：{new} > {current}")
                    return True
                elif new < current:
                    print(f"当前版本较新：{new} < {current}")
                    return False
            print("版本号完全相同")
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
            
            local_version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
            with open(local_version_path, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, ensure_ascii=False, indent=4)
            
            self.current_version = new_version
            return True
        except Exception as e:
            print(f"更新本地版本信息失败: {e}")
            return False
        
if __name__ == '__main__':
    updater = AutoUpdater()
    updater.check_update() 