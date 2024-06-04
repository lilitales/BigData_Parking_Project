

import schedule
import time
import datetime
import fetch_TDX as tdx
import signal
import sys

exec_count = 1
producer = None


def signal_handler(sig, frame):
    if producer:
        producer.close()
    print("producer closed")
    sys.exit(0)


# 註冊信號處理器，用於處理中斷信號
signal.signal(signal.SIGINT, signal_handler)


def fetch_TDX_task():
    global exec_count
    global producer
    try:
        impl = tdx.KafkaImplParkingAvail()
        impl.produce_parkingAvail()
        time.sleep(1)
        impl.consume_parkingAvail()

        producer = impl.get_producer()
    except Exception as e:
        print(e)
    print(f'執行第{exec_count}次 time:{datetime.datetime.now()}')
    exec_count += 1


def setup_schedule():
    interval_minutes = 5

    # 清除所有現有的排程
    schedule.clear()
    # 設定每x分鐘執行一次的排程
    schedule.every(interval_minutes).minutes.do(fetch_TDX_task)

    # 印出目前的排程狀態來確認設定
    for job in schedule.jobs:
        print(job)


def run_scheduler():
    setup_schedule()

    schedule.run_all(delay_seconds=5)
    while True:
        # 運行所有可運行的任務
        schedule.run_pending()
        # 暫停一定時間後再檢查，減少電腦資源使用
        time.sleep(60)


if __name__ == '__main__':
    run_scheduler()
