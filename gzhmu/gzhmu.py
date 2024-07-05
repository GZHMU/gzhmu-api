import re
import base64
from io import BytesIO
from typing import Union, Optional
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

import requests
import numpy as np
from Crypto.Cipher import AES
from PIL import Image

from .captcha import recognize


class InvalidUsernameException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidPasswordException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class EmptyUsernameException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class EmptyPasswordException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class FailedToGetCaptchaImage(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class LoginFailedException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class LoginFailedMaxRetriesException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class IncorrectCredentialException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class IncorrectVerificationCodeException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    
class UsernameNotExistsException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class OnCampusNetworkException(Exception):
    def __init__(self, *args):
        if len(args) == 0:
            msg = 'you are on campus network, there is no need to use Web VPN'
            super().__init__(msg)
        else:
            super().__init__(*args)


class NotOnCampusNetworkException(Exception):
    def __init__(self, *args):
        if len(args) == 0:
            msg = 'you are not on campus network, please connect to the campus network or use Web VPN'
            super().__init__(msg)
        else:
            super().__init__(*args)


class Contact:
    def __init__(self, phone: str, email: str = None):
        self.phone = phone
        self.email = email

    def __repr__(self):
        return '%s.%s(phone=%s, email=%s)' % (__name__, 
                                              Contact.__name__, 
                                              repr(self.phone), 
                                              repr(self.email))


class Gzhmu:
    """To log in websites of GMU and access intranet resources with ease.

    Features:
    1.Bypass CAPTCHA with high accuracy.
    2.Get user contact with username.
    3.Web VPN supported.
    4.Proxy supported.

    Note:
    This class is thread unsafe. Don't manipulate a same instance 
    among different threads, which may cause unexpected result.

    Get contact:

        >>> from gzhmu import Gzhmu
        >>> username = 'xxxxxxxxxx'
        >>> contact = Gzhmu.get_contact(username)
        >>> print('phone:', contact.phone)
        >>> print('email:', contact.email)

    Log in the portal and get timetable without web VPN:

        >>> from gzhmu import Gzhmu
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxx'
        >>> gmu = Gzhmu(username, password)
        >>> gmu.login()
        True
        >>> url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
        >>> resp = gmu.get(url)
        >>> with open('timetable.html', 'wb') as fp:
        ...     fp.write(resp.content)
        22300

    Log in the protal and get timetable with web VPN:

        >>> from gzhmu import WebVPN
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxx'
        >>> vpn = WebVPN(username, password)
        >>> # gmu = Gzhmu(username, password, webvpn=True)  # An alternative way.
        >>> vpn.login()
        True
        >>> url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
        >>> resp = vpn.get(url)
        >>> with open('timetable.html', 'wb') as fp:
        ...     fp.write(resp.content)
        22300

    Log in the protal and get timetable with web VPN and proxies:

        >>> from gzhmu import WebVPN
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxx'
        >>> proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
        >>> vpn = WebVPN(username, password, proxies=proxies)
        >>> # gmu = Gzhmu(username, password, webvpn=True, proxies=proxies)  # An alternative way.
        >>> vpn.login()
        True
        >>> url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
        >>> resp = vpn.get(url)
        >>> with open('timetable.html', 'wb') as fp:
        ...     fp.write(resp.content)
        22300

    :param username: The username to log in the portal.
    :param password: The password to log in the protal.
    :param webvpn: Whether to use web VPN.
    :param proxies: Use a proxy for every individual requests.
        See `https://docs.python-requests.org/en/latest/user/advanced/#proxies` in detail.
    :param timeout: Timeout for every individual requests.
    """

    key = b'wrdvpnisthebest!'
    iv = b'wrdvpnisthebest!'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5410.0 Safari/537.36',
    }

    def __init__(self, username: Optional[Union[None, str, int]] = None, 
                 password: Optional[Union[None, str]] = None, 
                 webvpn: Optional[bool] = False, 
                 proxies: Optional[Union[None, dict]] = None, 
                 timeout: Optional[Union[int ,float]] = 10):
        if username is not None:
            self.set_username(username)
        else:
            self.__username = None
        if password is not None:
            self.set_password(password)
        else:
            self.__password = None

        self.__webvpn = bool(webvpn)

        if proxies is not None and isinstance(proxies, dict):
            self.__proxies = proxies
        else:
            self.__proxies = None
        self.__timeout = float(timeout)

        self.__session = requests.session()
        self.__ticket = None
        self.__access_token = None

    @staticmethod
    def is_valid_username(username: Union[str, int]) -> bool:
        """Check if a username is valid.

        :param useranme: The username to check.
        :returns The result show that whether the username is valid.
        """
        return (isinstance(username, int) or \
               isinstance(username, str)) and \
               re.match(r'[0-9]{10}', str(username)) is not None
 
    @staticmethod
    def is_valid_password(password: str) -> bool:
        """Check if a password is valid.

        :param password: The password to check.
        :returns The result show that whether the password is valid.
        """
        return isinstance(password, str) and len(password) >= 8

    @staticmethod
    def is_on_campus_network(**kwargs) -> bool:
        """Check whether you are using campus network.

        :param kwargs: Argumenets for requests.request method.
        :returns True if you are using campus network, or False if you are not.
        """
        url = 'https://portal.gzhmu.edu.cn/portal'
        response = requests.get(url, allow_redirects=False, **kwargs)
        return not (response.status_code == requests.codes.FOUND and \
                    response.headers.get('Location') == 'https://webvpn.gzhmu.edu.cn/https/77726476706e69737468656265737421e0f85388263c2657640084b9d6502720b7aa6c/portal')

    @staticmethod
    def __get_execution(html: str, formid: str) -> str:
        """Get the value of a label named 'execution' from a specific form tag in HTML.

        The execution is in one of the form tags in an HTML text, 
        which is necessary to Gzhmu.login method.

        :param html: The HTML plain text.
        :param formid: To determine which form tag to get execution value from.
        :return The value of the specified execution.
        """
        pattern = 'form method="post" id="%s"' % formid
        index = html.find(pattern)
        if index < 0:
            return None
        index += len(pattern)
        pattern = 'name="execution" value="'
        start = html.find(pattern, index) + len(pattern)
        end = html.find('"', start)
        return html[start:end]

    @staticmethod
    def encrypt_host(host: str) -> str:
        """Encrypt a hostname.

        Necessary for Gzhmu.encrypt_url method.
        e.g. convert `jwgl.gzhmu.edu.cn` to
        `77726476706e69737468656265737421fae0469069377258731dc7a99c406d36d6`

        :param host: Hostname to encrypt.
        :returns An encrypted hostname.
        """
        cipher = AES.new(Gzhmu.key, AES.MODE_CFB, iv=Gzhmu.iv, segment_size=128)
        decrypted = cipher.encrypt(host.encode())
        return Gzhmu.iv.hex() + decrypted.hex()

    @staticmethod
    def decrypt_host(encrypted_host: str) -> str:
        """Decrypt a hostname.

        Reverse of Gzhmu.encrypt_host method.
        e.g. convert `77726476706e69737468656265737421fae0469069377258731dc7a99c406d36d6`
        to `jwgl.gzhmu.edu.cn`

        :param encrypted_host: The encrypted hostname.
        :returns An decrypted hostname.
        """
        cipher = AES.new(Gzhmu.key, AES.MODE_CFB, iv=Gzhmu.iv, segment_size=128)
        iv_hex = Gzhmu.iv.hex()
        if encrypted_host.startswith(iv_hex):
            encrypted_host = encrypted_host[len(iv_hex):]
        host = cipher.decrypt(bytes.fromhex(encrypted_host))
        return host.decode('utf-8')

    @staticmethod
    def encrypt_url(url: str) -> str:
        """Encrypt a URL.

        Usually used to convert a intranet URL into a web VPN URL.
        e.g. encrypt `http://jwgl.gzhmu.edu.cn/jsxsd/` will be converted to 
        `https://webvpn.gzhmu.edu.cn/http/77726476706e69737468656265737421fae0469069377258731dc7a99c406d36d6/jsxsd/`.

        :param url: The URL to encrypt.
        :returns An encrypted URL.
        """
        parsed_result = urlparse(url)
        protocol = parsed_result.scheme
        host = parsed_result.hostname
        port = parsed_result.port

        encrypted_host = Gzhmu.encrypt_host(host)
        path = '/'.join(['/'+protocol+('-'+str(port) if port else ''), 
                         encrypted_host])
        path += parsed_result.path
        url = urlunparse(('https', 'webvpn.gzhmu.edu.cn', path) + parsed_result[3:])
        return url

    @staticmethod
    def decrypt_url(encrypted_url: str) -> str:
        """Decrypt the URL.

        Reverse of Gzhmu.encrypt_url method. Convert a 
        web VPN URL to an intranet URL, e.g. convert 
        `https://webvpn.gzhmu.edu.cn/http/77726476706e69737468656265737421fae0469069377258731dc7a99c406d36d6/jsxsd/`
        to `http://jwgl.gzhmu.edu.cn/jsxsd/`.

        :param encrypted_url: The URL to decrypt.
        :returns A decrypted URL.
        """
        webvpn_url = 'https://webvpn.gzhmu.edu.cn'
        if not encrypted_url.startswith(webvpn_url):
            return
        parsed_url = urlparse(encrypted_url)
        end_of_protocol = parsed_url.path.find('/', 1)
        if end_of_protocol == -1:
            return
        end_of_encrypted_host = parsed_url.path.find('/', end_of_protocol+1)
        if end_of_encrypted_host == -1:
            return

        splited = parsed_url.path[1:end_of_protocol].split('-')
        if len(splited) == 1:
            protocol = splited[0]
            port = ''
        else:
            protocol, port = splited
        encrypted_host = parsed_url.path[end_of_protocol+1:end_of_encrypted_host]
        host = Gzhmu.decrypt_host(encrypted_host)
        netloc = host + (':'+port if len(port) > 0 else '')
        path = parsed_url.path[end_of_encrypted_host:]
        url = urlunparse((protocol, netloc, path) + parsed_url[3:])
        return url

    @staticmethod
    def get_contact(username: Union[str, int], 
                    webvpn: Optional[bool] = False, 
                    **kwargs) -> Contact:
        """Get the contact of a specific user.

        :param username: Specify a username.
        :param webvpn: Whether to use web VPN, True to use web VPN.
        :param kwargs: Arguments for requests.request method.
        :returns A Contact object.
        """
        if not Gzhmu.is_valid_username(username):
            raise InvalidUsernameException(username)

        url = 'https://sso.gzhmu.edu.cn/cas/login'
        if webvpn:
            url = Gzhmu.encrypt_url(url)
        gmu = Gzhmu(username, webvpn=webvpn)
        response = gmu.get(url, **kwargs)

        data = {
            'execution': Gzhmu.__get_execution(response.text, 'passwordManagementForm'),
            '_eventId': 'customResetPassword'
        }
        response = gmu.post(url, data=data, **kwargs)

        data = {
            'username': username,
            'captcha': gmu.bypass_captcha(),
            'execution': Gzhmu.__get_execution(response.text, 'resetPasswordForm'),
            '_eventId': 'submit',
            'submit': None
        }
        response = gmu.post(url, data=data, **kwargs)
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

    def get_username(self) -> str:
        """Get the current username.

        :returns A username.
        """
        return self.__username

    def get_password(self) -> str:
        """Get the current password.

        :returns A password.
        """
        return self.__password

    def set_username(self, username: Union[str, int]):
        """Set a username.

        :param username: A username to set.
        """
        if not Gzhmu.is_valid_username(username):
            raise InvalidUsernameException()
        self.__username = str(username)

    def set_password(self, password: str):
        """Set a password.

        :param password: A password to set.
        """
        if not Gzhmu.is_valid_password(password):
            raise InvalidPasswordException()
        self.__password = str(password)

    def get_session(self) -> requests.Session:
        """Get the session object for each individual requests.

        :returns A requests.Session object.
        """
        return self.__session

    def is_webvpn(self) -> bool:
        """Check if web VPN is enabled.

        :returns True if web VPN is currently enabled or False if disabled.
        """
        return self.__webvpn

    def set_webvpn(self, state: bool):
        """Set whether to use web VPN or not.

        :param state: True to enable web VPN or False to disable.
        """
        self.__webvpn = bool(state)

    def get_proxies(self) -> dict:
        """Get the currently in use proxies for each individual requests.

        :returns The proxies.
        """
        return self.__proxies

    def set_proxies(self, proxies: dict):
        """Set the proxies for each individual requests.

        See `https://docs.python-requests.org/en/latest/user/advanced/#proxies` for details.

        :param proxies: The proxies to use.
        """
        if isinstance(proxies, dict):
            self.__proxies = proxies

    def get_login_html(self, service: Optional[str] = 'https://portal.gzhmu.edu.cn/portal/login/') -> str:
        """Get the login HTML.

        :param service: The service URL which is about to be authorized.
        :returns The HTML text.
        """
        url = 'https://sso.gzhmu.edu.cn/cas/login?service=' + service
        response = self.get(url)
        return response.text

    def get_captcha_img(self) -> bytes:
        """Get the CAPTCHA image.

        :returns The CAPTCHA image in binary and in PNG format.
        """
        url = 'https://sso.gzhmu.edu.cn/cas/captcha'
        response = self.get(url)
        result = response.json()
        error_code = result.get('errorCode')
        error_message = result.get('errorMessage')
        if error_code != 'success' and error_message != 'success':
            raise FailedToGetCaptchaImage('errorCode "%s", errorMessage "%s"' % (error_code, error_message))
        data = result['data']
        return base64.b64decode(data[data.index(',')+1:])

    def bypass_captcha(self) -> int:
        """Bypass the captcha.

        Get the CAPTCHA image and recognize it, then get the verification code.

        :returns The verification code.
        """
        captcha_bytes = self.get_captcha_img()
        image = Image.open(BytesIO(captcha_bytes))
        captcha_array = np.array(image)
        captcha_result = recognize(captcha_array)
        return captcha_result

    def get_access_token(self) -> Union[None, str]:
        """Get the access token.

        Get the access token which is necessary for Gzhmu.logout method.

        :returns A access token when succeed or None when fail.
        """
        if self.__ticket is None:
            return

        if self.__access_token is not None:
            return self.__access_token

        url = 'https://portal.gzhmu.edu.cn/portal/login/config.js'
        response = self.get(url)
        text = response.content.decode('utf-8')
        client_id = re.search(r'CLIENT_ID:\s*?\'(\w+)\'', text).group(1)
        client_secret = re.search(r'CLIENT_SECRET:\s*?\'(\w+)\'', text).group(1)

        data = {
            "ticket": self.__ticket,
            "casServerUrl": "https://sso.gzhmu.edu.cn/cas",
            "pgtUrl": "",
            "serviceUrl": "https://portal.gzhmu.edu.cn/portal/login/"
        }
        url = 'https://portal.gzhmu.edu.cn/qzbps/oauth2/v3/sso/login/cas10/apply'
        response = self.post(url, json=data)
        login_state = response.json()['data']

        data = {
            'client_id': client_id,
            'login_state': login_state
        }
        url = 'https://portal.gzhmu.edu.cn/qzbps/oauth2/v3/authorize/apply'
        response = self.post(url, json=data)
        authorize_code = response.json()['data']

        data = {
            'client_id': client_id,
            'authorize_code': authorize_code,
            'client_secret': client_secret,
            'grant_type': 'authorization_code'
        }
        url = 'https://portal.gzhmu.edu.cn/qzbps/oauth2/v3/authentication/apply'
        response = self.post(url, json=data)
        json_data = response.json()

        self.__access_token = json_data['data']['access_token']
        return self.__access_token

    def login(self, service: Optional[str] = 'https://portal.gzhmu.edu.cn/portal/login/') -> str:
        """Log in the portal and authorize the specific service.

        :param service: Set the URL of the service to authorize, 
            so that you can access the resources of the service after login.
        :returns A URL that you can use to visit the service on browser.
        """
        if self.__username is None:
            raise EmptyUsernameException()
        if self.__password is None:
            raise EmptyPasswordException()

        is_on_campus_network = Gzhmu.is_on_campus_network()
        if is_on_campus_network and self.__webvpn:
            raise OnCampusNetworkException()
        if not is_on_campus_network and not self.__webvpn:
            raise NotOnCampusNetworkException()

        query = {'service': service}
        login_url = 'https://sso.gzhmu.edu.cn/cas/login?' + urlencode(query)

        login_html = self.get_login_html(service)
        execution = Gzhmu.__get_execution(login_html, 'fm1')

        # Logged in already.
        if execution is None:
            # Authorizate specific service.
            response = self.get(login_url, allow_redirects=False)
            return response.url

        captcha_result = self.bypass_captcha()
        # Post login form data
        formdata = {
            'username': self.__username,
            'password': self.__password,
            'captcha': captcha_result,
            '_eventId': 'submit',
            'geolocation': '',
            'execution': execution,
        }
        response = self.post(login_url, data=formdata, allow_redirects=self.__webvpn)

        # Check login result
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

        # Authorize Web VPN
        if self.__webvpn:
            response = self.get(response.url, allow_redirects=False)
            webvpn_login_url = response.headers['Location']
            self.get(response.url)
            response = self.get(login_url, allow_redirects=False)
 
        # Get login ticket
        location = None
        is_first_ticket = True
        while response.status_code in [requests.codes.FOUND, 
                                       requests.codes.MOVED_PERMANENTLY]:
            location = response.headers['Location']
            parsed_url = urlparse(response.url)
            parsed_location = urlparse(location)
            if parsed_location.netloc == '':
                location = urlunparse(parsed_url[:2]+parsed_location[2:])

            ticket = parse_qs(parsed_location.query).get('ticket')
            if ticket is not None and is_first_ticket:
                self.__ticket = ticket[0]
                is_first_ticket = False
            response = self.get(location, allow_redirects=False)

        if response.status_code not in [requests.codes.OK, 
                                        requests.codes.FOUND, 
                                        requests.codes.MOVED_PERMANENTLY]:
            raise LoginFailedException('unknow failure, alert message not found')

        if self.__webvpn:
            return webvpn_login_url
        else:
            return location

    def logout(self):
        """Log out the account."""
        if self.__webvpn is True:
            url = 'https://webvpn.gzhmu.edu.cn/logout'
            self.get(url)
            self.__ticket = None
            self.__access_token = None
            self.__session.cookies.clear()
            return

        if self.__ticket is None:
            return

        access_token = self.get_access_token()
        url = 'https://portal.gzhmu.edu.cn/qzbps/oauth2/v3/user/logout?access_token=%s' % access_token
        self.post(url)

        url = 'https://sso.gzhmu.edu.cn/cas/logout?service=https://portal.gzhmu.edu.cn/portal/home/'
        self.get(url)

        self.__ticket = None
        self.__access_token = None
        self.__session.cookies.clear()

    def request(self, method: str, url: str, 
                use_encrypt: Optional[Union[None, bool]] = None, 
                **kwargs) -> requests.Response:
        """Send a request.

        After login, you can access the resources on the campus network with this method.

        If use_encrypt is True, url will be encrypted using Gzhmu.encrypt_url 
        method, e.g. `http://jwgl.gzhmu.edu.cn/jsxsd/` will be converted to 
        `https://webvpn.gzhmu.edu.cn/http/77726476706e69737468656265737421fae0469069377258731dc7a99c406d36d6/jsxsd/`.
        If use_encrypt is False, url won't be encrypted and remainds the same.

        NOTE: But if use_encrypt is None, then the behavior is up to the url.
        When use_encrypt is None, if the network location of url is `webvpn.gzhmu.edu.cn`, 
        the url won't be encrypted, otherwise will be encrypted.

        :param method: The request method.
        :param url: The URL to request.
        :param use_encrypt: Determinte whether to use URL encryption.
        :param kwargs: Argumenets for requests.request method.
        :returns A requests.Response object.
        """
        if use_encrypt is None:
            if not urlparse(url).hostname == 'webvpn.gzhmu.edu.cn' \
                    and self.__webvpn:
                url = Gzhmu.encrypt_url(url)
        elif use_encrypt:
            url = Gzhmu.encrypt_url(url)
        if kwargs.get('headers') is None:
            kwargs['headers'] = Gzhmu.headers
        if kwargs.get('timeout') is None:
            kwargs['timeout'] = self.__timeout
        if kwargs.get('proxies') is None:
            kwargs['proxies'] = self.__proxies
        return self.__session.request(method, url, **kwargs)

    def get(self, url: str, 
            use_encrypt: Optional[Union[None, bool]] = None, 
            **kwargs) -> requests.Response:
        """Send a GET request.

        See the Gzhmu.request method for more details.
        """
        return self.request('GET', url, use_encrypt, **kwargs)

    def post(self, url: str, 
             use_encrypt: Optional[Union[None, bool]] = None, 
             **kwargs) -> requests.Response:
        """Send a POST request.

        See the Gzhmu.request method for more details.
        """
        return self.request('POST', url, use_encrypt, **kwargs)


class WebVPN(Gzhmu):
    """Gzhmu with Web VPN.

    Alternative for Gzhmu(username, password, webvpn=True)

    :param username: The username to log in the portal.
    :param password: The passwrod to log in the portal.
    :param proxies: Use a proxy for every individual requests.
        See `https://docs.python-requests.org/en/latest/user/advanced/#proxies` in detail.
    """
    def __init__(self, username: Optional[Union[None, str, int]] = None, 
                 password: Optional[Union[None, str]] = None, 
                 proxies: Optional[Union[None, dict]] = None):
        super().__init__(username, password, webvpn=True, proxies=proxies)
