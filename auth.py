import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

'''
secret.json放TDX所需資料
{
    "app_id": "",
    "app_key": ""
}
'''
API_FILE = 'secret.json'


class Auth():
    def __init__(self) -> None:
        assert Path(API_FILE).exists(), f"必須要有api file"
        with open(API_FILE, "r") as f:
            acc = json.load(f)
            self.app_id = acc["app_id"]
            self.app_key = acc["app_key"]
            self.cached_datetime = None  # 後續判斷是否要取access token用

    def _get_auth_response(self):
        request_data = {
            'content-type': 'application/x-www-form-urlencoded',
            'grant_type': 'client_credentials',
            'client_id': self.app_id,
            'client_secret': self.app_key
        }
        auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        return requests.post(auth_url, request_data)

    def _get_access_token(self):
        response_JSON = json.loads(self._get_auth_response().text)
        return response_JSON.get('access_token')

    def get_data_header(self):
        # TDX 強烈不建議每次呼叫API時都取得access token
        # 但有過期時間86400 = 24小時，tdx建議每6小時取一次
        if self.cached_datetime is None:
            self.cached_datetime = datetime.now()
            self.access_token = self._get_access_token()
            print('取得新token')
        else:
            time_diff = datetime.now() - self.cached_datetime
            past_hour = time_diff.total_seconds() / 3600
            if past_hour > 6:
                self.access_token = self._get_access_token()
                # 更新比對時間
                self.cached_datetime = datetime.now()
                print('超過6小時，取得新token')

        resObj = {
            'authorization': 'Bearer ' + self.access_token,
            # Accept-Encoding在tdx用來壓縮回傳的資料以便減少時間
            # 接受的參數有br和gzip，都是壓縮方法
            # 'br': Brotli algorithm, 'gzip': the Lempel-Ziv coding (LZ77) with a 32-bit CRC.
            'Accept-Encoding': 'gzip'
        }
        return resObj
