
import json
from pymongo import MongoClient


def obtain_db():
    # 讀入設定檔
    f = open("config.json", "r", encoding="utf-8")
    config = json.load(f)
    f.close()

    client = MongoClient(config["connect_db_str"])
    db = client[config["db_name"]]
    return db


def obtain_ParkingAvailability():
    db = obtain_db()
    parkCol = db['Time_ParkingAvailability']
    return parkCol
