

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import datasource.mongodb as mongodb


class Finder():
    def __init__(self) -> None:
        self.db = mongodb.obtain_db()

    def find(self, query):
        parkCol = self.db['Time_ParkingAvailability']
        return parkCol.find(query)


def main():
    db = mongodb.obtain_db()
    parkCol = db['Time_ParkingAvailability']

    # 用第一筆資料的所有停車場取停車場名稱
    first = parkCol.find_one({}, {'ParkingAvailabilities': 1})
    parkNameList = [res['CarParkName']['Zh_tw']
                    for res in first['ParkingAvailabilities']]

    # TODO 改成輸入哪個停車場名稱
    selectPark = parkNameList[8]

    # 條件
    dateFormat = r"%Y-%m-%dT%H:%M:%S%z"
    date_start = datetime.strftime(datetime(2024, 4, 20, 5), dateFormat)
    date_end = datetime.strftime(datetime(2024, 4, 20, 23, 59), dateFormat)

    query = {
        "ParkingAvailabilities": {
            "$elemMatch": {
                "CarParkName.Zh_tw": selectPark
            }
        },
        "UpdateTime": {"$gte": date_start, "$lt": date_end}
    }
    # 取哪個欄位
    projection = {'_id': 0, 'ParkingAvailabilities.$': 1}

    cursor = parkCol.find(
        query, projection)
    # TODO 資料量很大時使用list會將所有資料載入memory
    # resList = list(cursor)
    dataTimeList, availList = [], []
    for cur in cursor:
        res = cur['ParkingAvailabilities'][0]
        dataTimeList.append(
            datetime.strptime(res['DataCollectTime'], dateFormat))
        availList.append(res['AvailableSpaces'])

    time_arr = np.array(
        list(map(lambda date: datetime.strftime(date, "%H:%M"), dataTimeList)))
    # print(time_arr)
    # print(availList)

    # 繪圖顯示中文
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False
    lineList = plt.plot(time_arr, availList, '-o', label='星期六')
    line = lineList[0]
    plt.legend(handles=[line], loc="center left")
    # 旋轉標籤以節省空間
    plt.xticks(time_arr[::8], rotation=45)

    plt.title(selectPark)
    plt.xlabel('時間')
    plt.ylabel('車位數')
    plt.show()


if __name__ == '__main__':
    main()
