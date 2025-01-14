import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from tkinter.scrolledtext import ScrolledText
import pyperclip
from auto_updater import AutoUpdater  # 导入自动更新器


class VIPVideoParser:
    def __init__(self):
        """初始化上传工具"""
        self.window = tk.Tk()
        self.window.title('VIP视频解析工具')  # 添加版本号
        self.window.geometry('1000x800')
        self.window.resizable(True, True)
        
        # 创建菜单栏
        self.create_menu()
        
        # 初始化状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        self.status_bar = ttk.Label(self.window, textvariable=self.status_var,
                                  relief=tk.SUNKEN, padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 检查更新
        self.window.after(1000, self.check_update)  # 延迟1秒检查更新
        
        # 设置主题样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 设置全局字体和颜色
        bg_color = '#f0f0f0'  # 背景色
        accent_color = '#2196F3'  # 主题色
        self.window.configure(bg=bg_color)
        
        # 配置样式
        self.style.configure('TLabel',
                           background=bg_color,
                           font=('微软雅黑', 10))
        
        self.style.configure('Title.TLabel',
                           font=('微软雅黑', 24, 'bold'),
                           foreground='#1976D2',
                           background=bg_color,
                           padding=20)
        
        self.style.configure('TButton',
                           font=('微软雅黑', 10),
                           padding=8)
        
        self.style.configure('Primary.TButton',
                           font=('微软雅黑', 12, 'bold'),
                           padding=15)
        
        self.style.configure('Quick.TButton',
                           font=('微软雅黑', 10),
                           padding=5)
        
        self.style.configure('TEntry',
                           padding=8)
        
        self.style.configure('TFrame',
                           background=bg_color)
        
        self.style.configure('TLabelframe',
                           background=bg_color)
        
        self.style.configure('TLabelframe.Label',
                           background=bg_color,
                           font=('微软雅黑', 11, 'bold'),
                           foreground='#424242')
        
        self.style.configure('TRadiobutton',
                           background=bg_color,
                           font=('微软雅黑', 10))
        
        # 设置窗口图标
        try:
            self.window.iconbitmap('icon.ico')
        except:
            pass
            
        # 设置窗口最小尺寸
        self.window.minsize(700, 500)  # 减小最小尺寸
        
        # 解析接口列表
        self.api_list = {
            '线路1 - 通用': 'https://jx.m3u8.tv/jiexi/?url=',
            '线路2 - 稳定': 'https://jx.parwix.com:4433/player/?url=',
            '线路3 - 高速': 'https://jx.xmflv.com/?url=',
            '线路4 - 备用': 'https://www.yemu.xyz/?url=',
            '线路5 - 超清': 'https://api.jiexi.la/?url=',
            '线路6 - 急速': 'https://www.8090g.cn/?url='
        }
        
        # 初始化变量
        self.api_var = tk.StringVar(value='线路1 - 通用')
        
        # 添加历史记录列表
        self.history = []
        self.max_history = 10  # 最多保存10条历史记录
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding=10)  # 减小内边距
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="VIP视频解析工具", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))  # 减小标题下方间距
        
        # 创建URL输入框组
        url_frame = ttk.LabelFrame(main_frame, text="视频链接", padding=10)  # 减小内边距
        url_frame.pack(fill=tk.X, padx=5, pady=(0, 10))  # 减小外边距
        
        # URL输入框
        self.url_entry = ttk.Entry(url_frame, font=('微软雅黑', 11))
        self.url_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 绑定回车键
        self.url_entry.bind('<Return>', lambda e: self.parse_video())
        
        # 按钮组
        btn_group = ttk.Frame(url_frame)
        btn_group.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(btn_group, text="粘贴", 
                  command=self.paste_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_group, text="清空",
                  command=self.clear_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_group, text="历史",
                  command=self.show_history).pack(side=tk.LEFT, padx=2)
        
        # 创建解析线路选择框
        line_frame = ttk.LabelFrame(main_frame, text="解析线路", padding=10)
        line_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # 解析线路布局优化 - 改为两行三列
        radio_frame = ttk.Frame(line_frame)
        radio_frame.pack(fill=tk.X)
        
        for i, api in enumerate(self.api_list.keys()):
            row = i // 3
            col = i % 3
            ttk.Radiobutton(radio_frame, text=api, variable=self.api_var,
                          value=api).grid(row=row, column=col, padx=15, pady=2, sticky='w')
        
        # 操作按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=5)  # 减小按钮区域的间距
        
        ttk.Button(btn_frame, text="开始解析", style='Primary.TButton',
                  command=self.parse_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="使用帮助", style='Primary.TButton',
                  command=self.show_help).pack(side=tk.LEFT, padx=5)
        
        # 快速访问区域
        quick_frame = ttk.LabelFrame(main_frame, text="快速访问", padding=10)
        quick_frame.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # 创建两行按钮，每行4个，减小按钮内边距
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
        
        for i, (name, url) in enumerate(sites):
            row = i // 4
            col = i % 4
            btn = ttk.Button(quick_frame, text=name, style='Quick.TButton',
                           command=lambda u=url: webbrowser.open(u))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # 设置网格列的权重，使按钮均匀分布
        for i in range(4):
            quick_frame.grid_columnconfigure(i, weight=1)
        
        # 支持的网站列表
        site_frame = ttk.LabelFrame(main_frame, text="支持的视频网站", padding=10)
        site_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # 减小文本框的高度
        self.sites_text = ScrolledText(site_frame, wrap=tk.WORD,
                                     font=('微软雅黑', 10),
                                     height=6,  # 减小高度
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
        
        # 添加状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self.window, textvariable=self.status_var,
                             relief=tk.SUNKEN, background='#E0E0E0',
                             font=('微软雅黑', 9), padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

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
        help_text = """使用帮助：

1. 视频解析步骤：
   - 复制视频页面链接
   - 粘贴到输入框
   - 选择解析线路
   - 点击开始解析

2. 常见问题：
   - 如果解析失败，请尝试其他线路
   - 确保输入的是完整的视频页面链接
   - 部分视频可能需要多次尝试

3. 注意事项：
   - 仅供学习交流使用
   - 请勿用于商业用途
   - 建议支持正版
"""
        messagebox.showinfo("使用帮助", help_text)

    def parse_video(self):
        """解析视频"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning('警告', '请输入视频链接！')
            return
            
        # 检查URL格式
        if not (url.startswith('http://') or url.startswith('https://')):
            messagebox.showwarning('警告', '请输入正确的视频链接！\n链接应以 http:// 或 https:// 开头')
            return
            
        # 检查是否是支持的网站
        supported_sites = ['iqiyi.com', 'v.qq.com', 'youku.com', 'mgtv.com', 
                         'bilibili.com', 'tv.sohu.com', 'pptv.com', '1905.com']
        if not any(site in url.lower() for site in supported_sites):
            result = messagebox.askyesno('提示', 
                '当前链接可能不是支持的视频网站！\n是否继续解析？')
            if not result:
                return
        
        try:
            # 添加到历史记录
            if url not in self.history:
                self.history.insert(0, url)
                if len(self.history) > self.max_history:
                    self.history.pop()
            
            selected_api = self.api_list[self.api_var.get()]
            parse_url = selected_api + url
            
            # 更新状态
            self.status_var.set(f"正在使用 {self.api_var.get()} 解析视频...")
            self.window.update()
            
            # 打开浏览器
            webbrowser.open(parse_url)
            
            # 延迟更新状态
            self.window.after(2000, lambda: self.status_var.set("解析完成，请查看浏览器窗口"))
            
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("错误", f"解析失败：{error_msg}\n请尝试其他线路或检查网络连接")
            self.status_var.set("解析失败")

    def check_update(self):
        """检查更新"""
        try:
            # 更新状态栏
            self.status_var.set("正在检查更新...")
            self.window.update()
            
            updater = AutoUpdater()
            # 获取当前版本
            current_version = updater.get_current_version()
            self.window.title(f'VIP视频解析工具 v{current_version}')  # 在标题栏显示版本号
            
            # 检查更新
            has_update = updater.check_update()
            
            if not has_update:
                self.status_var.set(f"当前已是最新版本 v{current_version}")
                self.window.update()
                
        except Exception as e:
            error_msg = f"检查更新失败: {str(e)}"
            print(error_msg)
            self.status_var.set("检查更新失败")
            self.window.update()
            messagebox.showerror("更新检查失败", f"无法检查更新：{str(e)}\n请检查网络连接后重试。")

    def show_history(self):
        """显示历史记录"""
        if not self.history:
            messagebox.showinfo("历史记录", "暂无历史记录")
            return
            
        history_window = tk.Toplevel(self.window)
        history_window.title("历史记录")
        history_window.geometry("600x400")
        
        # 创建列表框
        listbox = tk.Listbox(history_window, font=('微软雅黑', 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 添加历史记录
        for url in self.history:
            listbox.insert(tk.END, url)
            
        # 添加双击事件
        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                url = self.history[selection[0]]
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, url)
                history_window.destroy()
                
        listbox.bind('<Double-Button-1>', on_double_click)
        
        # 添加按钮
        btn_frame = ttk.Frame(history_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="使用选中链接", 
                  command=lambda: on_double_click(None)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空历史", 
                  command=lambda: [self.history.clear(), history_window.destroy()]).pack(side=tk.LEFT, padx=5)

    def run(self):
        """运行程序"""
        try:
            self.window.iconbitmap('icon.ico')
        except:
            pass
        self.window.mainloop()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="检查更新", command=self.check_update)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.window.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用帮助", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """VIP视频解析工具 v1.0.0

作者：你的名字
邮箱：18558995273@163.com

Copyright © 2024 保留所有权利。
"""
        messagebox.showinfo("关于", about_text)


if __name__ == '__main__':
    app = VIPVideoParser()
    app.run()
