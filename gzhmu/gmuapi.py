import time
import json
from typing import List, Union

import requests


default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5746.284 Safari/537.36'


class IncorrectAccountOrPasswordException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AlreadyLoggedInException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedToGetUserInfoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedToLoadOnlineDevicesException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RequestException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserInfo:
    def __init__(self, account: Union[str, int], 
                 name: str = '', 
                 balance: float = 0, 
                 use_flow: float = 0, 
                 available_flow: float = 0):
        self.account = str(account)
        self.name = str(name)
        self.balance = float(balance)
        self.use_flow = float(use_flow)
        self.available_flow = float(available_flow)

    def __repr__(self):
        return '%s.%s(account=%s, name=%s, balance=%d, use_flow=%d, available_flow=%d)' % (__name__, UserInfo.__name__, repr(self.account), repr(self.name), self.balance, self.use_flow, self.available_flow)


class Device:
    def __init__(self, login_ip: str, mac: str, login_time: int = 0):
        self.login_ip = login_ip
        self.mac = mac.upper()
        self.login_time = login_time

    def __repr__(self):
        return '%s,%s(login_ip=%s, mac=%s, login_time=%d)' % (__name__, Device.__name__, repr(self.login_ip), repr(self.mac), self.login_time)


def balance_cvt(balance: str) -> float:
    """
    Convert balance in format like "0 Yuan" to float
    """

    return float(balance.split()[0])


def flow_cvt(flow: str) -> float:
    """
    Convert flow in format like "780MB" or "15GB" to float in MB
    """

    if flow.endswith('MB'):
        return float(flow[:-2])
    if flow.endswith('GB'):
        return float(flow[:-2]) * 1024
    if flow.endswith('TB'):
        return float(flow[:-2]) * 1048576
    if flow.endswith('PB'):
        return float(flow[:-2]) * 1073741824


def request_api(url, webvpn=None, *args, **kwargs) -> dict:
    if kwargs.get('headers') is None:
        kwargs['headers'] = {'User-Agent': default_user_agent}

    if webvpn is None:
        response = requests.get(url, *args, **kwargs)
    else:
        response = webvpn.get(url, *args, **kwargs)
    if response.status_code < 200 or response.status_code >= 300:
        raise RequestException(response.status_code)

    text = response.content.decode('utf-8')
    if webvpn is not None:
        text = text[text.find('{')+1:text.rfind('}')]
    text = text.strip()[12:-2]

    response_json = json.loads(text)
    return response_json
 

def login(account: Union[str, int], password, *args, **kwargs) -> bool:
    url = 'http://192.168.12.3:801/eportal/portal/login?lang=en&user_account=,0,%s&user_password=%s'
    url = url % (account, password)

    response_json = request_api(url, *args, **kwargs)
    result = response_json.get('result')
    ret_code = response_json.get('ret_code')

    if result == 1:
        return True
    if result == 0:
        if ret_code == 1:
            raise IncorrectAccountOrPasswordException()
        if ret_code == 2:
            raise AlreadyLoggedInException()
    return False


def loadUserInfo(account: Union[str, int], *args, **kwargs) -> UserInfo:
    url = 'http://192.168.12.3:801/eportal/portal/page/loadUserInfo?lang=en&program_index=1&page_index=voRYWy1627029238&wlan_user_ip=&wlan_user_mac=&jsVersion=&user_account=%s'
    url = url % account

    response_json = request_api(url, *args, **kwargs)
    code = response_json.get('code')

    if code == 1:
        user_info = response_json['user_info']
        account = user_info['account']
        name = user_info['name']
        balance = balance_cvt(user_info['balance'])
        use_flow = flow_cvt(user_info['use_flow'])
        available_flow = flow_cvt(user_info['available_flow'])
        userInfo = UserInfo(account, name, balance, use_flow, available_flow)
        return userInfo

    if code == 0:
        raise FailedToGetUserInfoException()



def loadOnlineDevices(account: Union[str, int], *args, **kwargs) -> List[Device]:
    url = 'http://192.168.12.3:801/eportal/portal/page/loadOnlineRecord?lang=en&program_index=1&page_index=voRYWy1627029238&wlan_user_ip=&wlan_user_mac=&start_time=0&end_time=0&start_rn=1&end_rn=5&jsVersion=&user_account=%s'
    url = url % account

    response_json = request_api(url, *args, **kwargs)
    code = response_json.get('code')

    if code == 1:
        records = response_json['records']
        devices = []
        for record in records:
            login_time = time.strptime(record['login_time'], r'%Y-%m-%d %H:%M:%S')
            login_time = time.mktime(login_time)
            device = Device(record['login_ip'], record['mac_address'], login_time)
            devices.append(device)
        return devices

    if code == 0:
        raise FailedToLoadOnlineDevicesException()

     
def unbind(account: Union[str, int], mac: str, *args, **kwargs) -> bool:
    url = 'http://192.168.12.3:801/eportal/portal/mac/unbind?user_account=%s&wlan_user_mac=%s'
    url = url % (account, mac.upper())

    response_json = request_api(url, *args, **kwargs)
    result = response_json.get('result')

    return result == 1


def logout(*args, **kwargs) -> bool:
    url = 'http://192.168.12.3:801/eportal/portal/logout'

    response_json = request_api(url, *args, **kwargs)
    result = response_json.get('result')

    return result == 1
