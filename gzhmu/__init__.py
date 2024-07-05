"""APIs of the portal and campus network of Guangzhou Medical University.

Use this module to access the campus network resources with ease.

Below are some examples for gzhmu:

    Get contact:

        >>> from gzhmu import Gzhmu
        >>> username = 'xxxxxxxxxx'
        >>> contact = Gzhmu.get_contact(username)
        >>> print('phone:', contact.phone)
        >>> print('email:', contact.email)

    Log in the portal and get student enrollment status:

        >>> from gzhmu import Gzhmu
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxx'
        >>> gmu = Gzhmu(username, password)
        >>> url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
        >>> res = gmu.login(url)
        >>> url = 'https://jwgl.gzhmu.edu.cn/jsxsd/grxx/xsxx_print.do'
        >>> resp = gmu.post(url)
        >>> with open('student_enrollment_status.xls', 'wb') as fp:
        ...     fp.write(resp.content)
        190900

    Log in the protal and get student enrollment status with web VPN:

        >>> from gzhmu import WebVPN
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxx'
        >>> vpn = WebVPN(username, password)
        >>> # gmu = Gzhmu(username, password, webvpn=True)  # An alternative way.
        >>> url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
        >>> res = vpn.login(url)
        >>> url = 'https://jwgl.gzhmu.edu.cn/jsxsd/grxx/xsxx_print.do'
        >>> resp = vpn.post(url)
        >>> with open('student_enrollment_status.xls', 'wb') as fp:
        ...     fp.write(resp.content)
        190900

    Log in the protal and get student enrollment status with web VPN and proxies:

        >>> from gzhmu import WebVPN
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxx'
        >>> proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
        >>> vpn = WebVPN(username, password, proxies=proxies)
        >>> # vpn = Gzhmu(username, password, webvpn=True, proxies=proxies)  # An alternative way.
        >>> url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
        >>> res = vpn.login(url)
        >>> url = 'https://jwgl.gzhmu.edu.cn/jsxsd/grxx/xsxx_print.do'
        >>> resp = vpn.post(url)
        >>> with open('student_enrollment_status.xls', 'wb') as fp:
        ...     fp.write(resp.content)
        190900

Below are some examples of gmuapi:

    Get user information:

        >>> from gzhmu import loadUserInfo
        >>> account = 'xxxxxxxxxx'
        >>> userInfo = loadUserInfo(account)
        >>> print('account:', userInfo.account)
        >>> print('name:', userInfo.name)
        >>> print('balance:', userInfo.balance)
        >>> print('used flow:', userInfo.use_flow)
        >>> print('available flow:', userInfo.available_flow)

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

    Some APIs in gmuzpi.py, e.g. loadUserInfo, loadOnlineDevices and unbind, 
    can be used with web VPN by providing a webvpn parameter which is 
    an object of WebVPN, for example:

    Get user infomation with web VPN

        >>> from gzhmu import WebVPN, loadUserInfo
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> vpn = WebVPN(username, password)
        >>> res = vpn.login()
        >>> userInfo = loadUserInfo(username, webvpn=vpn)
        >>> print('account:', userInfo.account)
        >>> print('name:', userInfo.name)
        >>> print('balance:', userInfo.balance)
        >>> print('used flow:', userInfo.use_flow)
        >>> print('available flow:', userInfo.available_flow)

"""
from .gzhmu  import InvalidUsernameException, InvalidPasswordException, \
                    EmptyUsernameException, EmptyPasswordException, \
                    FailedToGetCaptchaImage, LoginFailedException, \
                    LoginFailedMaxRetriesException, IncorrectCredentialException, \
                    IncorrectVerificationCodeException, UsernameNotExistsException, \
                    OnCampusNetworkException, NotOnCampusNetworkException, \
                    Contact, Gzhmu, WebVPN
from .gmuapi import IncorrectAccountOrPasswordException, AlreadyLoggedInException, \
                    FailedToGetUserInfoException, FailedToLoadOnlineDevicesException, \
                    RequestException, UserInfo, Device
from .gmuapi import balance_cvt, flow_cvt, request_api, login, loadUserInfo, \
                    loadOnlineDevices, unbind, logout


__all__ = [
    'InvalidUsernameException', 
    'InvalidPasswordException', 
    'EmptyUsernameException', 
    'EmptyPasswordException', 
    'FailedToGetCaptchaImage', 
    'LoginFailedException', 
    'LoginFailedMaxRetriesException', 
    'IncorrectCredentialException', 
    'IncorrectVerificationCodeException', 
    'UsernameNotExistsException', 
    'OnCampusNetworkException', 
    'NotOnCampusNetworkException', 
    'Contact', 
    'Gzhmu', 
    'WebVPN', 
    'IncorrectAccountOrPasswordException', 
    'AlreadyLoggedInException', 
    'FailedToGetUserInfoException', 
    'FailedToLoadOnlineDevicesException', 
    'RequestException', 
    'UserInfo', 
    'Device', 
    'balance_cvt', 
    'flow_cvt', 
    'request_api', 
    'login', 
    'loadUserInfo', 
    'loadOnlineDevices', 
    'unbind', 
    'logout',
]
