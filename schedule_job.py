

import schedule
import time
import fetch_TDX as tdx


def fetch_TDX_task():
    tdx.main()


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
    count = 1
    while True:
        # 運行所有可運行的任務
        schedule.run_pending()
        print(f'執行第{count}次')
        count += 1
        # 暫停一定時間後再檢查，減少電腦資源使用
        time.sleep(60)


if __name__ == '__main__':
    run_scheduler()
