

"""
1.取得DB資料
2.data為{停車場ID, 星期幾(0~6，0為星期一), 時間(時和分)}
3.label(target)為剩餘車輛數
"""

import pandas as pd
from datetime import datetime
import datasource.mongodb as mongodb
import numpy as np
dateFormat = r"%Y-%m-%dT%H:%M:%S%z"


def parse_park_name(park):
    return park['CarParkName']['Zh_tw']


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

    if parkFrame.empty:
        # 沒資料代表都沒營業或都沒小客車停車場，這不太可能，肯定程式哪邊出錯
        raise ValueError("DataFrame為空")

    # 轉換這日期是星期幾
    parkFrame["dayOfWeek"] = parkFrame["DataCollectTime"].dt.dayofweek
    return parkFrame

# TODO 測試用，看資料分布
# res = pd.Series(parkFrame['CarParkID']).value_counts(normalize=True)
# print(res)
# TODO 測試用，看資料分布
# X_train, X_test, y_train, y_test = train_test_split(data, target)
# r = pd.Series(X_train[:, 0]).value_counts(normalize=True)
# print(r)


def save_to_db(parkFrame: pd.DataFrame, clean_col=False):
    db = mongodb.obtain_db()
    dataCol = db['Dataset']
    if clean_col:
        # 清除舊有資料
        dataCol.delete_many({})

    # records: 多個物件，每個物件都有key和value
    # 指定欄位
    # insert = parkFrame[['CarParkID', 'dayOfWeek',
    #                     'culMinutes', 'AvailableSpaces']].to_dict('records')
    # 全部欄位
    # TODO 因為timestamp輸入MongoDB會產生時區消失導致時間錯誤的問題，所以先用字串存日期
    copy_frame = parkFrame.copy()
    copy_frame['DataCollectTime'] = copy_frame['DataCollectTime'].dt.strftime(
        dateFormat)
    insert = copy_frame.to_dict('records')
    dataCol.insert_many(insert)


def save_to_numpyFile(park_filename: str, data: np.ndarray, target: np.ndarray):
    np.savez(park_filename, data=data, target=target)
    # 只是載回來確認存入是否正常
    dic = np.load(park_filename, allow_pickle=True)
    X = dic['data']
    y = dic['target']
    # TODO 印出來看測試用
    # print(X)
    # print(y)
    dic.close()


def trans_to_trainData(parkFrame):
    """
    data和target兩組array，用index對應
    data為停車場ID, 星期幾, 從0點開始累積得分鐘數
    target(label)為剩餘車位數
    """
    data = parkFrame[['CarParkID', 'dayOfWeek', 'culMinutes']].to_numpy()
    target = parkFrame['AvailableSpaces'].to_numpy()
    return data, target


if __name__ == '__main__':
    debug = True
    saveNumpy = False
    saveDB = True

    parkCol = mongodb.obtain_ParkingAvailability()
    # 取哪個欄位
    # projection = {'_id': 1, 'ParkingAvailabilities.$': 1}
    if debug == False:
        cursor = parkCol.find()
    else:
        # cursor = parkCol.find().skip(1000).limit(2)
        cursor = parkCol.find().limit(1)

    parkFrame = build_DataFrame(cursor)
    if saveDB:
        save_to_db(parkFrame, clean_col=True)

    # 存numpy檔
    if saveNumpy:
        data, target = trans_to_trainData(parkFrame)
        park_numpy_filename = 'park_dict.npz'
        save_to_numpyFile(park_numpy_filename, data, target)
    print('done')
