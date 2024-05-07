
import json
import datasource.mongodb as mongodb
from datasource.data import DataAccess
from datetime import datetime

# 讀入設定檔
f = open("config.json", "r", encoding="utf-8")
config = json.load(f)
f.close()

db = mongodb.obtain_db()
data = DataAccess()
dateFormat = r"%Y-%m-%dT%H:%M:%S%z"
parkingAvail_collection_name = 'Time_ParkingAvailability'


def main():
    city = 'Tainan'
    parkInfo = data.get_parkingAvail(city)

    col = db[parkingAvail_collection_name]
    # 用時間替代id
    str_now = datetime.strftime(datetime.now(), dateFormat)
    parkInfo['_id'] = str_now
    col.insert_one(parkInfo)


if __name__ == '__main__':
    main()
