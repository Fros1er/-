# -*- coding: utf-8 -*-

from re import findall, search
from tkinter import ttk
from easygui import fileopenbox, msgbox
import tkinter as tk
import os
import csv
import json
import sys

#路径
csvpath = "" 
txtpath = ""

cargos = {}  # 此处是cargo类与箱号的查询字典，直接用箱号查。包含一个数组，[0]为cargo类，[1]为毛重。
containers = []  # csv的每一行。
identities = {}  # 所有的id对应的container

"""
导入配置文件
"""
with open("./config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


class container:
    def __init__(self, data):
        """
            表格拆出来的类。
            container: 箱号
            vesvoy: 航次
            ship: 船名
            identity: 以船名+航次构成, 来分文本文档和表格。
            fromtext: 箱号所对应的cargo类，与netweight一起由cargo_list传入
            netweight: 毛重
            data: 表格中需要的部分, 传入全表格
        """
        self.container = data["Container"]
        identity = data["Name"] + " " + data["OC VesVoy"]
        if identity in identities.keys():
            identities[identity].append(self)
        else:
            identities[identity] = [self]
        cargo_list = cargos[self.container]
        self.fromtext = cargo_list[0]
        self.netweight = cargo_list[1]
        self.data = self.process(data)

    def process(self, data):
        """
        把数据修改并按顺序排列。
        """
        newdata = {}
        for i in data.keys():  # 找出不需要改的数据
            if i in config["myfilter"]:
                newdata[i] = data[i]
        if data["ML Seal"] != "nan":  # 处理Seal
            newdata["ML Seal"] = data["ML Seal"]
        elif data["Shipper Seal"] != "nan":
            newdata["ML Seal"] = data["Shipper Seal"]
        elif data["Customs Seal"] != "nan":
            newdata["ML Seal"] = data["Customs Seal"]
        else:
            newdata["ML Seal"] = ""
        newdata["Blno"] = self.fromtext.blno
        newdata["Net weight"] = self.netweight
        newdata["Next Discharge"] = newdata["Next Discharge"][0:5]
        return newdata


class cargo:
    def __init__(self, text):
        """
            文本文档拆出来的类。
            text: 12-51全文本
            blno: 提单号 -> regex: ‘12:(.*?):’
            isadd: 是否被添加，默认False
            创建实例时向cargos字典添加自身所有的箱号
        """
        self.text = text
        self.blno = search("12:(.*?):", text).group(1)
        for i in findall("\n51:.*?'", text):  # 找51行
            container = search("51:[0-9]{3}:([A-Z]{4}[0-9]{7}[0]{0,1}):", i).group(1)  # 箱号
            netweight = round(
                float(search("51:.*?:.*?:.*?:.*?:.*?:.*?:(.*?):", i).group(1))
            )  # 毛重，删除前导零并四舍五入
            cargos[container] = [self, netweight]
        self.isadd = False #判断是否添加过


def replace(arr, replaces):
    """
    替换myfilter中的内容
    """
    for i in range(0, len(arr)):
        if arr[i] in replaces.keys():
            arr[i] = replaces[arr[i]]
    return arr


def todict(header, data):
    """
    将csv库读出的一行数据转成类似于pandas.Series的格式
    """
    result = {}
    if len(header) != len(data):
        raise Exception("wrong data length")
    for i in range(0, len(header)):
        result[header[i]] = data[i]
    return result


def txtparser(filename):
    """
    读txt并处理
    """
    txt = ""
    with open(filename, "r") as f:
        txt = f.read()
    head = txt.split("\n12")[0]  # 文本文档头
    tail = "99" + txt.split("\n12")[-1].split("\n99")[1]  # 文本文档尾

    for i in txt.split("\n12")[1:]:
        cargo(str("12" + i).split("\n99")[0])
    return head, tail


def csvparser(filename):
    """
    读csv并处理
    """
    with open(filename, "r") as f:
        reader = csv.reader(f)
        csv_header = next(reader)
        for i in reader:
            data = todict(csv_header, i)
            if data["Name"] == "":
                continue
            containers.append(container(data))
    return


def main():

    head, tail = txtparser(txtpath)
    csvparser(csvpath)

    """
    输出txt
    """
    print("txt start.")
    for key in identities:
        print("Now: " + key)
        text = head + "\n"
        for i in identities[key]:
            thiscargo = i.fromtext
            if thiscargo.isadd == False:
                text += thiscargo.text
        text = text + "\n" + tail
        with open(key + ".txt", "w") as f:
            f.write(text)
    print("Finished.")

    """
    输出csv
    """
    print("csv start.")
    for key in identities:
        print("Now: " + key)
        newcsv = [i.data for i in identities[key]]
        judges = [
            "Temp_C",
            "IMOCLS",
            "UNNO",
            "OOG front",
            "OOG left",
            "OOG rear",
            "OOG right",
            "OOG top",
        ]  # 按有无区分
        flags = {
            "Temp_C": True,
            "IMO": True,
            "IMOCLS": True,
            "UNNO": True,
            "OOG front": True,
            "OOG left": True,
            "OOG rear": True,
            "OOG right": True,
            "OOG top": True,
        }
        for i in range(0, len(newcsv)): #若有对应项则保留列名
            for j in judges:
                if str(newcsv[i][j]) != "nan" and str(newcsv[i][j]) != "0":
                    flags[j] = False
            if str(newcsv[i]["IMO"]) == "Y":
                flags["IMO"] = False

        for i in flags: #删除未使用的列名
            if flags[i]:
                for j in newcsv:
                    j.pop(i)

        newcsv.sort(key=lambda e: e["Blno"]) #根据Blno排序
        for i in range(0, len(newcsv)):  # 添加行号
            newcsv[i][""] = i + 1
        with open(key + ".csv", "w", newline="") as f:  # 写入csv
            writer = csv.DictWriter(f, [""] + config["myfilter"])  # 添加行号
            writer.writeheader()
            writer.writerows(newcsv)
    msgbox("完成")
    sys.exit(0)


"""
UI部分
"""
window = tk.Tk()
window.title("打开文件")


textframe = ttk.LabelFrame(window, text="打开文件")
textframe.grid(column=0, row=0, padx=10, pady=10)

"""
CSV
"""


def opencsv():
    global csvpath
    path = fileopenbox()
    print(path)
    csvtext.set(path)
    csvpath = path


ttk.Label(textframe, text="CSV: ").grid(column=0, row=0)
csvtext = tk.StringVar()
csvlabel = ttk.Entry(textframe, width=50, textvariable=csvtext, state="readonly")
csvlabel.grid(column=1, row=0, sticky=tk.W)
ttk.Button(textframe, text="打开", command=opencsv).grid(column=2, row=0)

"""
TXT
"""


def opentxt():
    global txtpath
    path = fileopenbox()
    print(path)
    txttext.set(path)
    txtpath = path


ttk.Label(textframe, text="TXT: ").grid(column=0, row=1)
txttext = tk.StringVar()
txtlabel = ttk.Entry(textframe, width=50, textvariable=txttext, state="readonly")
txtlabel.grid(column=1, row=1, sticky=tk.W)
ttk.Button(textframe, text="打开", command=opentxt).grid(column=2, row=1)

"""
开始、配置按钮
"""
buttons = tk.Frame(window)
buttons.grid(column=0, row=1, padx=10)


def start():
    main()


ttk.Button(buttons, text="开始", command=start).grid(
    column=0, row=2, sticky=tk.W, padx=5, pady=5
)


def editconfig():
    os.startfile("config.json")


ttk.Button(buttons, text="配置", command=editconfig).grid(
    column=1, row=2, sticky=tk.W, padx=5, pady=5
)

window.mainloop()
