前置作業:  
1.需要建立 secret.json 放 TDX 所需資料，如下  
{  
 "app_id": "",  
 "app_key": ""  
}

2.MongoDB 的 doument name(table name)為'Parking_Project' (可在 config.json 修改)  
裡面有 collection  
'Time_ParkingAvailability'(以時間為 id 存停車場剩餘車位)  
和 'Time_CarPark' (停車場資訊，因為停車場資訊屬於不太變動資料所以暫沒用到)

各檔案功能:  
schedule\_job.py 執行週期性任務  
fetch\_TDX.py 抓取 TDX 資料並存入資料庫  
program.py 輸出特定資料時用此程式撰寫  
test.py 測試想到的 code 能不能正常執行  
test*開頭的都是測試對應功能細節有無正常運作  
build_dataset.py 將收集的原始停車位剩餘位資料轉成訓練用格式，可選擇存入 DB 或存成 numpy file  
build_dataset_multithread.py 使用 build_dataset function 的多執行續版本  
train.py 目前訓練+預測車位  
train.\_1hun.py 易鴻的 train 版本
