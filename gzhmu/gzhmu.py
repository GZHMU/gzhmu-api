import re
import base64
import urllib
from io import BytesIO

import requests
import numpy as np
from Crypto.Cipher import AES
from PIL import Image

from .captcha import recognize


class InvalidUsernameException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidPasswordException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EmptyUsernameException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EmptyPasswordException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedToGetCaptchaImage(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LoginFailedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LoginFailedMaxRetriesException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IncorrectCredentialException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IncorrectVerificationCodeException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    
class UsernameNotExistsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class OnCampusNetworkException(Exception):
    def __init__(self, *args: object) -> None:
        if len(args) == 0:
            msg = 'you are on campus network, there is no need to use Web VPN'
            super().__init__(msg)
        else:
            super().__init__(*args)


class NotOnCampusNetworkException(Exception):
    def __init__(self, *args: object) -> None:
        if len(args) == 0:
            msg = 'you are not on campus network, please connect to the campus network or use Web VPN'
            super().__init__(msg)
        else:
            super().__init__(*args)


class Contact:
    def __init__(self, phone: str, email: str = None) -> None:
        self.phone = phone
        self.email = email

    def __repr__(self):
        return '%s.%s(phone=%s, email=%s)' % (__name__, Contact.__name__, repr(self.phone), repr(self.email))


class Gzhmu:
    """To log in websites of Guangzhou Medical University autometically

    Features:
    1.Bypass captcha with high accuracy
    2.Get user contact with username
    3.Web VPN supported

    Caution:
    1.This class is thread unsafe. Don't manipulate a same instance 
    among different threads, which may cause unexpected result.

    Examples:
    from gzhmu import Gzhmu
    username = 'xxxxxxxxxx'
    password = 'xxxxxxxx'

    # login on campus network
    gmu = Gzhmu(username, password)
    gmu.login()

    # login with Web VPN
    gmu = Gzhmu(username, password, webvpn=True)
    gmu.login()

    # after logging in, you can use the "request" method
    # to authorize and access other websites on GMU intranet
    # e.g. https://jwgl.gzhmu.edu.cn/jsxsd
    resp = gmu.get('https://jwgl.gzhmu.edu.cn/jsxsd', headers=Gzhmu.headers)

    # get user contact
    contact = Gzhmu.get_user_contact(username)
    print('phone:', contact.phone)
    print('email:', contact.email)
    """

    protocol = 'https'
    sso_host = 'sso.gzhmu.edu.cn'
    sso_login_path = '/cas/login'
    sso_logout_path = '/qzbps/oauth2/v3/user/logout'
    sso_login_url = protocol + '://' + sso_host + sso_login_path
    sso_logout_url = protocol + '://' + sso_host + sso_logout_path

    webvpn_host = 'webvpn.gzhmu.edu.cn'
    webvpn_url = protocol + '://' + webvpn_host
    key = b'wrdvpnisthebest!'
    iv = b'wrdvpnisthebest!'

    request_timeout = 10

    max_login_retry = 10

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5410.0 Safari/537.36',
    }

    def __init__(self, username=None, password=None, webvpn=False):
        if username is not None:
            self.set_username(username)
        else:
            self.__username = None
        if password is not None:
            self.set_password(password)
        else:
            self.__password = None

        self.__webvpn = bool(webvpn)
        self.__login_retry_count = 0
        self.__session = requests.session()

    @staticmethod
    def is_valid_username(username):
        return (isinstance(username, int) or isinstance(username, str)) and re.match(r'[0-9]{10}', str(username)) is not None
 
    @staticmethod
    def is_valid_password(password):
        return isinstance(password, str) and len(password) >= 8

    @staticmethod
    def is_on_campus_network():
        url = 'https://portal.gzhmu.edu.cn/portal'
        response = requests.get(url, headers=Gzhmu.headers, allow_redirects=False, timeout=Gzhmu.request_timeout)
        return not (response.status_code == requests.codes.FOUND and response.headers.get('Location') == 'https://webvpn.gzhmu.edu.cn/https/77726476706e69737468656265737421e0f85388263c2657640084b9d6502720b7aa6c/portal')

    @staticmethod
    def get_captcha_img(session, webvpn=False):
        url = 'https://sso.gzhmu.edu.cn/cas/captcha'
        if webvpn:
            url = Gzhmu.get_encrypted_url(url)
        response = session.get(url, headers=Gzhmu.headers, timeout=Gzhmu.request_timeout)
        result = response.json()
        error_code = result.get('errorCode')
        error_message = result.get('errorMessage')
        if error_code != 'success' and error_message != 'success':
            raise FailedToGetCaptchaImage('errorCode "%s", errorMessage "%s"' % (error_code, error_message))

        data = result['data']
        return base64.b64decode(data[data.index(',')+1:])

    @staticmethod
    def bypass_captcha(session, webvpn=False):
        captcha_bytes = Gzhmu.get_captcha_img(session, webvpn=webvpn)
        image = Image.open(BytesIO(captcha_bytes))
        captcha_array = np.array(image)
        captcha_result = recognize(captcha_array)
        return captcha_result

    @staticmethod
    def __get_execution(html, formid):
        pattern = 'form method="post" id="%s"' % formid
        index = html.find(pattern)
        if index < 0:
            raise Exception('failed to get execution of form with id %s' % formid)
        index += len(pattern)
        pattern = 'name="execution" value="'
        start = html.find(pattern, index) + len(pattern)
        end = html.find('"', start)
        return html[start:end]

    @staticmethod
    def encrypt_host(host):
        cipher = AES.new(Gzhmu.key, AES.MODE_CFB, iv=Gzhmu.iv, segment_size=128)
        decrypted = cipher.encrypt(host.encode())

        return Gzhmu.iv.hex() + decrypted.hex()

    @staticmethod
    def get_encrypted_url(url):
        parsed_result = urllib.parse.urlparse(url)
        protocol = parsed_result.scheme
        host = parsed_result.hostname
        port = parsed_result.port
        path_and_query = parsed_result.path + ('?' + parsed_result.query if parsed_result.query else '')

        encrypted_host = Gzhmu.encrypt_host(host)

        return '/'.join([Gzhmu.webvpn_url, protocol+('-'+str(port) if port else ''), encrypted_host]) + path_and_query

    @staticmethod
    def get_user_contact(username, webvpn=False):
        if not Gzhmu.is_valid_username(username):
            raise InvalidUsernameException(username)

        url = 'https://sso.gzhmu.edu.cn/cas/login'
        if webvpn:
            url = Gzhmu.get_encrypted_url(url)

        session = requests.session()
        response = session.get(url, headers=Gzhmu.headers, timeout=Gzhmu.request_timeout)

        data = {
            'execution': Gzhmu.__get_execution(response.text, 'passwordManagementForm'),
            '_eventId': 'customResetPassword'
        }

        response = session.post(url, data=data, headers=Gzhmu.headers, timeout=Gzhmu.request_timeout)

        data = {
            'username': username,
            'captcha': Gzhmu.bypass_captcha(session, webvpn=webvpn),
            'execution': Gzhmu.__get_execution(response.text, 'resetPasswordForm'),
            '_eventId': 'submit',
            'submit': None
        }

        response = session.post(url, data=data, headers=Gzhmu.headers, timeout=Gzhmu.request_timeout)
        text = response.content.decode('utf-8')

        if '账号不存在' in text:
            raise UsernameNotExistsException()
        
        if '信息缺失，无法重置密码，请联系管理员重置' in text:
            return Contact(None, None)

        pattern = 'id="phone" name="phone" type="hidden" value="'
        start = response.text.find(pattern) + len(pattern)
        if response.text[start] == '"':
            phone = None
        else:
            end = response.text.find('"', start)
            phone = response.text[start:end]

        pattern = 'id="email" name="email" type="hidden" value="'
        start = response.text.find(pattern) + len(pattern)
        if response.text[start] == '"':
            email = None
        else:
            end = response.text.find('"', start)
            email = response.text[start:end]

        return Contact(phone, email)

    def is_webvpn(self):
        return self.__webvpn

    def set_webvpn(self, state):
        self.__webvpn = bool(state)

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def set_username(self, username):
        if not Gzhmu.is_valid_username(username):
            raise InvalidUsernameException()
        self.__username = str(username)

    def set_password(self, password):
        if not Gzhmu.is_valid_password(password):
            raise InvalidPasswordException()
        self.__password = str(password)

    def get_session(self):
        return self.__session

    def get_login_html(self, service='https://portal.gzhmu.edu.cn/portal/login/', webvpn=None):
        url = 'https://sso.gzhmu.edu.cn/cas/login?service=' + service
        if webvpn is None:
            webvpn = self.__webvpn

        if webvpn:
            url = Gzhmu.get_encrypted_url(url)

        response = self.__session.get(url, headers=Gzhmu.headers, timeout=Gzhmu.request_timeout)

        return response.text

    def login(self, username=None, password=None, service='https://portal.gzhmu.edu.cn/portal/login/', webvpn=None):
        if self.__username is None:
            if username is None:
                raise EmptyUsernameException()
            else:
                self.set_username(username)
        if self.__password is None:
            if password is None:
                raise EmptyPasswordException()
            else:
                self.set_password(password)

        if webvpn is None:
            webvpn = self.__webvpn

        is_on_campus_network = Gzhmu.is_on_campus_network()
        if is_on_campus_network and webvpn:
            raise OnCampusNetworkException()
        if not is_on_campus_network and not webvpn:
            raise NotOnCampusNetworkException()

        login_html = self.get_login_html(service, webvpn=webvpn)

        try:
            execution = Gzhmu.__get_execution(login_html, 'fm1')
        except:
            return True

        captcha_result = Gzhmu.bypass_captcha(self.__session, webvpn=webvpn)

        formdata = {
            'username': self.__username,
            'password': self.__password,
            'captcha': captcha_result,
            '_eventId': 'submit',
            'geolocation': '',
            'execution': execution,
        }

        url = Gzhmu.sso_login_url + '?service=' + service
        if webvpn:
            url = Gzhmu.get_encrypted_url(url)

        response = self.__session.post(url, data=formdata, headers=Gzhmu.headers, allow_redirects=webvpn, timeout=Gzhmu.request_timeout)

        html = response.content.decode('utf-8')
        if response.status_code == requests.codes.UNAUTHORIZED:
            alert_pattern = '<div class="alert alert-danger">'
            alert_start = html.find(alert_pattern)
            if alert_start == -1:
                raise LoginFailedException('unknow failure, alert message not found')
            alert_end = response.text.find('</div>', alert_start)
            msg = html[alert_start:alert_end]

            if '用户名或密码错误，请检查后重试！' in msg:
                raise IncorrectCredentialException()
            elif '验证码错误' in msg:
                raise IncorrectVerificationCodeException()

        while response.status_code == requests.codes.FOUND and not webvpn:
            location = response.headers['Location']
            if urllib.parse.urlparse(location).netloc == '':
                location = urllib.parse.urlunparse(urllib.parse.urlparse(response.url)[:2]+urllib.parse.urlparse(location)[2:])

            if 'ticket=ST-' in location:
                service_ticket = location
                break
            response = self.__session.get(location, headers=Gzhmu.headers, allow_redirects=False, timeout=Gzhmu.request_timeout)

        if webvpn:  # authorize Web VPN
            self.__session.get(response.url, headers=Gzhmu.headers, allow_redirects=True, timeout=Gzhmu.request_timeout)

        if response.status_code != requests.codes.OK:
            raise LoginFailedException('unknow failure, alert message not found')

        return True if webvpn else service_ticket

    def request(self, method, url, *args, **kwargs):
        if self.__webvpn:
            url = Gzhmu.get_encrypted_url(url)
        return self.__session.request(method, url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self.request('GET', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.request('POST', url, *args, **kwargs)


class WebVPN(Gzhmu):
    def __init__(self, username=None, password=None):
        super().__init__(username, password, webvpn=True)
