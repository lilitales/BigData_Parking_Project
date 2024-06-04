
import json
from pymongo import MongoClient
from pathlib import Path


def load_json_file(pFilename):
    # 讀入設定檔
    filename = f"{pFilename}.json"
    assert Path(filename).exists(), f'{filename} 不存在'
    f = open(filename, "r", encoding="utf-8")
    config = json.load(f)
    f.close()
    return config


def obtain_db():
    config = load_json_file('config')
    db_config = load_json_file('secret_connection')

    client = MongoClient(db_config["connect_db_str"])
    db = client[config["db_name"]]
    return db


def obtain_ParkingAvailability():
    db = obtain_db()
    parkCol = db['Time_ParkingAvailability']
    return parkCol


def obtain_Dataset():
    db = obtain_db()
    datasetCol = db['Dataset']
    return datasetCol
