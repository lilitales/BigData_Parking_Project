
import threading
import build_dataset
import datasource.mongodb as mongodb

import numpy as np


def process_data(idxStart, limit):
    """
    multi-thread執行之程式
    """
    parkCol = mongodb.obtain_ParkingAvailability()
    cursor = parkCol.find().skip(idxStart).limit(limit)
    parkFrame = build_dataset.build_DataFrame(cursor)
    build_dataset.save_to_db(parkFrame)


def split_by_partNum(dataAmt, partNum):
    """
    例如: 34567(dataAmt)筆每10000(partNum)切一份就是[10000, 10000, 4567]
    """
    shape = dataAmt // partNum
    # ex: np.full(3, 5)為[5, 5, 5]
    full_parts = np.full(shape, partNum)
    # 計算剩下的數量
    remainder = dataAmt % partNum
    # 如果有剩下的數量，則加到結果中
    if remainder > 0:
        result = np.append(full_parts, remainder)
    else:
        result = full_parts
    return result.tolist()


parkCol = mongodb.obtain_ParkingAvailability()
# 總筆數
dataAmt = parkCol.count_documents({})
# 目的：因為是先讀取所有資料再寫入DB，所以分多批次的多執行緒，才能釋放資源
partAmt = 100  # 每個thread要處理幾筆資料(*60才是實際筆數)
batchAmt = 10  # 分幾批處理
partNumList = split_by_partNum(dataAmt, partAmt)

thread_idx_start = 0
for i, sub_partNumList in enumerate(np.array_split(partNumList, batchAmt)):
    threads = []
    for sub_partNum in sub_partNumList:
        thread = threading.Thread(
            target=process_data, args=(thread_idx_start, sub_partNum))
        # 根據處理了多少資料決定下一個Thread從哪邊開始處理資料
        thread_idx_start += sub_partNum
        threads.append(thread)
        thread.start()
    # 等待所有執行緒完成
    for thread in threads:
        thread.join()
    print(f'index: {i} 批次結束')

print(f'{dataAmt}({dataAmt * 60})筆完成')
