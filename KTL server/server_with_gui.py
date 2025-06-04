# 文件名：server_with_gui.py

import sys
import threading
import signal
import Ice
import tkinter as tk
from tkinter import ttk

# ------------------------------------------------------------
# 1. 加载 Slice 及生成的 CombIce 模块
# ------------------------------------------------------------
Ice.loadSlice('KtlIce.ice')
import CombIce

# 假设 parse_xml 与 KeckLFC 在上一级目录中
sys.path.append('../')
from KeckLFC import KeckLFC
from parse_xml import parse_xml  # 用于解析已去除 <serverside> 的 LFC_withgui.xml.sin

# ------------------------------------------------------------
# 2. 定义 ICE Server 的接口实现 LfcI
# ------------------------------------------------------------
class LfcI(CombIce.Lfc):
    def __init__(self):
        # 解析 “已去除 <serverside>” 的 LFC_withgui.xml.sin，获取关键词列表
        self.keyword_names, _ = parse_xml('LFC_withgui.xml.sin')
        # 实际硬件或模拟驱动
        self.mkl = KeckLFC()
        print('LfcI 已初始化，共 %d 个关键词。' % len(self.keyword_names))

    def modifiedkeyword(self, name, value, current):
        """
        Dispatcher 向某个关键词写入时触发
        例如： modifiedkeyword("LFC_RFAMP_ONOFF", "1", current)
        """
        try:
            self.mkl[name] = value
            print(f'[ICE] 修改 {name} = {value}')
        except Exception as e:
            print(f'[ICE] modifiedkeyword 设置 {name} 时出错：{e}')

    def receive(self, name, current):
        """
        Dispatcher 读取某个关键词时触发，只返回字符串
        注意：由于 XML 里已无 <serverside>，Dispatcher 只会在手动触发或脚本调取时调用这里
        """
        try:
            val = self.mkl[name]
            return str(val)
        except Exception as e:
            print(f'[ICE] receive 读取 {name} 时出错：{e}')
            return ""

    def keylist(self, current):
        """Dispatcher 启动时调用，返回关键词列表"""
        return self.keyword_names

    def cleanup(self, current):
        """Dispatcher 请求 cleanup 时回调"""
        print('[ICE] Dispatcher 请求 cleanup')

    def shutdown(self, current):
        """Dispatcher 发起 shutdown 时调用"""
        print('[ICE] Dispatcher 请求关闭 Server')
        current.adapter.getCommunicator().shutdown()

# ------------------------------------------------------------
# 3. 后台线程：启动 ICE Server，不阻塞主线程
# ------------------------------------------------------------
def start_ice_server():
    communicator = Ice.initialize(sys.argv, 'config.server')
    signal.signal(signal.SIGINT, lambda s, f: communicator.shutdown())

    adapter = communicator.createObjectAdapter("Lfc")
    lfc_impl = LfcI()
    adapter.add(lfc_impl, Ice.stringToIdentity("lfc"))
    adapter.activate()
    print('ICE Server 已启动，正在等待 Dispatcher 连接…')

    # 把 waitForShutdown 放到后台线程里
    def wait_loop():
        communicator.waitForShutdown()
        print('ICE Communicator 已关闭，后台线程结束。')

    threading.Thread(target=wait_loop, daemon=True).start()
    return lfc_impl

# ------------------------------------------------------------
# 4. GUI 部分：由 GUI 负责周期性读取 self.lfc.mkl[...]，Dispatcher 不再周期拉取
# ------------------------------------------------------------
class LfcMonitorGUI:
    def __init__(self, root, lfc_service: LfcI):
        self.root = root
        self.lfc = lfc_service
        root.title("LFC 状态监控与控制")
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        frame = ttk.Frame(root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # ———— 左侧：控制按钮 ————
        btn_frame = ttk.LabelFrame(frame, text="设备控制", padding=8)
        btn_frame.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        # 示例按钮：RF Amp 开/关
        ttk.Button(btn_frame, text="RF Amp 开机",
                   command=lambda: self.set_kw("LFC_RFAMP_ONOFF", "1")
                  ).grid(row=0, column=0, pady=(0,5), sticky="ew")
        ttk.Button(btn_frame, text="RF Amp 关机",
                   command=lambda: self.set_kw("LFC_RFAMP_ONOFF", "0")
                  ).grid(row=1, column=0, pady=(0,5), sticky="ew")

        # 示例按钮：VOA1550 衰减 10dB
        ttk.Button(btn_frame, text="VOA1550 衰减 10dB",
                   command=lambda: self.set_kw("LFC_VOA1550_ATTEN", "10.00")
                  ).grid(row=2, column=0, pady=(0,5), sticky="ew")

        # 如果需要更多按钮，可按此方式继续添加
        # ttk.Button(btn_frame, text="…", command=lambda: self.set_kw("关键词", "值")).grid(...)
        # …

        # ———— 右侧：状态监测指示灯 ————
        status_frame = ttk.LabelFrame(frame, text="状态监测", padding=8)
        status_frame.grid(row=0, column=1, sticky="nsew")
        status_frame.columnconfigure(1, weight=1)

        # 把想要 GUI 轮询的关键词放在这里：
        self.status_items = [
            ("LFC_TEMP_MONITOR", "温度监测"),
            ("LFC_RFOSCI_MONITOR", "RF Oscillator"),
            # … 如果有更多，也可以继续添加
        ]
        self.indicator_ids = {}
        for idx, (kw, label_text) in enumerate(self.status_items):
            ttk.Label(status_frame, text=label_text + "：").grid(row=idx, column=0, sticky="w", pady=5)
            c = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
            oval = c.create_oval(2, 2, 18, 18, fill="gray")
            c.grid(row=idx, column=1, sticky="w", padx=5)
            self.indicator_ids[kw] = (c, oval)

        # 启动 GUI 轮询，interval 单位为毫秒
        self.poll_interval = 2000
        self.root.after(self.poll_interval, self.update_indicators)

    def set_kw(self, name: str, value: str):
        """ 点击按钮时，把 value 写给底层 KeckLFC """
        try:
            self.lfc.mkl[name] = value
            print(f"[GUI] 已设置 {name} = {value}")
        except Exception as e:
            print(f"[GUI] 设置 {name} 时出错：{e}")

    def update_indicators(self):
        """ GUI 周期性回调：直接读取 self.lfc.mkl[kw] 并更新指示灯 """
        for kw, _ in self.status_items:
            canvas, oval_id = self.indicator_ids[kw]
            try:
                raw = self.lfc.mkl[kw]    # 直接从底层硬件/模拟读取
                val = int(raw)            # 假设所有监测关键词都能转为 int
            except:
                val = None

            # 根据 val 设定颜色（可按实际需求修改判断逻辑）
            if kw == "LFC_TEMP_MONITOR":
                color = "green" if val == 1 else "red"
            elif kw == "LFC_RFOSCI_MONITOR":
                color = "green" if val == 0 else "red"
            else:
                color = "gray"

            canvas.itemconfig(oval_id, fill=color)

        # 2 秒后再调一次自己
        self.root.after(self.poll_interval, self.update_indicators)

    def on_close(self):
        """ GUI 窗口关闭回调 """
        # 如果需要同时关闭 ICE Server，可在此处调用 shutdown
        try:
            self.lfc._adapter.getCommunicator().shutdown()
        except:
            pass
        self.root.destroy()

# ------------------------------------------------------------
# 5. 主程序：先启动 ICE Server，再启动 GUI
# ------------------------------------------------------------
if __name__ == "__main__":
    # （1）后台启动 ICE Server
    lfc_impl = start_ice_server()

    # （2）前台启动 Tkinter GUI
    root = tk.Tk()
    gui = LfcMonitorGUI(root, lfc_impl)
    root.mainloop()

    # GUI 关闭后，再次确保 ICE Server 退出
    try:
        lfc_impl._adapter.getCommunicator().shutdown()
    except:
        pass
