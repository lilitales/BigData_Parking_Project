from data import DataAccess
from auth import Auth
import json
from datetime import datetime, timedelta
import requests
from pathlib import Path

data = DataAccess()
auth = Auth()


# select_cond = 'CarParkName'
# filter_cond = "CarParkName/Zh_tw eq '大湳公有停車場'"
# url = data.get_parkingAvail(
#     city='Taoyuan', select=select_cond, filter=filter_cond)
# # select=select_cond, filter=filter_cond
# print(url)


# 測試減時間間格
# n = datetime.now()
# hour = timedelta(hours=1)
# prev_date = (n - hour)
# res = datetime.now() - prev_date
# print(res.total_seconds() / A3600)


parkingAvail_url = r"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/{city}".format(
    city='aaa')

paramStr = data._build_query_params()
send_url = parkingAvail_url + '?' + paramStr
try:
    response = data._send_request(send_url)
    print(response)
except Exception as e:
    print(e)


# p = Path(f'./log/123_errLog.txt')
# print(p.resolve())
