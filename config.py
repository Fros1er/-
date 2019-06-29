import json

"""
导入配置文件
"""
with open("./config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
