import threading
import queue
import time

# 定義執行緒工作函數


def process_data(data_slice, result_queue):

    if 55 in data_slice:
        time.sleep(2)
        print(f'slice: {data_slice}')
        time.sleep(5)
        print(f'sleep done')
    else:
        print(f'slice: {data_slice}')
    # 假設我們簡單地計算數據片段的總和
    result = sum(data_slice)
    # 把結果放入隊列中
    result_queue.put(result)


# 生成模擬數據
data = list(range(300))  # 0, 1, 2, ..., 299

# 創建結果隊列
results_queue = queue.Queue()

# 創建執行緒列表
threads = []

# 分割數據並創建執行緒
for i in range(3):
    start_index = i * 100
    end_index = start_index + 100
    thread = threading.Thread(target=process_data, args=(
        data[start_index:end_index], results_queue))
    threads.append(thread)
    thread.start()

# 等待所有執行緒完成
for thread in threads:
    thread.join()

# 收集結果
total_result = 0
while not results_queue.empty():
    total_result += results_queue.get()

print("Total sum of all elements:", total_result)
