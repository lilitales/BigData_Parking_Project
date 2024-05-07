
from datasource.auth import Auth
import requests
import json
import urllib.parse as parse
from pathlib import Path
from datetime import datetime


class DataAccess():
    def __init__(self) -> None:
        self.auth_singleton = Auth()

    def get_data_response(self, url):
        data_response = self._send_request(url)
        return json.loads(data_response.text)

    def _send_request(self, url):
        authObj = self.auth_singleton
        response = requests.get(url, headers=authObj.get_data_header())
        if response.status_code == 200:
            return response
        # 非預期情況
        else:
            log_root = Path('./log')
            log_root.mkdir(exist_ok=True)

            # 寫log檔
            res = {
                'status_code': response.status_code,
                'reason': response.reason,
                'text': response.text
            }
            dateFormat = r"%Y-%m-%dT%H-%M-%S%z"
            nowStr = datetime.strftime(datetime.now(), dateFormat)
            jsonStr = json.dumps(res)
            log_file = log_root / Path(f'{nowStr}_errLog.txt')
            log_file.write_text(jsonStr)
            print(f'{nowStr} send request發生error')

            raise ValueError(
                f"send request發生error，log path: {log_file.resolve()}")

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
