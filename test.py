from data import DataAccess
from auth import Auth
import json
from datetime import datetime, timedelta

data = DataAccess()
auth = Auth()


select_cond = 'CarParkName'
filter_cond = "CarParkName/Zh_tw eq '大湳公有停車場'"
url = data.get_parkingAvail(
    city='Taoyuan', select=select_cond, filter=filter_cond)
# select=select_cond, filter=filter_cond
print(url)


# 測試減時間間格
# n = datetime.now()
# hour = timedelta(hours=1)
# prev_date = (n - hour)
# res = datetime.now() - prev_date
# print(res.total_seconds() / 3600)
