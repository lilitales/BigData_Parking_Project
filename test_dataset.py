
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


def build_DataFrame(parkingDataCursor):
    """
    MongoDB每筆ParkingAvailability(Cursor)轉為DataFrame格式
    """
    # 停車場ID, 停車場名稱, 資料收集時間, 總車位數, 剩餘車位數, 星期幾, 從0點開始累積得分鐘數,
    parkFrame = pd.DataFrame(
        columns=["CarParkID", "CarParkName", "DataCollectTime",
                 "NumberOfSpaces", "AvailableSpaces", "dayOfWeek", "culMinutes"]
    )

    # 用index新增dataFrame一筆資料
    dataIdx = 0
    for cur in parkingDataCursor:
        parkList = cur['ParkingAvailabilities']
        # 這時間點蒐集的所有停車場資料
        collectDatetime = datetime.strptime(cur['SrcUpdateTime'], dateFormat)
        # 從0點開始累積得分鐘數
        culMinutes = collectDatetime.hour * 60 + collectDatetime.minute
        for park in parkList:
            # 跳過未營業停車場
            # 1: 營業, 0:未營業
            if park['ServiceStatus'] == 0:
                print(parse_park_name(park) + " 未營業")
                continue

            # 只取SpaceType:1(自小客車)的資料
            availTypeList = park['Availabilities']
            hasCarPark = False
            for avail in availTypeList:
                if avail['SpaceType'] == 1:
                    hasCarPark = True
                    numberOfSpaces = avail['NumberOfSpaces']
                    availableSpaces = avail['AvailableSpaces']

            # 此停車場沒有自小客車車位
            if hasCarPark == False:
                print(
                    f"停車場: {park['CarParkID']}/{parse_park_name(park)} 未設置小客車車位")
                continue

            data = {
                "CarParkID": park['CarParkID'],
                "CarParkName": parse_park_name(park),
                "DataCollectTime": collectDatetime,
                "NumberOfSpaces": numberOfSpaces,
                "AvailableSpaces": availableSpaces,
                "culMinutes": culMinutes,
            }
            parkFrame.loc[dataIdx] = data
            dataIdx += 1
            if dataIdx % 600 == 0:
                print(f'處理至第{dataIdx}筆')
    # 轉換這日期是星期幾
    parkFrame["dayOfWeek"] = parkFrame["DataCollectTime"].dt.dayofweek
    return parkFrame


def save_to_numpyFile(filename: str, data: np.ndarray, target: np.ndarray):
    np.savez(filename, data=data, target=target)
    # 只是載回來確認存入是否正常
    dic = np.load(filename, allow_pickle=True)
    X = dic['data']
    y = dic['target']
    dic.close()


# CarParkID: 88909843 為 復華一街停車場
filter_CarParkId = '88909843'
date_base = datetime(2024, 4, 22)
aWeek = timedelta(days=7)

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

parkFrame = build_DataFrame(cursor)
# data = parkFrame[['CarParkID', 'dayOfWeek', 'culMinutes']].to_numpy()
# target = parkFrame['AvailableSpaces'].to_numpy()

# filename = 'park_dict_88909843.npz'
# save_to_numpyFile(filename, data, target)
