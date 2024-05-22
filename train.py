
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.metrics import root_mean_squared_error
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time
import datasource.mongodb as mongodb
import pandas as pd
import build_dataset

dateFormat = r"%Y-%m-%dT%H:%M:%S%z"


def obtain_from_file():
    # data_type = [('id', 'U10'), ('value1', int), ('value2', int)]
    park_filename = 'park_dict_88909843.npz'
    dic = np.load(park_filename, allow_pickle=True)
    dataSrc = dic['data']
    targetSrc = dic['target']
    dic.close()
    return dataSrc, targetSrc


def datetime_str_range(input_date: datetime):
    """
    取得該日期的字串時間區間
    """
    start_hour, end_hour = 5, 23
    date_start = datetime.strftime(
        input_date.replace(hour=start_hour), dateFormat)
    date_end = datetime.strftime(input_date.replace(
        hour=end_hour, minute=59), dateFormat)
    return date_start, date_end


def obtain_from_DB():
    # TODO 原本是要動態取前四週(資料不夠十週)資料，目前寫死取4/15~5/13共四周資料
    start_date, end_date = datetime(2024, 4, 15), datetime(2024, 5, 17)
    start_datetime = datetime_str_range(start_date)[0]
    end_datetime = datetime_str_range(end_date)[1]
    # TODO 效能太慢了，因為我要用星期一當測試，那先取星期二的資料
    query = {
        "DataCollectTime": {"$gte": start_datetime, "$lt": end_datetime},
        "dayOfWeek": 0
    }
    datasetCol = mongodb.obtain_Dataset()
    cursor = datasetCol.find(query)
    # TODO 直接轉極耗時間嗎?
    datasetFrame = pd.DataFrame(cursor)

    data, target = build_dataset.trans_to_trainData(datasetFrame)
    return data, target


"""
training
"""
dataSrc, targetSrc = obtain_from_DB()
print(f'資料量: {len(dataSrc)}')
# TODO 36萬筆目前訓練很久，取十幾萬就好
dataAmt = 190_000
data = dataSrc[:dataAmt]
target = targetSrc[:dataAmt]

# OrdinalEncoder 應用於第一列 (index=0)
column_transformer = ColumnTransformer(
    transformers=[
        ('encoder', OrdinalEncoder(), [0])
    ],
    remainder='passthrough'  # 告訴 ColumnTransformer 其餘的列不做轉換
)
# 建立 Pipeline
pipeline = Pipeline(steps=[
    ('column_transformer', column_transformer),
    ('scaler', StandardScaler())  # 標準化全部數據
])
transformed_data = pipeline.fit_transform(data)


X_train, X_test, y_train, y_test = train_test_split(
    transformed_data, target,
    test_size=0.2, stratify=transformed_data[:, 0])

c = 1
epsilon = 0.1
svm_reg = SVR(kernel="poly", degree=4, C=c, epsilon=epsilon, gamma="scale")
svm_reg.fit(X_train, y_train)
y_pred = svm_reg.predict(X_test)
mseVal = root_mean_squared_error(y_test, y_pred)
print(f'RMSE = {mseVal}')

"""
結果顯示
"""
# 繪圖顯示中文
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False


class ResDrawer():
    def __init__(self, svm_reg, pipeline) -> None:
        self.svm_reg = svm_reg
        self.pipeline = pipeline
        # 只是要5點到23點50分，100年1月1號不用理
        self.timeAxes = [datetime(100, 1, 1, 5), datetime(100, 1, 1, 23, 50)]

    def plot_svm_regression(self, dayOfWeek, CarParkID):
        timeAxes = self.timeAxes
        # 生成每隔固定時間時間之間格
        minute_interval = timedelta(minutes=5)
        time_start, time_end = timeAxes[0], timeAxes[1]
        testList = []
        while time_start < time_end:
            culMinute = time_start.hour * 60 + time_start.minute
            testList.append([CarParkID, dayOfWeek, int(culMinute)])
            time_start += minute_interval
        test_arr = np.array(testList)

        transformed_test_arr = self.pipeline.fit_transform(test_arr)
        y_pred = self.svm_reg.predict(transformed_test_arr)

        test_arr_plot = test_arr[:, 2].astype(np.int32)
        plt.plot(test_arr_plot, y_pred, "k-",
                 linewidth=3, label=r"$\hat{y}$")  # 預測線

        plt.xticks(test_arr_plot[::8], rotation=45)

    def plot_dataset(self, X, y, label="test_dataset"):
        plt.scatter(X, y, label=label)


# TODO 暫時取5/20當驗證
# TODO 40814707 新營綠都心停車場
# TODO CarParkID: 88909843 為 復華一街停車場
query_CarParkID = "40814707"
start_datetime, end_datetime = datetime_str_range(datetime(2024, 5, 20))
query = {
    "CarParkID": query_CarParkID,
    "DataCollectTime": {"$gte": start_datetime, "$lt": end_datetime}
}
datasetCol = mongodb.obtain_Dataset()
cursor = datasetCol.find(query)
datasetFrame = pd.DataFrame(cursor)
X_test, y_test = build_dataset.trans_to_trainData(datasetFrame)

drawer = ResDrawer(svm_reg=svm_reg, pipeline=pipeline)
# 取累積時間欄位
X_test_plot = X_test[:, 2].astype(np.int32)
drawer.plot_dataset(X_test_plot, y_test, "新營綠都心停車場, 5/20星期一")
# TODO 2024-05-20 星期一，dayOfWeek=0
drawer.plot_svm_regression(dayOfWeek=0, CarParkID=query_CarParkID)

# 原始資料
# range = 228
# X_plot = data[:, 2].astype(np.int32)
# plt.plot(X_plot[:range], target[:range], '-o', label='4月22日')
# plt.plot(X_plot[range: 2*range], target[range: 2*range], '-o', label='4月29日')
# plt.plot(X_plot[2*range:], target[2*range:], '-o', label='5月6日')
# plt.legend(loc="upper left", fontsize=12)

plt.legend(fontsize=12)
plt.title(f'4/15到目前為止的資料來訓練, RMSE = {mseVal:3}')
plt.xlabel('一天累積分鐘數(60 * hour + minute)')
plt.ylabel('車位數')
plt.show()
