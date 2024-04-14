前置作業:  
1.需要建立secret.json放TDX所需資料，如下  
{  
    "app_id": "",  
    "app_key": ""  
}  

2.MongoDB的doument name(database name)為'Parking_Project' (可在config.json修改)  
裡面有collection  
'Time_ParkingAvailability'(以時間為id存停車場剩餘車位)  
和 'Time_CarPark' (停車場資訊，因為停車場資訊屬於不太變動資料所以暫沒用到)  


各檔案功能:
schedule_job.py 執行週期性任務  
fetch_TDX.py 抓取TDX資料並存入資料庫  
program.py 輸出特定資料時用此程式撰寫  
test.py 測試想到的code能不能正常執行  
