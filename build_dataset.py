

"""
1.取得DB資料
2.data為{停車場ID, 星期幾(0~6，0為星期一), 時間(時和分)}
3.label(target)為剩餘車輛數
"""

import pandas as pd
from datetime import datetime
import datasource.mongodb as mongodb
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

dateFormat = r"%Y-%m-%dT%H:%M:%S%z"
debug = False


def parse_park_name(park):
    return park['CarParkName']['Zh_tw']


"""
資料庫取得所需資料
"""
# 停車場ID, 星期幾, 從0點開始累積得分鐘數, 時間, 剩餘車位數
parkFrame = pd.DataFrame(
    columns=["CarParkID", "dayOfWeek",
             "culMinutes", "datetime", "AvailableSpaces"]
)
parkCol = mongodb.obtain_ParkingAvailability()
# 取哪個欄位
# projection = {'_id': 1, 'ParkingAvailabilities.$': 1}
if debug == False:
    cursor = parkCol.find()
else:
    cursor = parkCol.find().skip(1000).limit(100)

dataIdx = 0
for cur in cursor:
    parkList = cur['ParkingAvailabilities']
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
# parkFrame.hist(bins=50, figsize=(20,15))
# plt.show()

"""
建立dataset
data和target兩組array，用index對應
"""
data = parkFrame[['CarParkID', 'dayOfWeek', 'culMinutes']].to_numpy()
target = parkFrame['AvailableSpaces'].to_numpy()

# TODO 測試用，看資料分布
# res = pd.Series(parkFrame['CarParkID']).value_counts(normalize=True)
# print(res)
# TODO 測試用，看資料分布
# X_train, X_test, y_train, y_test = train_test_split(data, target)
# r = pd.Series(X_train[:, 0]).value_counts(normalize=True)
# print(r)

# TODO 看是要寫成json、csv還是存入MongoDB


def save_to_db(parkFrame: pd.DataFrame):
    db = mongodb.obtain_db()
    dataCol = db['Dataset']
    # 清除舊有資料
    dataCol.delete_many({})
    # records: 多個物件，每個物件都有key和value
    insert = parkFrame[['CarParkID', 'dayOfWeek',
                        'culMinutes', 'AvailableSpaces']].to_dict('records')
    dataCol.insert_many(insert)


def save_to_numpyFile(data: np.ndarray, target: np.ndarray):
    park_filename = 'park_dict.npz'
    np.savez(park_filename, data=data, target=target)
    # 只是載回來確認存入是否正常
    dic = np.load(park_filename, allow_pickle=True)
    X = dic['data']
    y = dic['target']
    dic.close()
    # print(y)


save_to_numpyFile(data, target)
save_to_db(parkFrame)
print('done')
