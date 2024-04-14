
from auth import Auth
import requests
import json
import urllib.parse as parse


class DataAccess():
    def __init__(self) -> None:
        self.data_header = Auth().get_data_header()

    def get_data_response(self, url):
        data_response = requests.get(url, headers=self.data_header)
        return json.loads(data_response.text)

    def _build_query_params(self, select=None, filter=None):
        '''
        https://motc-ptx.gitbook.io/tdx-xin-shou-zhi-yin/api-te-se-shuo-ming/zhi-yuan-odata-cha-xun-yu-fa/odata-jian-jie
        OData格式(Open Data Protocol)
        select ->取哪個欄位
        filter ->過濾資料
        '''
        params = {'$format': 'JSON',
                  # 要它回傳取得的數量
                  '$count': 'true',
                  }
        if select is not None:
            # url += rf"$select={select}"
            params['$select'] = select
        if filter is not None:
            # url += rf"$filter={filter}"
            params['$filter'] = filter
        # URL參數編碼
        res = parse.urlencode(params, quote_via=parse.quote)
        return res

    def get_parkingAvail(self, city, select=None, filter=None):
        '''
        路外停車場剩餘車位
        '''
        parkingAvail_url = r"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/{city}"
        paramStr = self._build_query_params(select, filter)
        url = parkingAvail_url.format(city=city)
        # 增加參數
        send_url = url + '?' + paramStr
        return self.get_data_response(send_url)

    def get_parkingInfo(self, city, select=None, filter=None):
        '''
        停車場基本資料
        '''
        parkInfo_url = r"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark/City/{city}"
        paramStr = self._build_query_params(select, filter)
        url = parkInfo_url.format(city=city)
        # 增加參數
        send_url = url + '?' + paramStr
        return self.get_data_response(send_url)
