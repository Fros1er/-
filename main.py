# -*- coding: utf-8 -*-

from re import findall, search
import csv

from gui import gui
from container import container
from config import config
from cargo import cargo

cargos = {}  # 此处是cargo类与箱号的查询字典，直接用箱号查。包含一个数组，[0]为cargo类，[1]为毛重。
containers = []  # csv的每一行。
identities = {}  # 所有的id对应的container


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
        text = str("12" + i).split("\n99")[0]
        thiscargo = cargo(text)
        for i in findall("\n51:.*?'", text):  # 找51行
            container = search("51:[0-9]{3}:([A-Z]{4}[0-9]{7}[0]{0,1}):", i).group(1)  # 箱号
            netweight = round(
                float(search("51:.*?:.*?:.*?:.*?:.*?:.*?:(.*?):", i).group(1))
            )  # 毛重，删除前导零并四舍五入
            cargos[container] = [
                thiscargo,
                netweight,
            ]  # 以自身所具有的箱号作为cargos字典的key，其中记录自己的引用和毛重
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
            thiscontainer = container(data, cargos)
            containers.append(thiscontainer)
            thisidentity = thiscontainer.getidentity()
            if thisidentity in identities.keys():
                identities[thisidentity].append(thiscontainer)
            else:
                identities[thisidentity] = [thiscontainer]
    return


def main(csvpath, txtpath, ui):
    """
    主函数
    """
    ui.changeinf("读取中")
    head, tail = txtparser(txtpath)
    csvparser(csvpath)

    """
    输出txt
    """
    ui.changeinf("开始输出txt")
    for key in identities:
        ui.changeinf("正在输出txt\n" + key)
        text = head + "\n"
        for i in identities[key]:
            thiscargo = i.fromtext
            if thiscargo.isadd == False:
                text += thiscargo.text
        text = text + "\n" + tail
        with open(key + ".txt", "w") as f:
            f.write(text)
    ui.changeinf("txt输出完成")

    """
    输出csv
    """
    ui.changeinf("开始输出csv")
    for key in identities:
        ui.changeinf("正在输出csv\n" + key)
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
        for i in range(0, len(newcsv)):  # 若有对应项则保留列名
            for j in judges:
                if str(newcsv[i][j]) != "nan" and str(newcsv[i][j]) != "0":
                    flags[j] = False
            if str(newcsv[i]["IMO"]) == "Y":
                flags["IMO"] = False

        for i in flags:  # 删除未使用的列名
            if flags[i]:
                for j in newcsv:
                    j.pop(i)

        newcsv.sort(key=lambda e: e["Blno"])  # 根据Blno排序
        for i in range(0, len(newcsv)):  # 添加行号
            newcsv[i][""] = i + 1
        with open(key + ".csv", "w", newline="") as f:  # 写入csv
            writer = csv.DictWriter(f, [""] + config["myfilter"])  # 添加行号
            writer.writeheader()
            writer.writerows(newcsv)
        ui.changeinf("完成")
    return


if __name__ == "__main__":
    ui = gui(main)
    ui.window.mainloop()
