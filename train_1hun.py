import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# 解析 JSON 資料並提取所需特徵


def parse_data(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        data = json.load(file)

    features = []
    for entry in data:
        car_park_name = entry['CarParkName']
        available_spaces = entry['Availabilities'][0]['AvailableSpaces']
        total_spaces = entry['Availabilities'][0]['NumberOfSpaces']
        collect_time = datetime.strptime(
            entry['DataCollectTime'], '%Y-%m-%dT%H:%M:%S%z')

        features.append({
            'CarParkName': car_park_name,
            'AvailableSpaces': available_spaces,
            'TotalSpaces': total_spaces,
            'CollectTime': collect_time
        })

    return features

# 準備訓練和測試資料


def prepare_data(data):
    X = np.array([[entry['TotalSpaces'], entry['CollectTime'].hour,
                 entry['CollectTime'].minute] for entry in data])
    y = np.array([entry['AvailableSpaces'] for entry in data])
    return X, y

# 主函數


def main():
    # 設定字體以顯示繁體中文
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 微軟正黑體
    plt.rcParams['axes.unicode_minus'] = False  # 用於正常顯示負號

    # 讀取資料
    data_dir = 'D:/BigData/AI/Train'
    all_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(data_dir, filename)
            all_data.extend(parse_data(file_path))

    # 將數據按日期排序
    all_data.sort(key=lambda x: x['CollectTime'])

    predictions = pd.DataFrame(
        columns=['CarParkName', 'PredictedAvailableSpaces', 'Date'])
    rmses = []  # 用於儲存每次預測的RMSE

    # 進行訓練、驗證和預測
    window_size = 7

    for start_index in range(len(all_data) - window_size):
        train_data = all_data[start_index:start_index + window_size]
        test_data = [all_data[start_index + window_size]]

        X_train, y_train = prepare_data(train_data)
        X_test, y_test = prepare_data(test_data)

        # 訓練模型
        model = LinearRegression()
        model.fit(X_train, y_train)

        # 預測第8天的情況
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        # 檢查實際資料中是否存在預測日期的資料
        if test_data[0] in all_data:
            rmses.append(rmse)
            print(
                f"Mean Squared Error for prediction on {test_data[0]['CollectTime'].date()}: {mse}")
            print(f"Root Mean Squared Error for prediction: {rmse}")

            # 保存預測結果
            predictions = pd.concat([predictions, pd.DataFrame({'CarParkName': [test_data[0]['CarParkName']], 'PredictedAvailableSpaces': [
                                    y_pred[0]], 'Date': [test_data[0]['CollectTime'].date()]})], ignore_index=True)

            # 将预测的第8天数据加入训练集中
            all_data[start_index + window_size]['AvailableSpaces'] = y_pred[0]
        else:
            print(
                f"No data available for prediction on {test_data[0]['CollectTime'].date()}. Skipping...")

    # 將預測結果保存為 CSV 文件到使用者的 "Documents" 資料夾
    output_file_path = os.path.expanduser('~/Documents/predictions.csv')
    predictions.to_csv(output_file_path, index=False)

    # 繪製圖表
    for car_park in predictions['CarParkName'].unique():
        park_data = predictions[predictions['CarParkName'] == car_park]
        plt.plot(park_data['Date'],
                 park_data['PredictedAvailableSpaces'], label=car_park)

    plt.xlabel('日期')
    plt.ylabel('預測可用車位數')
    plt.title('各日期預測可用車位數')
    plt.legend()
    plt.show()

    # 顯示每次預測的RMSE
    for i, rmse in enumerate(rmses, start=1):
        print(f"第 {i} 次預測的 RMSE: {rmse}")


# 執行主函數
if __name__ == "__main__":
    main()
