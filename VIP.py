import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from tkinter.scrolledtext import ScrolledText
import pyperclip
from auto_updater import AutoUpdater  # 导入自动更新器
import json
import os
import concurrent.futures
import threading
import requests
import logging
import datetime
import time
from urllib.parse import urlparse


def create_retry_strategy():
    """创建请求重试策略"""
    return requests.adapters.Retry(
        total=3,  # 总重试次数
        backoff_factor=0.5,  # 重试延迟因子
        status_forcelist=[500, 502, 503, 504],  # 需要重试的HTTP状态码
        allowed_methods=["HEAD", "GET", "POST"],  # 允许重试的请求方法
        raise_on_redirect=False,  # 重定向不抛出异常
        raise_on_status=False  # 状态码错误不抛出异常
    )


class VIPVideoParser:
    def __init__(self):
        """初始化上传工具"""
        self.window = tk.Tk()
        self.window.title('VIP视频解析工具')
        self.window.geometry('1000x800')
        self.window.resizable(True, True)
        
        # 设置主题和样式
        self.setup_styles()
        
        # 初始化API状态
        self.api_status = {}
        
        # 解析接口列表
        self.api_list = {
            '线路1 - 稳定(需要VPN)': 'https://jx.playerjy.com/?url=',  # 需要VPN访问
            '线路2 - 备用': 'https://jx.jsonplayer.com/player/?url=',
            '线路3 - 通用': 'https://jx.aidouer.net/?url=',
            '线路4 - 高速': 'https://jx.bozrc.com:4433/player/?url=',
            '线路5 - 超清': 'https://jx.zhanlangbu.com/?url=',
            '线路6 - 急速': 'https://jx.ppflv.com/?url=',
            '线路7 - 优选': 'https://jx.xyflv.com/?url=',
            '线路8 - 备选': 'https://jx.m3u8.tv/jiexi/?url=',
            '线路9 - M3U8': 'https://jx.m3u8.pw/?url=',
            '线路10 - 全能': 'https://jx.xyflv.cc/?url=',
            '线路11 - 智能': 'https://jx.jsonplayer.net/player/?url=',
            '线路12 - 解析': 'https://jx.xmflv.com/?url=',
            '线路13 - 云解析': 'https://jx.yparse.com/index.php?url=',
            '线路14 - 8090': 'https://www.8090g.cn/?url=',
            '线路15 - 快速': 'https://api.jiexi.la/?url=',
            '线路16 - 免费': 'https://www.pangujiexi.cc/jiexi.php?url=',
            '线路17 - 高清': 'https://www.ckmov.vip/api.php?url=',
            '线路18 - B站1': 'https://jx.bozrc.com:4433/player/?url=',
            '线路19 - B站2': 'https://jx.parwix.com:4433/player/?url=',
            '线路20 - 万能': 'https://jx.ivito.cn/?url=',
            '线路21 - OK': 'https://okjx.cc/?url=',
            '线路22 - 夜幕': 'https://www.yemu.xyz/?url=',
            '线路23 - 虾米': 'https://jx.xmflv.com/?url=',
            '线路24 - 爱豆': 'https://jx.aidouer.net/?url=',
            '线路25 - 诺讯': 'https://www.nxflv.com/?url='
        }
        
        # 初始化变量
        self.api_var = tk.StringVar(value='线路1 - 稳定(需要VPN)')
        self.history = []
        self.max_history = 10  # 最多保存10条历史记录
        
        # 优化缓存管理
        self.cache = {}
        self.cache_limit = 100  # 缓存限制
        self.cache_expire_time = 3600  # 缓存过期时间（秒）
        self.cache_hits = 0  # 缓存命中次数
        self.cache_misses = 0  # 缓存未命中次数
        
        # 启动定期清理缓存的定时器
        self.start_cache_cleanup()
        
        # 网络状态监控
        self.network_status = {'status': True, 'last_check': time.time()}
        self.start_network_monitor()
        
        # API性能统计
        self.api_performance = {}  # 用于存储API响应时间统计
        
        # 优化线程池配置
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=min(32, (os.cpu_count() or 1) * 4),  # 根据CPU核心数动态设置
            thread_name_prefix="VIPParser"
        )
        
        # 优化请求会话配置
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100,  # 连接池大小
            pool_maxsize=100,  # 最大连接数
            max_retries=create_retry_strategy(),  # 重试策略
            pool_block=False  # 连接池满时不阻塞
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        
        # 优化重试策略配置
        self.request_timeout = 5  # 将超时时间从10秒减少到5秒
        self.max_retries = 2  # 将重试次数从3次减少到2次
        self.retry_delay = 0.5  # 将重试延迟从1秒减少到0.5秒
        self.retry_backoff = 2  # 重试延迟倍数
        self.retry_max_delay = 10  # 最大重试延迟（秒）
        
        # 添加性能监控
        self.performance_metrics = {
            'parse_times': [],  # 解析时间记录
            'api_response_times': {},  # API响应时间
            'cache_hits': 0,  # 缓存命中次数
            'cache_misses': 0,  # 缓存未命中次数
            'failed_attempts': 0,  # 失败尝试次数
        }
        
        # 创建菜单栏
        self.create_menu()
        
        # 初始化状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_bar = ttk.Label(self.window, textvariable=self.status_var,
                                  relief=tk.SUNKEN, padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 检查更新
        self.window.after(1000, self.check_update)  # 延迟1秒检查更新
        
        # 设置窗口图标
        try:
            self.window.iconbitmap('portfolio.ico')
        except:
            pass
            
        # 设置窗口最小尺寸
        self.window.minsize(800, 600)
        
        # 创建主框架为PanedWindow
        main_paned = ttk.PanedWindow(self.window, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部分框架
        upper_frame = ttk.Frame(main_paned)
        main_paned.add(upper_frame, weight=1)
        
        # 标题
        title_label = ttk.Label(upper_frame, text="VIP视频解析工具", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # URL输入区域
        url_frame = ttk.LabelFrame(upper_frame, text="视频链接", padding=10)
        url_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # 使用Grid布局管理URL输入框和按钮组
        url_frame.grid_columnconfigure(0, weight=1)  # URL输入框列可扩展
        
        # URL输入框
        self.url_entry = ttk.Entry(url_frame, font=('微软雅黑', 11))
        self.url_entry.grid(row=0, column=0, sticky='ew', padx=5)
        
        # 按钮组
        btn_group = ttk.Frame(url_frame)
        btn_group.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Button(btn_group, text="粘贴", 
                  command=self.paste_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_group, text="清空",
                  command=self.clear_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_group, text="历史",
                  command=self.show_history).pack(side=tk.LEFT, padx=2)
        
        # 解析线路区域
        line_frame = ttk.LabelFrame(upper_frame, text="解析线路", padding=10)
        line_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 10))
        
        # 使用Grid布局管理解析线路按钮
        self.radio_frame = ttk.Frame(line_frame)
        self.radio_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置Grid列权重
        columns_per_row = 5
        for i in range(columns_per_row):
            self.radio_frame.grid_columnconfigure(i, weight=1)
        
        # 创建解析线路单选按钮
        for i, api in enumerate(self.api_list.keys()):
            row = i // columns_per_row
            col = i % columns_per_row
            btn_frame = ttk.Frame(self.radio_frame)
            btn_frame.grid(row=row, column=col, sticky='nsew')
            btn_frame.grid_columnconfigure(0, weight=1)
            
            radio_btn = ttk.Radiobutton(btn_frame, text=api, 
                                      variable=self.api_var,
                                      value=api)
            radio_btn.grid(padx=2, pady=1, sticky='w')
        
        # 下部分框架
        lower_frame = ttk.Frame(main_paned)
        main_paned.add(lower_frame, weight=1)
        
        # 操作按钮区域
        btn_frame = ttk.Frame(lower_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="开始解析", style='Primary.TButton',
                  command=self.parse_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="使用帮助", style='Primary.TButton',
                  command=self.show_help).pack(side=tk.LEFT, padx=5)
        
        # 快速访问区域
        quick_frame = ttk.LabelFrame(lower_frame, text="快速访问", padding=10)
        quick_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 10))
        
        # 使用Grid布局管理快速访问按钮
        sites = [
            ('爱奇艺', 'https://www.iqiyi.com'),
            ('腾讯视频', 'https://v.qq.com'),
            ('优酷视频', 'https://www.youku.com'),
            ('芒果TV', 'https://www.mgtv.com'),
            ('哔哩哔哩', 'https://www.bilibili.com'),
            ('搜狐视频', 'https://tv.sohu.com'),
            ('PP视频', 'https://www.pptv.com'),
            ('1905影视', 'https://www.1905.com')
        ]
        
        # 配置Grid列权重
        quick_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        for i, (name, url) in enumerate(sites):
            row = i // 4
            col = i % 4
            btn = ttk.Button(quick_frame, text=name, style='Quick.TButton',
                           command=lambda u=url: webbrowser.open(u))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # 支持的网站列表
        site_frame = ttk.LabelFrame(lower_frame, text="支持的视频网站", padding=10)
        site_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        self.sites_text = ScrolledText(site_frame, wrap=tk.WORD,
                                     font=('微软雅黑', 10),
                                     height=6,
                                     bg='white')
        self.sites_text.pack(fill=tk.BOTH, expand=True)
        
        sites_info = """✓ 爱奇艺 (www.iqiyi.com)
✓ 腾讯视频 (v.qq.com)
✓ 优酷视频 (www.youku.com)
✓ 芒果TV (www.mgtv.com)
✓ 哔哩哔哩 (www.bilibili.com)
✓ 搜狐视频 (tv.sohu.com)
✓ PP视频 (www.pptv.com)
✓ 1905电影网 (www.1905.com)

使用说明：
1. 复制需要解析的视频页面完整链接
2. 点击"粘贴"按钮或直接粘贴到输入框
3. 选择解析线路（建议从线路1开始尝试）
4. 点击"开始解析"
5. 如果当前线路解析失败，请尝试其他线路

注意事项：
· 建议支持正版，尊重知识产权
· 仅供学习交流使用，请勿用于商业用途
· 部分视频可能需要多次尝试不同线路"""
        
        self.sites_text.insert(tk.END, sites_info)
        self.sites_text.configure(state='disabled')
        
        # 绑定窗口大小变化事件
        self.window.bind('<Configure>', self._on_window_configure)
        
        # 加载历史记录
        self.load_history()
        
        # 加载配置
        self.load_config()
        
        # 配置日志
        self.setup_logging()
        
        # 绑定快捷键
        self.bind_shortcuts()

    def _on_window_configure(self, event):
        """处理窗口大小变化事件"""
        if event.widget == self.window:
            # 保存新的窗口大小到配置
            self.save_config()
            
            # 更新UI布局
            self.window.update_idletasks()

    def paste_url(self):
        """粘贴剪贴板内容到输入框"""
        try:
            url = pyperclip.paste()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            self.status_var.set("已粘贴链接")
        except Exception as e:
            messagebox.showerror("错误", f"无法访问剪贴板：{str(e)}\n请手动复制粘贴")

    def clear_url(self):
        """清空输入框"""
        self.url_entry.delete(0, tk.END)
        self.status_var.set("已清空链接")

    def show_help(self):
        """显示帮助信息"""
        help_window = tk.Toplevel(self.window)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        help_window.transient(self.window)
        help_window.grab_set()
        
        # 设置窗口样式
        help_window.configure(bg=self.style.lookup('TFrame', 'background'))
        
        # 创建主框架
        main_frame = ttk.Frame(help_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame,
                              text="使用帮助",
                              style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 创建Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 基本使用标签页
        basic_frame = ttk.Frame(notebook, padding=10)
        notebook.add(basic_frame, text="基本使用")
        
        basic_text = """1. 复制视频链接
• 在视频网站找到想要观看的视频
• 复制视频页面的完整链接

2. 粘贴链接
• 点击"粘贴"按钮或使用Ctrl+V
• 链接会自动粘贴到输入框

3. 选择解析线路
• 推荐优先使用线路1
• 如果解析失败可依次尝试其他线路

4. 开始解析
• 点击"开始解析"按钮或按Ctrl+Enter
• 等待解析完成后会自动打开视频"""
        
        basic_label = ttk.Label(basic_frame, text=basic_text,
                              justify=tk.LEFT, wraplength=500)
        basic_label.pack(fill=tk.BOTH, expand=True)
        
        # 快捷键标签页
        shortcut_frame = ttk.Frame(notebook, padding=10)
        notebook.add(shortcut_frame, text="快捷键")
        
        shortcuts = [
            ("Ctrl + V", "粘贴链接"),
            ("Ctrl + Enter", "开始解析"),
            ("Ctrl + H", "显示历史记录"),
            ("Ctrl + L", "清空输入框"),
            ("F5", "检测解析线路"),
            ("F1", "显示本帮助")
        ]
        
        for key, desc in shortcuts:
            row = ttk.Frame(shortcut_frame)
            row.pack(fill=tk.X, pady=5)
            
            ttk.Label(row, text=key,
                     font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 20))
            ttk.Label(row, text=desc,
                     font=('微软雅黑', 10)).pack(side=tk.LEFT)
        
        # 常见问题标签页
        faq_frame = ttk.Frame(notebook, padding=10)
        notebook.add(faq_frame, text="常见问题")
        
        faq_text = """Q: 为什么视频解析失败？
A: 可能是当前线路不稳定，请尝试其他解析线路。

Q: 支持哪些视频网站？
A: 支持爱奇艺、腾讯视频、优酷、芒果TV等主流视频网站。

Q: 解析后视频无法播放怎么办？
A: 1. 确保输入的是完整的视频页面链接
   2. 尝试使用其他浏览器打开
   3. 更换其他解析线路

Q: 为什么有时候会很慢？
A: 解析速度取决于网络状况和服务器负载，建议耐心等待或更换线路。"""
        
        faq_label = ttk.Label(faq_frame, text=faq_text,
                            justify=tk.LEFT, wraplength=500)
        faq_label.pack(fill=tk.BOTH, expand=True)
        
        # 注意事项标签页
        notice_frame = ttk.Frame(notebook, padding=10)
        notebook.add(notice_frame, text="注意事项")
        
        notice_text = """• 本工具仅供学习交流使用
• 请勿用于任何商业用途
• 建议支持正版，尊重知识产权
• 部分视频可能需要多次尝试
• 定期检查更新以获得最佳体验
• 如遇问题请查看常见问题解答"""
        
        notice_label = ttk.Label(notice_frame, text=notice_text,
                               justify=tk.LEFT, wraplength=500)
        notice_label.pack(fill=tk.BOTH, expand=True)
        
        # 确定按钮
        ttk.Button(main_frame, text="我知道了",
                  command=help_window.destroy,
                  style='Primary.TButton').pack()
        
        # 使窗口居中
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry(f'{width}x{height}+{x}+{y}')

    def parse_video(self):
        """解析视频（支持批量解析）"""
        # 首先检查网络状态
        if not self.network_status['status']:
            if not messagebox.askyesno("网络异常",
                "当前网络连接异常，是否继续尝试解析？"):
                return
        
        urls = self.url_entry.get().strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        if not urls:
            self.logger.warning("用户未输入URL")
            messagebox.showwarning("警告", "请输入视频链接")
            return
            
        # 创建批量解析状态窗口
        status_window = tk.Toplevel(self.window)
        status_window.title("批量解析进度")
        status_window.geometry("600x400")
        status_window.transient(self.window)
        status_window.grab_set()
        
        # 添加状态标签
        status_label = ttk.Label(status_window, 
                               text=f"正在解析 {len(urls)} 个视频...", 
                               font=('微软雅黑', 10))
        status_label.pack(pady=10)
        
        # 添加总进度条
        total_progress_var = tk.DoubleVar()
        total_progress_bar = ttk.Progressbar(status_window, 
                                           variable=total_progress_var,
                                           maximum=len(urls), 
                                           length=500, 
                                           mode='determinate')
        total_progress_bar.pack(pady=10)
        
        # 添加当前任务进度条
        task_progress_var = tk.DoubleVar()
        task_progress_bar = ttk.Progressbar(status_window, 
                                          variable=task_progress_var,
                                          maximum=100, 
                                          length=500, 
                                          mode='determinate')
        task_progress_bar.pack(pady=5)
        
        # 添加详细信息文本框
        info_text = ScrolledText(status_window, height=15, width=60)
        info_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        def update_status(text, total_progress=None, task_progress=None):
            info_text.insert(tk.END, text + "\n")
            info_text.see(tk.END)
            if total_progress is not None:
                total_progress_var.set(total_progress)
            if task_progress is not None:
                task_progress_var.set(task_progress)
            status_window.update()
        
        # 获取当前选中的解析线路
        selected_api = self.api_var.get()
        if not selected_api or selected_api not in self.api_list:
            # 如果没有选择线路，尝试使用性能最好的线路
            best_api = self.get_best_api()
            if best_api:
                selected_api = best_api
                self.api_var.set(best_api)
            else:
                messagebox.showwarning("警告", "请选择解析线路")
                status_window.destroy()
                return
        
        # 检查是否需要VPN
        if "需要VPN" in selected_api:
            if not messagebox.askyesno("VPN提示", 
                "当前选择的解析线路需要开启VPN才能访问。\n是否已开启VPN？"):
                status_window.destroy()
                return
        
        try:
            success_count = 0
            for i, url in enumerate(urls):
                try:
                    update_status(f"\n开始解析第 {i+1}/{len(urls)} 个视频:", 
                                total_progress=i)
                    
                    # 验证URL格式
                    if not self._validate_url(url):
                        update_status(f"错误：无效的视频网站链接 - {url}", 
                                    task_progress=0)
                        continue
                    
                    # 检查缓存
                    cache_key = f"{selected_api}_{url}"
                    cached_result = self._get_from_cache(cache_key)
                    if cached_result:
                        update_status("使用缓存记录...", task_progress=50)
                        webbrowser.open(cached_result)
                        update_status("解析完成！", task_progress=100)
                        success_count += 1
                        continue
                    
                    # 添加到历史记录
                    self.add_to_history(url)
                    update_status("已保存到历史记录", task_progress=30)
                    
                    # 构造解析URL
                    api_url = self.api_list[selected_api]
                    parse_url = api_url + url
                    update_status("正在连接解析服务器...", task_progress=60)
                    
                    # 测试解析链接可用性
                    if not self._check_url_availability(parse_url):
                        raise Exception("当前解析线路不可用")
                    
                    update_status("正在打开解析链接...", task_progress=80)
                    webbrowser.open(parse_url)
                    
                    # 添加到缓存
                    self._add_to_cache(cache_key, parse_url)
                    update_status("已缓存解析结果", task_progress=90)
                    
                    success_count += 1
                    update_status("解析完成！", task_progress=100)
                    
                except Exception as e:
                    update_status(f"解析失败: {str(e)}", task_progress=0)
                    if selected_api in self.api_performance:
                        self.api_performance[selected_api]['fail_count'] += 1
                    continue
            
            # 更新总进度
            total_progress_var.set(len(urls))
            
            # 显示最终结果
            update_status(f"\n批量解析完成！成功: {success_count}/{len(urls)}")
            self.status_var.set(f"批量解析完成 - 成功率: {success_count}/{len(urls)}")
            
            # 优化API顺序
            self.optimize_api_order()
            
        except Exception as e:
            update_status(f"发生错误：{str(e)}")
            self.logger.error(f"批量解析失败: {str(e)}")
            messagebox.showerror("错误", f"批量解析失败: {str(e)}")
        
        # 添加关闭按钮
        ttk.Button(status_window, 
                  text="关闭", 
                  command=status_window.destroy).pack(pady=10)

    def _validate_url(self, url):
        """验证URL格式"""
        valid_domains = [
            'iqiyi.com', 'v.qq.com', 'youku.com', 'mgtv.com', 
            'bilibili.com', 'tv.sohu.com', 'pptv.com', '1905.com'
        ]
        try:
            result = urlparse(url)
            return all([
                result.scheme in ['http', 'https'],
                any(domain in result.netloc.lower() for domain in valid_domains)
            ])
        except:
            return False

    def _check_url_availability(self, url):
        """检查URL可用性（优化版本）"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.head(
                    url,
                    timeout=self.request_timeout,
                    allow_redirects=True,
                    verify=False
                )
                
                if response.status_code == 200:
                    return True
                return False
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False

    def _get_from_cache(self, key):
        """从缓存获取数据"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_expire_time:
                self.cache_hits += 1
                return data
            else:
                del self.cache[key]
        self.cache_misses += 1
        return None

    def _add_to_cache(self, key, value):
        """添加数据到缓存"""
        self.cache[key] = (value, time.time())
        # 如果缓存超出限制，删除最早的条目
        if len(self.cache) > self.cache_limit:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

    def check_update(self):
        """检查更新"""
        try:
            # 显示准备检查更新的状态
            self.status_var.set("正在检查更新...")
            self.window.update()
            
            updater = AutoUpdater()
            current_version = updater.get_current_version()
            latest_version = updater.get_latest_version()
            
            print(f"当前版本：{current_version}")
            print(f"最新版本：{latest_version}")
            
            # 比较版本号，只有新版本才显示更新窗口
            if not updater._compare_versions(latest_version, current_version):
                print("当前已是最新版本")
                self.status_var.set(f"已是最新版本 (当前版本: {current_version})")
                return
            
            # 创建更新窗口
            update_window = tk.Toplevel(self.window)
            update_window.title("发现新版本")
            update_window.geometry("500x600")
            update_window.transient(self.window)
            update_window.grab_set()
            
            # 设置窗口样式
            update_window.configure(bg='white')
            
            # 创建主框架
            main_frame = ttk.Frame(update_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # 图标
            icon_label = ttk.Label(main_frame, text="↑",
                                font=('微软雅黑', 24))
            icon_label.pack(pady=(0, 10))
            
            # 版本信息
            version_label = ttk.Label(main_frame,
                                   text=f"发现新版本：{latest_version}\n当前版本：{current_version}",
                                   font=('微软雅黑', 10))
            version_label.pack(pady=5)
            
            # 获取更新内容
            try:
                response = requests.get(updater.version_url, timeout=5, verify=False)
                if response.status_code == 200:
                    version_info = response.json()
                    update_text = "更新内容:\n" + "\n".join([f"- {item}" for item in version_info.get('changelog', [])])
                else:
                    update_text = "无法获取更新内容"
            except:
                update_text = "无法获取更新内容"
            
            # 创建文本框架
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 20))
            
            info_text = ScrolledText(text_frame, height=20,
                                  font=('微软雅黑', 9),
                                  wrap=tk.WORD)
            info_text.pack(fill=tk.BOTH, expand=True)
            info_text.insert(tk.END, update_text)
            info_text.configure(state='disabled')
            
            # 按钮框架
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=(0, 10))
            
            # 统一按钮样式
            button_style = {
                'width': 20,
                'style': 'Primary.TButton'
            }
            
            # 左侧按钮
            left_btn_frame = ttk.Frame(btn_frame)
            left_btn_frame.pack(side=tk.LEFT)
            
            ttk.Button(left_btn_frame, text="立即更新",
                     command=lambda: self.do_update(update_window, updater),
                     **button_style).pack(side=tk.LEFT, padx=(0, 10))
            
            # 右侧按钮
            right_btn_frame = ttk.Frame(btn_frame)
            right_btn_frame.pack(side=tk.RIGHT)
            
            ttk.Button(right_btn_frame, text="暂不更新",
                     command=update_window.destroy,
                     **button_style).pack(side=tk.RIGHT)
            
            # 使窗口居中
            update_window.update_idletasks()
            width = update_window.winfo_width()
            height = update_window.winfo_height()
            x = (update_window.winfo_screenwidth() // 2) - (width // 2)
            y = (update_window.winfo_screenheight() // 2) - (height // 2)
            update_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # 更新状态栏
            self.status_var.set(f"发现新版本：{latest_version}")
            
        except Exception as e:
            self.logger.error(f"检查更新失败: {str(e)}")
            self.status_var.set("检查更新失败")
            messagebox.showerror("更新检查失败", f"无法检查更新：{str(e)}\n请检查网络连接后重试。")

    def do_update(self, update_window, updater):
        """执行更新操作"""
        try:
            # 关闭更新窗口
            update_window.destroy()
            
            # 显示更新进度窗口
            progress_window = tk.Toplevel(self.window)
            progress_window.title("正在更新")
            progress_window.geometry("400x150")
            progress_window.transient(self.window)
            progress_window.grab_set()
            
            # 进度标签
            progress_label = ttk.Label(progress_window, text="正在获取更新信息...",
                                     font=('微软雅黑', 10))
            progress_label.pack(pady=10)
            
            def update_status(text):
                progress_label.config(text=text)
                progress_window.update()
            
            try:
                # 获取下载链接
                update_status("正在获取下载链接...")
                download_url = updater.get_download_url()
                
                if download_url:
                    update_status("正在准备下载...")
                    if updater.download_update(download_url):
                        update_status("更新文件已开始下载...")
                        progress_window.after(3000, progress_window.destroy)  # 3秒后关闭窗口
                    else:
                        update_status("下载失败，请稍后重试")
                        progress_window.after(2000, progress_window.destroy)
                else:
                    messagebox.showerror("更新失败", "无法获取下载链接")
                    progress_window.destroy()
                    
            except Exception as e:
                self.logger.error(f"执行更新失败: {str(e)}")
                messagebox.showerror("更新失败", f"更新过程出错：{str(e)}\n请稍后重试。")
                progress_window.destroy()
            
        except Exception as e:
            self.logger.error(f"执行更新失败: {str(e)}")
            messagebox.showerror("更新失败", f"更新过程出错：{str(e)}\n请稍后重试。")

    def show_history(self):
        """显示历史记录"""
        if not self.history:
            messagebox.showinfo("历史记录", "暂无历史记录")
            return
            
        history_window = tk.Toplevel(self.window)
        history_window.title("历史记录")
        history_window.geometry("1000x700")  # 设置初始窗口大小
        history_window.minsize(800, 600)  # 设置最小窗口大小
        history_window.transient(self.window)
        history_window.grab_set()
        
        # 设置窗口样式
        history_window.configure(bg=self.style.lookup('TFrame', 'background'))
        
        # 创建主框架
        main_frame = ttk.Frame(history_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="历史记录",
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        # 创建列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建Treeview
        columns = ('时间', 'URL')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # 设置列
        tree.heading('时间', text='时间')
        tree.heading('URL', text='视频链接')
        
        tree.column('时间', width=200)
        tree.column('URL', width=750)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加历史记录
        for url in self.history:
            tree.insert('', tk.END, values=(
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                url
            ))
        
        # 底部按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        def use_selected():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                url = item['values'][1]
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, url)
                history_window.destroy()
                
        # 创建统一样式的按钮
        button_style = {
            'width': 15,  # 统一按钮宽度
            'padding': 5  # 统一内边距
        }
        
        # 左侧按钮
        left_btn_frame = ttk.Frame(btn_frame)
        left_btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        use_btn = ttk.Button(left_btn_frame, 
                          text="使用选中链接",
                          command=use_selected,
                          style='Primary.TButton',
                          **button_style)
        use_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(left_btn_frame,
                           text="清空历史",
                           command=lambda: [self.clear_history(), history_window.destroy()],
                           style='Primary.TButton',
                           **button_style)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 右侧按钮
        right_btn_frame = ttk.Frame(btn_frame)
        right_btn_frame.pack(side=tk.RIGHT)
        
        close_btn = ttk.Button(right_btn_frame,
                           text="关闭",
                           command=history_window.destroy,
                           style='Primary.TButton',
                           **button_style)
        close_btn.pack(side=tk.RIGHT)
        
        # 双击选中条目
        tree.bind('<Double-1>', lambda e: use_selected())
        
        # 使窗口居中
        history_window.update_idletasks()
        width = history_window.winfo_width()
        height = history_window.winfo_height()
        x = (history_window.winfo_screenwidth() // 2) - (width // 2)
        y = (history_window.winfo_screenheight() // 2) - (height // 2)
        history_window.geometry(f'{width}x{height}+{x}+{y}')

    def run(self):
        """运行程序"""
        try:
            self.window.iconbitmap('portfolio.ico')
        except:
            pass
            
        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
    
    def on_closing(self):
        """窗口关闭时的处理"""
        try:
            self.save_config()  # 保存配置
            self.save_history()  # 保存历史记录
            self.logger.info("程序正常退出")
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            print(f"保存数据失败: {e}")
        self.window.destroy()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="检查更新", command=self.check_update)
        file_menu.add_command(label="检测解析线路", command=self.check_api_availability)
        file_menu.add_command(label="线路测速", command=self.auto_test_api_speed)
        file_menu.add_command(label="清空缓存", command=self.clear_cache)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.window.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="清空历史记录", command=self.clear_history)
        tools_menu.add_command(label="重置窗口大小", 
                             command=lambda: self.window.geometry('1000x800'))
        tools_menu.add_command(label="管理解析线路", command=self.manage_api_list)
        tools_menu.add_command(label="线路测速排序", command=self.auto_test_api_speed)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用帮助", command=self.show_help)
        help_menu.add_command(label="检查更新", command=self.check_update)
        help_menu.add_separator()
        help_menu.add_command(label="关于", command=self.show_about)
        
    def show_about(self):
        """显示关于信息"""
        about_window = tk.Toplevel(self.window)
        about_window.title("关于")
        about_window.geometry("500x400")
        about_window.transient(self.window)
        about_window.grab_set()
        
        # 设置窗口样式
        about_window.configure(bg=self.style.lookup('TFrame', 'background'))
        
        # 创建主框架
        main_frame = ttk.Frame(about_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo区域（如果有logo的话）
        try:
            logo_img = tk.PhotoImage(file='portfolio.ico')
            logo_label = ttk.Label(main_frame, image=logo_img)
            logo_label.image = logo_img  # 保持引用
            logo_label.pack(pady=(0, 20))
        except:
            pass
        
        # 标题
        title_label = ttk.Label(main_frame,
                              text="VIP视频解析工具",
                              style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # 版本信息
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        version_label = ttk.Label(version_frame,
                                text=f"版本 {self.get_version()}",
                                font=('微软雅黑', 12))
        version_label.pack()
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # 作者信息
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        author_info = [
            ("作者", "刘柱"),
            ("邮箱", "18558995273@163.com"),
            ("开发时间", "2024年"),
            ("支持格式", "主流视频网站VIP视频"),
            ("运行环境", "Windows 7/8/10/11")
        ]
        
        for label, value in author_info:
            row = ttk.Frame(info_frame)
            row.pack(fill=tk.X, pady=5)
            
            ttk.Label(row, text=label + "：",
                     font=('微软雅黑', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(row, text=value,
                     font=('微软雅黑', 10)).pack(side=tk.LEFT)
        
        # 分隔线
        separator2 = ttk.Separator(main_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=10)
        
        # 版权信息
        copyright_label = ttk.Label(main_frame,
                                  text="Copyright © 2024 保留所有权利",
                                  font=('微软雅黑', 9))
        copyright_label.pack(pady=(0, 20))
        
        # 确定按钮
        ttk.Button(main_frame, text="确定",
                  command=about_window.destroy,
                  style='Primary.TButton').pack()
        
        # 使窗口居中
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'{width}x{height}+{x}+{y}')
                  
    def get_version(self):
        """获取当前版本号"""
        try:
            with open('version.json', 'r', encoding='utf-8') as f:
                version_info = json.load(f)
                return version_info.get('version', '1.0.0')
        except Exception:
            return "1.0.0"

    def check_api_availability(self):
        """检查所有解析线路的可用性（优化版本）"""
        check_window = tk.Toplevel(self.window)
        check_window.title("检测解析线路")
        check_window.geometry("500x600")
        check_window.transient(self.window)
        check_window.grab_set()
        
        # 设置窗口样式
        check_window.configure(bg='white')
        
        # 创建主框架
        main_frame = ttk.Frame(check_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 标题区域
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 图标和标题
        icon_label = ttk.Label(header_frame, text="🔍",
                             font=('微软雅黑', 20))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = ttk.Label(header_frame, text="检测解析线路",
                              font=('微软雅黑', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_text = ScrolledText(main_frame, height=20,
                                 font=('微软雅黑', 10),
                                 wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True, pady=10)
        result_text.configure(bg='#F8F9FA')
        
        # 进度条
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame,
                                     variable=progress_var,
                                     maximum=len(self.api_list),
                                     mode='determinate',
                                     length=460)
        progress_bar.pack(fill=tk.X, pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 用于控制检测的标志
        is_checking = threading.Event()
        
        def start_check():
            """开始检测"""
            start_btn.configure(state='disabled')
            stop_btn.configure(state='normal')
            is_checking.set()
            result_text.delete(1.0, tk.END)
            progress_var.set(0)
            threading.Thread(target=update_api_status, daemon=True).start()
        
        def stop_check():
            """停止检测"""
            is_checking.clear()
            start_btn.configure(state='normal')
            stop_btn.configure(state='disabled')
            result_text.insert(tk.END, "\n检测已停止！\n")
            result_text.see(tk.END)
        
        # 创建按钮
        start_btn = ttk.Button(btn_frame, text="开始检测",
                             command=start_check,
                             style='Accent.TButton',
                             width=15)
        start_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = ttk.Button(btn_frame, text="停止检测",
                            command=stop_check,
                            state='disabled',
                            width=15)
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        def check_api(api_name, api_url):
            """检查单个API的可用性"""
            try:
                if not is_checking.is_set():
                    return False, 0
                
                result_text.insert(tk.END, f"\n正在检测 {api_name}")
                result_text.see(tk.END)
                
                test_url = "https://www.iqiyi.com/v_19rr1skq2c.html"
                
                try:
                    parse_url = api_url + test_url
                    if self._check_url_availability(parse_url):
                        result_text.insert(tk.END, " ✓ 可用\n", "success")
                        is_available = True
                    else:
                        result_text.insert(tk.END, " ✗ 不可用\n", "error")
                        is_available = False
                        
                    result_text.see(tk.END)
                    self.api_status[api_name] = is_available
                    return is_available, 1 if is_available else 0
                    
                except Exception:
                    result_text.insert(tk.END, " - 连接超时\n")
                    result_text.see(tk.END)
                    return False, 0
                
            except Exception:
                result_text.insert(tk.END, " - 检测失败\n")
                result_text.see(tk.END)
                return False, 0
        
        # 配置文本标签样式
        result_text.tag_configure("success", foreground="#28a745")
        result_text.tag_configure("error", foreground="#dc3545")
        
        def update_api_status():
            """更新所有API状态"""
            try:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "开始检测解析线路...\n")
                result_text.insert(tk.END, "=" * 40 + "\n")
                
                api_results = []
                available_count = 0
                total_count = len(self.api_list)
                available_apis = {}
                
                for i, (api_name, api_url) in enumerate(self.api_list.items()):
                    if not is_checking.is_set():
                        break
                        
                    try:
                        is_available, success_count = check_api(api_name, api_url)
                        if is_available:
                            api_results.append((api_name, api_url, success_count))
                            available_count += 1
                            available_apis[api_name] = api_url
                    except Exception as e:
                        result_text.insert(tk.END, f"\n{api_name}: ✗ 检测失败 ({str(e)})\n")
                        result_text.insert(tk.END, "-" * 40 + "\n")
                    
                    progress_var.set(i + 1)
                
                if is_checking.is_set():
                    result_text.insert(tk.END, "\n" + "=" * 40 + "\n")
                    result_text.insert(tk.END, "检测完成！\n")
                    result_text.insert(tk.END, f"可用线路: {available_count}/{total_count}\n")
                    
                    if api_results:
                        api_results.sort(key=lambda x: x[2], reverse=True)
                        best_api = api_results[0][0]
                        self.api_list = available_apis
                        self.update_api_radio_buttons()
                        self.api_var.set(best_api)
                        result_text.insert(tk.END, f"\n已自动选择最佳线路: {best_api}\n")
                        result_text.insert(tk.END, "\n可用解析线路:\n")
                        for api_name in available_apis.keys():
                            result_text.insert(tk.END, f"✓ {api_name}\n")
                    else:
                        result_text.insert(tk.END, "\n没有找到可用的解析线路！\n")
                        result_text.insert(tk.END, "请稍后重试或检查网络连接。\n")
                    
                    self.save_config()
                
            finally:
                start_btn.configure(state='normal')
                stop_btn.configure(state='disabled')
                is_checking.clear()
        
        def on_closing():
            stop_check()
            check_window.destroy()
            
        check_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 使窗口居中
        check_window.update_idletasks()
        width = check_window.winfo_width()
        height = check_window.winfo_height()
        x = (check_window.winfo_screenwidth() // 2) - (width // 2)
        y = (check_window.winfo_screenheight() // 2) - (height // 2)
        check_window.geometry(f'{width}x{height}+{x}+{y}')

    def update_api_radio_buttons(self):
        """更新解析线路单选按钮"""
        if not hasattr(self, 'radio_frame'):
            return
            
        # 清除现有的单选按钮
        for widget in self.radio_frame.winfo_children():
            widget.destroy()
            
        # 设置每行显示的按钮数量
        columns_per_row = 5
        
        # 为所有列配置相等的权重
        for i in range(columns_per_row):
            self.radio_frame.grid_columnconfigure(i, weight=1)
        
        # 重新创建单选按钮
        for i, api in enumerate(self.api_list.keys()):
            row = i // columns_per_row
            col = i % columns_per_row
            btn_frame = ttk.Frame(self.radio_frame)
            btn_frame.grid(row=row, column=col, sticky='nsew')
            btn_frame.grid_columnconfigure(0, weight=1)
            
            radio_btn = ttk.Radiobutton(btn_frame, text=api, 
                                      variable=self.api_var,
                                      value=api)
            radio_btn.grid(padx=2, pady=1, sticky='w')
        
        # 刷新显示
        self.radio_frame.update()

    def load_history(self):
        """加载历史记录"""
        try:
            history_file = 'history.json'
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                    # 限制历史记录数量
                    self.history = self.history[:self.max_history]
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            self.history = []
    
    def save_history(self):
        """保存历史记录"""
        try:
            history_file = 'history.json'
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def add_to_history(self, url):
        """添加URL到历史记录"""
        if url not in self.history:
            self.history.insert(0, url)
            if len(self.history) > self.max_history:
                self.history.pop()
            self.save_history()  # 保存历史记录
            
    def clear_history(self):
        """清空历史记录"""
        self.history.clear()
        self.save_history()  # 保存历史记录

    def load_config(self):
        """加载配置"""
        try:
            config_file = 'config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 加载API列表
                    if 'api_list' in config:
                        self.api_list.update(config['api_list'])
                    # 加载默认线路
                    if 'default_api' in config:
                        self.api_var.set(config['default_api'])
                    # 加载其他配置
                    if 'window_size' in config:
                        self.window.geometry(config['window_size'])
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                'api_list': self.api_list,
                'default_api': self.api_var.get(),
                'window_size': self.window.geometry()
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def add_to_cache(self, url, result):
        """添加结果到缓存"""
        self.cache[url] = result
        # 如果缓存超出限制，删除最早的条目
        if len(self.cache) > self.cache_limit:
            oldest_url = next(iter(self.cache))
            del self.cache[oldest_url]
            
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()

    def setup_logging(self):
        """配置日志系统"""
        try:
            # 创建logs目录
            if not os.path.exists('logs'):
                os.makedirs('logs')
            
            # 设置日志文件名
            log_file = f'logs/vip_parser_{datetime.datetime.now().strftime("%Y%m%d")}.log'
            
            # 配置日志格式
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            
            self.logger = logging.getLogger('VIPParser')
            self.logger.info('程序启动')
            
        except Exception as e:
            print(f"配置日志系统失败: {e}")

    def bind_shortcuts(self):
        """绑定快捷键"""
        # Ctrl+V：粘贴
        self.window.bind('<Control-v>', lambda e: self.paste_url())
        # Ctrl+Return：开始解析
        self.window.bind('<Control-Return>', lambda e: self.parse_video())
        # Ctrl+H：显示历史记录
        self.window.bind('<Control-h>', lambda e: self.show_history())
        # Ctrl+L：清空输入框
        self.window.bind('<Control-l>', lambda e: self.clear_url())
        # F5：检测解析线路
        self.window.bind('<F5>', lambda e: self.check_api_availability())
        # F1：显示帮助
        self.window.bind('<F1>', lambda e: self.show_help())

    def manage_api_list(self):
        """管理解析线路"""
        manage_window = tk.Toplevel(self.window)
        manage_window.title("管理解析线路")
        manage_window.geometry("600x400")
        manage_window.transient(self.window)
        manage_window.grab_set()
        
        # 创建框架
        frame = ttk.Frame(manage_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建列表框
        list_frame = ttk.LabelFrame(frame, text="当前解析线路", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        columns = ('名称', 'URL')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 设置列标题
        tree.heading('名称', text='名称')
        tree.heading('URL', text='URL')
        
        # 设置列宽
        tree.column('名称', width=150)
        tree.column('URL', width=350)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加现有线路
        for name, url in self.api_list.items():
            tree.insert('', tk.END, values=(name, url))
        
        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        def add_api():
            """添加新线路"""
            add_window = tk.Toplevel(manage_window)
            add_window.title("添加解析线路")
            add_window.geometry("400x150")
            add_window.transient(manage_window)
            add_window.grab_set()
            
            # 创建输入框
            input_frame = ttk.Frame(add_window, padding=10)
            input_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(input_frame, text="名称:").grid(row=0, column=0, padx=5, pady=5)
            name_var = tk.StringVar()
            name_entry = ttk.Entry(input_frame, textvariable=name_var)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
            
            ttk.Label(input_frame, text="URL:").grid(row=1, column=0, padx=5, pady=5)
            url_var = tk.StringVar()
            url_entry = ttk.Entry(input_frame, textvariable=url_var)
            url_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
            
            def save_api():
                name = name_var.get().strip()
                url = url_var.get().strip()
                
                if not name or not url:
                    messagebox.showwarning("警告", "请填写完整信息")
                    return
                    
                if not url.startswith(('http://', 'https://')):
                    messagebox.showwarning("警告", "URL必须以http://或https://开头")
                    return
                    
                tree.insert('', tk.END, values=(name, url))
                add_window.destroy()
            
            # 按钮
            btn_frame = ttk.Frame(input_frame)
            btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
            
            ttk.Button(btn_frame, text="保存", command=save_api).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="取消", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
            
        def remove_api():
            """删除选中的线路"""
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("警告", "请先选择要删除的线路")
                return
                
            if messagebox.askyesno("确认", "确定要删除选中的解析线路吗？"):
                for item in selected:
                    tree.delete(item)
                    
        def save_changes():
            """保存更改"""
            new_api_list = {}
            for item in tree.get_children():
                name, url = tree.item(item)['values']
                new_api_list[name] = url
                
            if not new_api_list:
                messagebox.showwarning("警告", "至少需要保留一条解析线路")
                return
                
            self.api_list = new_api_list
            self.update_api_radio_buttons()
            self.save_config()
            manage_window.destroy()
            messagebox.showinfo("提示", "解析线路已更新")
        
        # 添加按钮
        ttk.Button(btn_frame, text="添加线路", command=add_api).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=remove_api).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存更改", command=save_changes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=manage_window.destroy).pack(side=tk.RIGHT, padx=5)

    def __del__(self):
        """析构函数：清理资源"""
        try:
            # 关闭线程池
            self.thread_pool.shutdown(wait=False)
            # 关闭会话
            self.session.close()
        except:
            pass

    def setup_styles(self):
        """设置自定义样式"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 定义颜色方案
        primary_color = '#2196F3'  # 主色调
        secondary_color = '#1976D2'  # 次要色调
        hover_color = '#42A5F5'  # 悬停色
        focus_color = '#E3F2FD'  # 焦点色
        bg_color = '#F5F5F5'  # 背景色
        text_color = '#212121'  # 文本色
        accent_color = '#FF4081'  # 强调色
        success_color = '#4CAF50'  # 成功色
        warning_color = '#FFC107'  # 警告色
        error_color = '#F44336'  # 错误色
        
        # 配置全局样式
        self.window.configure(bg=bg_color)
        
        # 标签样式
        self.style.configure('TLabel',
                           background=bg_color,
                           foreground=text_color,
                           font=('微软雅黑', 10))
        
        # 标题样式
        self.style.configure('Title.TLabel',
                           font=('微软雅黑', 24, 'bold'),
                           foreground=secondary_color,
                           background=bg_color,
                           padding=20)
        
        # 按钮样式和悬停效果
        self.style.configure('TButton',
                           font=('微软雅黑', 10),
                           background=primary_color,
                           foreground='white',
                           padding=(10, 5))
        
        self.style.map('TButton',
                      background=[('active', hover_color),
                                ('pressed', secondary_color)],
                      foreground=[('active', 'white'),
                                ('pressed', 'white')],
                      relief=[('pressed', 'sunken')])
        
        # 主要按钮样式
        self.style.configure('Primary.TButton',
                           font=('微软雅黑', 12, 'bold'),
                           background=primary_color,
                           foreground='white',
                           padding=(20, 10))
                           
        self.style.map('Primary.TButton',
                      background=[('active', hover_color),
                                ('pressed', secondary_color)],
                      foreground=[('active', 'white'),
                                ('pressed', 'white')],
                      relief=[('pressed', 'sunken')])
        
        # 快速按钮样式
        self.style.configure('Quick.TButton',
                           font=('微软雅黑', 10),
                           background=secondary_color,
                           foreground='white',
                           padding=(8, 4))
                           
        self.style.map('Quick.TButton',
                      background=[('active', hover_color),
                                ('pressed', secondary_color)],
                      foreground=[('active', 'white'),
                                ('pressed', 'white')],
                      relief=[('pressed', 'sunken')])
        
        # 输入框样式和焦点效果
        self.style.configure('TEntry',
                           fieldbackground='white',
                           padding=8,
                           relief='solid',
                           borderwidth=1)
                           
        self.style.map('TEntry',
                      fieldbackground=[('focus', focus_color)],
                      bordercolor=[('focus', primary_color)],
                      lightcolor=[('focus', primary_color)],
                      darkcolor=[('focus', primary_color)],
                      borderwidth=[('focus', 2)])
        
        # 框架样式
        self.style.configure('TFrame',
                           background=bg_color)
        
        # 标签框样式
        self.style.configure('TLabelframe',
                           background=bg_color)
        self.style.configure('TLabelframe.Label',
                           background=bg_color,
                           font=('微软雅黑', 11, 'bold'),
                           foreground=text_color)
        
        # 单选按钮样式和悬停效果
        self.style.configure('TRadiobutton',
                           background=bg_color,
                           font=('微软雅黑', 10),
                           foreground=text_color)
                           
        self.style.map('TRadiobutton',
                      background=[('active', focus_color)],
                      foreground=[('active', secondary_color)])
        
        # 进度条样式
        self.style.configure('Horizontal.TProgressbar',
                           background=primary_color,
                           troughcolor=bg_color,
                           bordercolor=secondary_color,
                           lightcolor=primary_color,
                           darkcolor=primary_color)
        
        # 状态栏样式
        self.style.configure('Status.TLabel',
                           font=('微软雅黑', 9),
                           background='#E0E0E0',
                           foreground=text_color,
                           padding=(10, 5))
                           
        # 状态栏特殊状态样式
        self.style.configure('Status.Success.TLabel',
                           foreground=success_color)
        self.style.configure('Status.Warning.TLabel',
                           foreground=warning_color)
        self.style.configure('Status.Error.TLabel',
                           foreground=error_color)
        
        # 滚动文本框样式
        self.style.configure('Custom.TScrolledText',
                           background='white',
                           foreground=text_color,
                           font=('微软雅黑', 10))

    def start_cache_cleanup(self):
        """启动定期清理缓存的定时器"""
        def cleanup():
            while True:
                try:
                    self.clean_expired_cache()
                    time.sleep(300)  # 每5分钟清理一次
                except Exception as e:
                    self.logger.error(f"缓存清理失败: {e}")
                    
        # 启动清理线程
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
        
    def clean_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, (value, timestamp) in self.cache.items():
            if current_time - timestamp > self.cache_expire_time:
                expired_keys.append(key)
                
        # 删除过期缓存
        for key in expired_keys:
            del self.cache[key]
            
        self.logger.info(f"清理了 {len(expired_keys)} 条过期缓存")
        
    def start_network_monitor(self):
        """启动网络状态监控"""
        def monitor():
            while True:
                try:
                    self.check_network_status()
                    time.sleep(60)  # 每分钟检查一次
                except Exception as e:
                    self.logger.error(f"网络状态检查失败: {e}")
                    
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def check_network_status(self):
        """检查网络状态"""
        try:
            # 测试与常用网站的连接
            test_urls = [
                'https://www.baidu.com',
                'https://www.qq.com',
                'https://www.iqiyi.com'
            ]
            
            for url in test_urls:
                response = self.session.head(
                    url,
                    timeout=3,
                    verify=False
                )
                if response.status_code == 200:
                    self.network_status = {
                        'status': True,
                        'last_check': time.time()
                    }
                    self.update_status_bar()
                    return True
                    
            raise Exception("所有测试站点均无法访问")
            
        except Exception as e:
            self.network_status = {
                'status': False,
                'last_check': time.time(),
                'error': str(e)
            }
            self.update_status_bar()
            return False
            
    def update_status_bar(self):
        """更新状态栏显示"""
        # 网络状态
        if self.network_status['status']:
            network_text = "网络正常 ✓"
            network_style = 'Status.Success.TLabel'
        else:
            network_text = "网络异常 ✗"
            network_style = 'Status.Error.TLabel'
            
        # 缓存状态
        cache_count = len(self.cache)
        cache_percent = (cache_count / self.cache_limit) * 100
        if cache_percent < 50:
            cache_style = 'Status.Success.TLabel'
        elif cache_percent < 80:
            cache_style = 'Status.Warning.TLabel'
        else:
            cache_style = 'Status.Error.TLabel'
        cache_text = f"缓存: {cache_count}/{self.cache_limit}"
        
        # API性能
        if self.api_performance:
            best_api = max(self.api_performance.items(),
                         key=lambda x: x[1]['success_rate'])
            api_text = f"最佳线路: {best_api[0]} ({best_api[1]['success_rate']:.1f}%)"
        else:
            api_text = "暂无线路统计"
            
        # 更新状态栏标签
        status_text = f"{network_text} | {cache_text} | {api_text}"
        self.status_var.set(status_text)
        
        # 根据状态设置样式
        if not self.network_status['status']:
            self.status_bar.configure(style='Status.Error.TLabel')
        elif cache_percent >= 80:
            self.status_bar.configure(style='Status.Warning.TLabel')
        else:
            self.status_bar.configure(style='Status.TLabel')
        
    def update_api_performance(self, api_name, response_time, success=True):
        """更新API性能统计"""
        if api_name not in self.api_performance:
            self.api_performance[api_name] = {
                'total_time': 0,
                'count': 0,
                'avg_time': 0,
                'success_rate': 0,
                'success_count': 0,
                'fail_count': 0,
                'last_test': 0,
                'speed_test': []  # 存储最近的速度测试结果
            }
            
        stats = self.api_performance[api_name]
        stats['total_time'] += response_time
        stats['count'] += 1
        stats['avg_time'] = stats['total_time'] / stats['count']
        
        if success:
            stats['success_count'] += 1
        else:
            stats['fail_count'] += 1
            
        stats['success_rate'] = (stats['success_count'] / 
            (stats['success_count'] + stats['fail_count'])) * 100
            
        # 更新速度测试结果
        stats['speed_test'].append(response_time)
        if len(stats['speed_test']) > 5:  # 只保留最近5次测试结果
            stats['speed_test'].pop(0)
            
        stats['last_test'] = time.time()
        
    def test_api_speed(self, api_name, api_url):
        """测试单个API的速度"""
        try:
            test_url = "https://www.iqiyi.com/v_19rr1skq2c.html"
            parse_url = api_url + test_url
            
            start_time = time.time()
            response = self.session.head(
                parse_url,
                timeout=self.request_timeout,
                allow_redirects=True,
                verify=False
            )
            response_time = time.time() - start_time
            
            success = response.status_code == 200
            self.update_api_performance(api_name, response_time, success)
            
            return success, response_time
            
        except Exception as e:
            self.update_api_performance(api_name, self.request_timeout, False)
            return False, self.request_timeout
            
    def auto_test_api_speed(self):
        """自动测试所有API速度"""
        speed_test_window = tk.Toplevel(self.window)
        speed_test_window.title("解析线路测速")
        speed_test_window.geometry("800x600")  # 增加窗口大小
        speed_test_window.transient(self.window)
        speed_test_window.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(speed_test_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        ttk.Label(main_frame, text="解析线路测速",
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # 进度条
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame,
                                     variable=progress_var,
                                     maximum=len(self.api_list),
                                     length=700,  # 增加进度条长度
                                     mode='determinate')
        progress_bar.pack(pady=10)
        
        # 结果显示框架
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 结果显示
        result_text = ScrolledText(result_frame, height=20, width=80)  # 增加文本框大小
        result_text.pack(fill=tk.BOTH, expand=True)
        
        def update_status(text):
            result_text.insert(tk.END, text + "\n")
            result_text.see(tk.END)
            speed_test_window.update()
        
        def run_speed_test():
            try:
                update_status("开始测速...")
                results = []
                
                for i, (api_name, api_url) in enumerate(self.api_list.items()):
                    update_status(f"\n测试 {api_name}...")
                    success, response_time = self.test_api_speed(api_name, api_url)
                    
                    status = "✓ 可用" if success else "✗ 不可用"
                    speed = f"{response_time:.2f}秒"
                    update_status(f"状态: {status}")
                    update_status(f"响应时间: {speed}")
                    
                    if success:
                        results.append((api_name, response_time))
                    
                    progress_var.set(i + 1)
                
                # 根据速度排序
                if results:
                    results.sort(key=lambda x: x[1])
                    update_status("\n\n测速结果排名:")
                    for i, (api_name, response_time) in enumerate(results, 1):
                        update_status(f"{i}. {api_name} - {response_time:.2f}秒")
                    
                    # 自动选择最快的线路
                    best_api = results[0][0]
                    self.api_var.set(best_api)
                    update_status(f"\n已自动选择最快线路: {best_api}")
                    
                    # 优化API顺序
                    self.optimize_api_order()
                
                update_status("\n测速完成！")
                
            except Exception as e:
                update_status(f"\n测速过程出错: {str(e)}")
            
            finally:
                test_btn.configure(state='normal')
        
        # 底部按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 左侧按钮
        left_btn_frame = ttk.Frame(btn_frame)
        left_btn_frame.pack(side=tk.LEFT)
        
        def start_test():
            test_btn.configure(state='disabled')
            progress_var.set(0)
            result_text.delete(1.0, tk.END)
            threading.Thread(target=run_speed_test, daemon=True).start()
        
        # 统一按钮样式
        button_style = {
            'width': 20,  # 统一按钮宽度
            'style': 'Primary.TButton'  # 统一使用主要按钮样式
        }
        
        test_btn = ttk.Button(left_btn_frame, 
                          text="开始测速",
                          command=start_test,
                          **button_style)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 右侧按钮
        right_btn_frame = ttk.Frame(btn_frame)
        right_btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_btn_frame,
                text="关闭",
                command=speed_test_window.destroy,
                **button_style).pack(side=tk.RIGHT)
        
        # 使窗口居中
        speed_test_window.update_idletasks()
        width = speed_test_window.winfo_width()
        height = speed_test_window.winfo_height()
        x = (speed_test_window.winfo_screenwidth() // 2) - (width // 2)
        y = (speed_test_window.winfo_screenheight() // 2) - (height // 2)
        speed_test_window.geometry(f'{width}x{height}+{x}+{y}')

    def optimize_api_order(self):
        """优化API顺序"""
        if not self.api_performance:
            return
            
        # 根据性能统计重新排序API列表
        sorted_apis = sorted(
            self.api_list.items(),
            key=lambda x: (
                self.api_performance.get(x[0], {}).get('success_rate', 0),
                -self.api_performance.get(x[0], {}).get('avg_time', float('inf')),
                -len(self.api_performance.get(x[0], {}).get('speed_test', [])),
                -self.api_performance.get(x[0], {}).get('last_test', 0)
            ),
            reverse=True
        )
        
        # 更新API列表
        self.api_list = dict(sorted_apis)
        # 更新界面
        self.update_api_radio_buttons()

    def get_best_api(self):
        """获取性能最好的API"""
        if not self.api_performance:
            return None
            
        # 根据平均响应时间和成功率排序
        sorted_apis = sorted(
            self.api_performance.items(),
            key=lambda x: (x[1]['success_rate'], -x[1]['avg_time']),
            reverse=True
        )
        
        return sorted_apis[0][0] if sorted_apis else None


if __name__ == '__main__':
    app = VIPVideoParser()
    app.run()
