
import pandas as pd
from datetime import datetime, timedelta
import datasource.mongodb as mongodb
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

dateFormat = r"%Y-%m-%dT%H:%M:%S%z"


def parse_park_name(park):
    return park['CarParkName']['Zh_tw']


def date_str_range(input_date):
    start_hour, end_hour = 5, 23
    date_start = datetime.strftime(
        input_date.replace(hour=start_hour), dateFormat)
    date_end = datetime.strftime(input_date.replace(
        hour=end_hour, minute=59), dateFormat)
    return date_start, date_end


# CarParkID: 88909843 為 復華一街停車場
filter_CarParkId = '88909843'
date_base = datetime(2024, 4, 22)
aWeek = timedelta(days=7)

# 停車場ID, 星期幾, 從0點開始累積得分鐘數, 時間, 剩餘車位數
parkFrame = pd.DataFrame(
    columns=["CarParkID", "dayOfWeek",
             "culMinutes", "datetime", "AvailableSpaces"]
)
parkCol = mongodb.obtain_ParkingAvailability()

d1_start, d1_end = date_str_range(date_base)
d2_start, d2_end = date_str_range(date_base + aWeek)
d3_start, d3_end = date_str_range(date_base + 2*aWeek)
query = {
    "$or": [
        {"UpdateTime": {"$gte": d1_start, "$lt": d1_end}},
        {"UpdateTime": {"$gte": d2_start, "$lt": d2_end}},
        {"UpdateTime": {"$gte": d3_start, "$lt": d3_end}},
    ]
}
cursor = parkCol.find(query)

dataIdx = 0
for cur in cursor:
    parkListSrc = cur['ParkingAvailabilities']
    parkList = list(
        filter(lambda data: data['CarParkID'] == filter_CarParkId, parkListSrc))
    # 這時間點蒐集的所有停車場資料
    collectDatetime = datetime.strptime(cur['SrcUpdateTime'], dateFormat)
    # 從0點開始累積得分鐘數
    culMinutes = collectDatetime.hour * 60 + collectDatetime.minute
    for park in parkList:
        # 1: 營業, 0:未營業
        if park['ServiceStatus'] == '0':
            print(parse_park_name(park) + " 未營業")
            continue

        data = {
            "CarParkID": park['CarParkID'],
            "datetime": collectDatetime,
            "culMinutes": culMinutes,
            "AvailableSpaces": park['AvailableSpaces']
        }
        parkFrame.loc[dataIdx] = data
        dataIdx += 1
        if dataIdx % 600 == 0:
            print(f'處理至第{dataIdx}筆')
# 轉換這日期是星期幾
parkFrame["dayOfWeek"] = parkFrame["datetime"].dt.dayofweek

data = parkFrame[['CarParkID', 'dayOfWeek', 'culMinutes']].to_numpy()
target = parkFrame['AvailableSpaces'].to_numpy()


def save_to_numpyFile(filename: str, data: np.ndarray, target: np.ndarray):
    np.savez(filename, data=data, target=target)
    # 只是載回來確認存入是否正常
    dic = np.load(filename, allow_pickle=True)
    X = dic['data']
    y = dic['target']
    dic.close()


filename = 'park_dict_88909843.npz'
save_to_numpyFile(filename, data, target)
