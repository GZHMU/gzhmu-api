"""API to campus network of GMU

Use this module to easily log in, log out, unbind devices, query 
user information and get online devices information, with or without
web VPN.

Examples:

    Get user information:

        >>> from gzhmu import loadUserInfo
        >>> account = 'xxxxxxxxxx'
        >>> userInfo = loadUserInfo(account)
        >>> print('account:', userInfo.account)
        account: xxx
        >>> print('name:', userInfo.name)
        name: xxx
        >>> print('balance:', userInfo.balance, 'Yuan')
        balance: xxx Yuan
        >>> print('used flow:', userInfo.use_flow, 'MB')
        used flow: xxx MB
        >>> print('available flow:', userInfo.available_flow, 'MB')
        available flow: xxx MB

    Log in campus network:

        >>> from gzhmu import login
        >>> account = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> login(account, password)

    Get online devices of the specified account:

        >>> from gzhmu import loadOnlineDevices
        >>> account = 'xxxxxxxxxx'
        >>> devices = loadOnlineDevices(account)
        >>> for device in devices:
        ...     print(device.login_ip, device.mac, time.ctime(device.login_time), sep='\t')
        ... 
        
    Unbind a specific device:

        >>> from gzhmu import unbind
        >>> account = 'xxxxxxxxxx'
        >>> mac = 'xxxxxxxxxxxx'
        >>> unbind(account, mac)
        True

    Logout the current device:

        >>> from gzhmu import logout
        >>> logout()
        True

Some APIs in this module, e.g. loadUserInfo, loadOnlineDevices and unbind, 
can be rquested with web VPN by providing a webvpn parameter which is 
an object of WebVPN, for example:

    Get user infomation with web VPN

        >>> from gzhmu import WebVPN, loadUserInfo
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> vpn = WebVPN(username, password)
        >>> res = vpn.login()
        >>> userInfo = loadUserInfo(username, webvpn=vpn)
        >>> print('account:', userInfo.account)
        account: xxx
        >>> print('name:', userInfo.name)
        name: xxx
        >>> print('balance:', userInfo.balance, 'Yuan')
        balance: xxx Yuan
        >>> print('used flow:', userInfo.use_flow, 'MB')
        used flow: xxx MB
        >>> print('available flow:', userInfo.available_flow, 'MB')
        available flow: xxx MB
"""

import time
import json
from typing import List, Union, Optional

import requests


default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5746.284 Safari/537.36'


class IncorrectAccountOrPasswordException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class AlreadyLoggedInException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class FailedToGetUserInfoException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class FailedToLoadOnlineDevicesException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class RequestException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class UserInfo:
    def __init__(self, 
            account: Union[str, int], 
            name: str = '', 
            balance: Optional[float] = 0, 
            use_flow: Optional[float] = 0, 
            available_flow: Optional[float] = 0):
        self.account = str(account)
        self.name = str(name)
        self.balance = float(balance)
        self.use_flow = float(use_flow)
        self.available_flow = float(available_flow)

    def __repr__(self):
        pattern = '%s.%s(account=%s, name=%s, balance=%d, use_flow=%d, available_flow=%d)' 
        return pattern % (__name__, UserInfo.__name__, repr(self.account), 
                          repr(self.name), self.balance, self.use_flow, self.available_flow)


class Device:
    def __init__(self, 
            login_ip: str, mac: str, login_time: Optional[int] = 0):
        self.login_ip = login_ip
        self.mac = mac.upper()
        self.login_time = login_time

    def __repr__(self):
        pattern = '%s.%s(login_ip=%s, mac=%s, login_time=%d)' 
        return pattern % (__name__, Device.__name__, repr(self.login_ip), 
                          repr(self.mac), self.login_time)


def balance_cvt(balance: str) -> float:
    """Convert balance in format like "0 Yuan" to float"""
    return float(balance.split()[0])


def flow_cvt(flow: str) -> float:
    """Convert flow in format like "780MB" or "15GB" to float in MB"""
    if flow.endswith('MB'):
        return float(flow[:-2])
    if flow.endswith('GB'):
        return float(flow[:-2]) * 1024
    if flow.endswith('TB'):
        return float(flow[:-2]) * 1048576
    if flow.endswith('PB'):
        return float(flow[:-2]) * 1073741824


def request_api(url, webvpn=None, **kwargs) -> dict:
    if kwargs.get('headers') is None:
        kwargs['headers'] = {'User-Agent': default_user_agent}

    if webvpn is None:
        response = requests.get(url, **kwargs)
    else:
        response = webvpn.get(url, **kwargs)
    if response.status_code < 200 or response.status_code >= 300:
        raise RequestException(response.status_code)

    text = response.content.decode('utf-8')
    if webvpn is not None:
        text = text[text.find('{')+1:text.rfind('}')]
    text = text.strip()[12:-2]

    response_json = json.loads(text)
    return response_json
 

def login(account: Union[str, int], password: str, webvpn=None, **kwargs) -> bool:
    """Log in to campus network.

    :param account: The account.
    :param password: The password.
    :param webvpn: An object of gzhmu.Gzhmu class. With this argument set, you 
        can query this API via web VPN. But you have to log in the protal first.
    :param kwargs: Arguments for requests.request method.
    :return True if succeed or False if fail.
    """
    url = 'http://192.168.12.3:801/eportal/portal/login?lang=en&user_account=,0,%s&user_password=%s'
    url = url % (account, password)

    response_json = request_api(url, webvpn=webvpn, **kwargs)
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


def loadUserInfo(account: Union[str, int], webvpn=None, **kwargs) -> UserInfo:
    """Get user information of the specified account.

    :param account: The account.
    :param webvpn: An object of gzhmu.Gzhmu class. With this argument set, you 
        can query this API via web VPN. But you have to log in the protal first.
    :param kwargs: Arguments for requests.request method.
    :return An object of UserInfo.
    """
    url = 'http://192.168.12.3:801/eportal/portal/page/loadUserInfo?lang=en&program_index=1&page_index=voRYWy1627029238&wlan_user_ip=&wlan_user_mac=&jsVersion=&user_account=%s'
    url = url % account

    response_json = request_api(url, webvpn=webvpn, **kwargs)
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



def loadOnlineDevices(account: Union[str, int], webvpn=None, **kwargs) -> List[Device]:
    """Get online devices of the specified account.

    :param account: The account.
    :param webvpn: An object of gzhmu.Gzhmu class. With this argument set, you 
        can query this API via web VPN. But you have to log in the protal first.
    :param kwargs: Arguments for requests.request method.
    :return A list of objects of Device.
    """
    url = 'http://192.168.12.3:801/eportal/portal/page/loadOnlineRecord?lang=en&program_index=1&page_index=voRYWy1627029238&wlan_user_ip=&wlan_user_mac=&start_time=0&end_time=0&start_rn=1&end_rn=5&jsVersion=&user_account=%s'
    url = url % account

    response_json = request_api(url, webvpn=webvpn, **kwargs)
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

     
def unbind(account: Union[str, int], mac: str, webvpn=None, **kwargs) -> bool:
    """Unbind an online device of the specified account and MAC address.

    :param account: The account.
    :param mac: A 12 digits hexadecimal number, e.g. 2c549188c9e3.
    :param webvpn: An object of gzhmu.Gzhmu class. With this argument set, you 
        can query this API via web VPN. But you have to log in the protal first.
    :param kwargs: Arguments for requests.request method.
    :return The result whether the unbind is successful.
    """
    url = 'http://192.168.12.3:801/eportal/portal/mac/unbind?user_account=%s&wlan_user_mac=%s'
    url = url % (account, mac.upper())

    response_json = request_api(url, webvpn=webvpn, **kwargs)
    result = response_json.get('result')

    return result == 1


def logout(webvpn=None, **kwargs) -> bool:
    """Logout the current device.

    :param webvpn: An object of gzhmu.Gzhmu class. With this argument set, you 
        can query this API via web VPN. But you have to log in the protal first.
    :param kwargs: Arguments for requests.request method.
    :return The result whether the logout is successful.
    """
    url = 'http://192.168.12.3:801/eportal/portal/logout'

    response_json = request_api(url, webvpn=webvpn, **kwargs)
    result = response_json.get('result')

    return result == 1
