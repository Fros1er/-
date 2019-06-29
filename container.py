from config import config


class container:
    def __init__(self, data, cargos):
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
        cargo_list = cargos[self.container]
        self.fromtext = cargo_list[0]
        self.netweight = cargo_list[1]
        self.process(data)

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
        self.data = newdata
        return

    def getidentity(self):
        return self.data["Name"] + " " + self.data["OC VesVoy"]
