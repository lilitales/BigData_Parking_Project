
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.metrics import root_mean_squared_error
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, time

# data_type = [('id', 'U10'), ('value1', int), ('value2', int)]

park_filename = 'park_dict_88909843.npz'
dic = np.load(park_filename, allow_pickle=True)
dataSrc = dic['data']
targetSrc = dic['target']
dic.close()

# TODO 36萬筆目前訓練很久，取十幾萬就好
dataAmt = 130_00
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


def plot_svm_regression(svm_reg, pipeline, X, y, timeAxes):
    # TODO dayOfWeek : 0 (星期一)
    # TODO CarParkID: 88909843 為 復華一街停車場
    dayOfWeek = 0
    CarParkID = "88909843"
    minute_interval = timedelta(minutes=5)
    time_start, time_end = timeAxes[0], timeAxes[1]
    testList = []
    while time_start < time_end:
        culMinute = time_start.hour * 60 + time_start.minute
        testList.append([CarParkID, dayOfWeek, int(culMinute)])
        time_start += minute_interval

    test_arr = np.array(testList)
    # print(test_arr)
    transformed_test_arr = pipeline.fit_transform(test_arr)
    y_pred = svm_reg.predict(transformed_test_arr)

    test_arr_plot = test_arr[:, 2].astype(np.int32)
    plt.plot(test_arr_plot, y_pred, "k-",
             linewidth=3, label=r"$\hat{y}$")  # 預測線

    plt.xticks(test_arr_plot[::8], rotation=45)


# 繪圖顯示中文
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

timeAxes = [datetime(100, 1, 1, 5), datetime(100, 1, 1, 23, 50)]
plot_svm_regression(svm_reg, pipeline, data, target, timeAxes)
# 原始資料
range = 228
X_plot = data[:, 2].astype(np.int32)
plt.plot(X_plot[:range], target[:range], '-o', label='4月22日')
plt.plot(X_plot[range: 2*range], target[range: 2*range], '-o', label='4月29日')
plt.plot(X_plot[2*range:], target[2*range:], '-o', label='5月6日')
plt.legend(loc="upper left", fontsize=12)

plt.title(f'復華一街停車場, 星期一, RMSE = {mseVal:3}')
plt.xlabel('一天累積分鐘數(60 * hour + minute)')
plt.ylabel('車位數')
plt.show()
