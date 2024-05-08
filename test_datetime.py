# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:43:55 2024

@author: Livi-Chiayi
"""

from datetime import datetime
import pandas as pd

test_date = datetime(2024, 5, 7, 5)
#weekdata
dayOfWeek = test_date.weekday()
print(dayOfWeek)

df = pd.DataFrame({
    "name": ["张三", "李四", "朱五"],
    "date": [datetime(2024, 5, 5), datetime(2024, 5, 6), datetime(2024, 5, 7)]})
df["week_num1"] = df["date"].dt.dayofweek
df["week_num2"] = df["date"].dt.weekday
df["week_name"] = df["date"].dt.day_name()
print(df)