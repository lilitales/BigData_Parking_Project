# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:43:55 2024

@author: Livi-Chiayi
"""

from datetime import datetime
import pandas as pd

# test_date = datetime(2024, 5, 7, 5)
# #weekdata
# dayOfWeek = test_date.weekday()
# print(dayOfWeek)

# df = pd.DataFrame({
#     "name": ["张三", "李四", "朱五"],
#     "date": [datetime(2024, 5, 5), datetime(2024, 5, 6), datetime(2024, 5, 7)]})
# df["week_num1"] = df["date"].dt.dayofweek
# df["week_num2"] = df["date"].dt.weekday
# df["week_name"] = df["date"].dt.day_name()
# print(df)

dateFormat = r"%Y-%m-%dT%H:%M:%S%z"
srcUpdateTime = "2024-04-15T02:43:01+08:00"
test_date = datetime.strptime(srcUpdateTime, dateFormat)
parkFrame = pd.DataFrame(
    columns=["CarParkID", "DataCollectTime", "dayOfWeek"]
)
data = {"CarParkID": "123", "DataCollectTime": test_date}
parkFrame.loc[0] = data
parkFrame["dayOfWeek"] = parkFrame["DataCollectTime"].dt.dayofweek

print(parkFrame[parkFrame.columns.difference(['DataCollectTime'])])
