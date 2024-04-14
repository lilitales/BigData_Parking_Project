from data import DataAccess
import json

data = DataAccess()

city = 'Taoyuan'
# $filter條件
filter_cond = "CarParkName/Zh_tw eq '大湳公有停車場'"

# 取得指定停車場剩餘車位
# $select 條件
select_cond = 'CarParkName,AvailableSpaces'
parkData = data.get_parkingAvail(
    city=city, select=select_cond, filter=filter_cond)
parkObj = parkData['ParkingAvailabilities'][0]

# 取得指定停車場基本資料
info_select_cond = 'CarParkName,Address,CarParkPosition'
infoData = data.get_parkingInfo(
    city=city, select=info_select_cond, filter=filter_cond)
infoObj = infoData['CarParks'][0]

# 輸出暫存物件
outObj = {'停車場名稱': parkObj['CarParkName']['Zh_tw'],
          '地址': infoObj['Address'],
          '經緯度': infoObj['CarParkPosition'],
          '剩餘車位': str(parkObj['AvailableSpaces']) + '格'
          }
outputStr = ', \n'.join(f'{key}: {val}' for key, val in outObj.items())
print(outputStr)
