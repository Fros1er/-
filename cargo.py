from re import findall, search

class cargo:
    def __init__(self, text):
        """
            文本文档拆出来的类。
            text: 12-51全文本
            blno: 提单号 -> regex: ‘12:(.*?):’
            isadd: 是否被添加，默认False
        """
        self.text = text
        self.blno = search("12:(.*?):", text).group(1)
        self.isadd = False #判断是否添加过
