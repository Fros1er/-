from tkinter import ttk
from easygui import fileopenbox, msgbox
import tkinter as tk
import os
import sys


class gui:
    paths = {"csvpath": "", "txtpath": ""}

    def __init__(self, startfunc):
        self.window = tk.Tk()
        self.window.title("打开")
        self.bottom = tk.Frame(self.window)
        self.bottom.grid(column=0, row=0)
        textframe = ttk.LabelFrame(self.bottom, text="打开文件")
        textframe.grid(column=0, row=0, padx=10, pady=10)
        self.partcsv(textframe)
        self.parttxt(textframe)
        self.partbuttons()
        self.startfunc = startfunc

    def openfile(self, text, target):
        """
        通过fileopenbox获取路径
        """
        path = fileopenbox()
        text.set(path)
        self.paths[target] = path

    def partcsv(self, frame):
        """
        添加CSV打开部分
        """
        ttk.Label(frame, text="CSV: ").grid(column=0, row=0)
        csvtext = tk.StringVar()
        ttk.Entry(frame, width=50, textvariable=csvtext, state="readonly").grid(
            column=1, row=0, sticky=tk.W
        )
        ttk.Button(
            frame, text="打开", command=lambda: self.openfile(csvtext, "csvpath")
        ).grid(column=2, row=0)

    def parttxt(self, frame):
        """
        添加TXT打开部分
        """
        ttk.Label(frame, text="TXT: ").grid(column=0, row=1)
        txttext = tk.StringVar()
        ttk.Entry(frame, width=50, textvariable=txttext, state="readonly").grid(
            column=1, row=1, sticky=tk.W
        )
        ttk.Button(
            frame, text="打开", command=lambda: self.openfile(txttext, "txtpath")
        ).grid(column=2, row=1)

    def start(self):
        """
        绑定到开始按钮
        程序入口
        """
        paths = self.paths
        self.initprogressmonitor()
        self.startfunc(paths["csvpath"], paths["txtpath"], self)
        self.end()

    def editconfig(self):
        """
        修改配置文件
        """
        os.startfile("config.json")

    def partbuttons(self):
        """
        添加开始、配置按钮
        """
        buttons = tk.Frame(self.bottom)
        buttons.grid(column=0, row=1, padx=10)
        ttk.Button(buttons, text="开始", command=self.start).grid(
            column=0, row=2, sticky=tk.W, padx=5, pady=5
        )
        ttk.Button(buttons, text="配置", command=self.editconfig).grid(
            column=1, row=2, sticky=tk.W, padx=5, pady=5
        )

    def end(self):
        """
        更改按钮文字
        """
        self.endbuttontext.set("确定")

    def initprogressmonitor(self):
        """
        重设窗口
        """
        self.window.title("运行中")
        self.bottom.destroy()
        self.bottom = tk.Frame(self.window)
        self.bottom.grid(column=0, row=0)

        """
        添加进度文字显示
        """
        frame = ttk.LabelFrame(self.bottom, text="当前进度")
        frame.grid(column=0, row=0, padx=10, pady=10)
        self.inf = tk.StringVar()
        ttk.Label(frame, width=50, textvariable=self.inf, state="readonly").grid(
            column=0, row=0, sticky=tk.W
        )

        """
        添加取消/确定按钮
        """
        self.endbuttontext = tk.StringVar(value="取消")
        endbutton = tk.Frame(self.bottom)
        endbutton.grid(column=0, row=1, padx=10, pady=10)
        ttk.Button(endbutton, textvariable=self.endbuttontext, command=lambda: sys.exit(0)).grid(
            column=0, row=2, sticky=tk.W, padx=5, pady=3
        )

    def changeinf(self, text):
        """
        更改进度文字
        """
        self.inf.set(text)
