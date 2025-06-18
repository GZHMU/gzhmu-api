"""APIs of the portal and campus network of Guangzhou Medical University.

This package contaning 3 modules which are gzhmu, gmuapi and gmulib. Use these modules to access the campus network resources with ease.

gzhmu.py mainly contains the basic login and web VPN functions.
gmuapi.py contains the interfaces to campus network.
gmulib.py contains the interfaces to access GMU library.

Below are some examples of gzhmu:

    Get contact:

        >>> from gzhmu import Gzhmu
        >>> username = 'xxxxxxxxxx'
        >>> contact = Gzhmu.get_contact(username)
        >>> print('phone:', contact.phone)
        phone: xxx
        >>> print('email:', contact.email)
        email: xxx

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
        ... 
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
        ... 
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
        ... 
        190900

Below are some examples of gmuapi:

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

    Check if MAC address is bound to an account for non-perceptional authentication:

        >>> from gzhmu import checkMacBinding
        >>> mac = 'aabbccddeeff'
        >>> checkMacBinding(mac)
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
        account: xxx
        >>> print('name:', userInfo.name)
        name: xxx
        >>> print('balance:', userInfo.balance, 'Yuan')
        name: xxx Yuan
        >>> print('used flow:', userInfo.use_flow, 'MB')
        used flow: xxx MB
        >>> print('available flow:', userInfo.available_flow, 'MB')
        available flow: xxx MB

Below are some examples of gmulib:

    List all the room names of all the libraries:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> libraries = lib.get_libraries()
        >>> for library in libraries:
        ...     print(library.lib_name)
        ...     for room in library.rooms:
        ...         print('\t', room.room_name)
        ... 

    Get a check-in URL of the specific seat:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> # You can get a room name from the previous example.
        >>> room_name = 'xxx'
        >>> room_list = lib.get_room_with_name(room_name)
        >>> room = room_list[0]
        >>> seat_number = 20
        >>> seat = room.get_seat_with_number(seat_number)
        >>> url = GmuLib.get_check_in_url(seat)
        >>> print(url)
        http://update.unifound.net/wxnotice/s.aspx?c=100492751_Seat_100495246_1EQ

    Get seat information from a check-in URL:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> check_in_url = 'http://update.unifound.net/wxnotice/s.aspx?c=100492751_Seat_100495246_1EQ'
        >>> seat = lib.get_seat_with_check_in_url(check_in_url)
        >>> print('{} {} {}号座'.format(seat.lib_name, seat.room_name, seat.seat_number))

    Get the latest reservation records of the current user:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> user_records = lib.get_reserve_history()
        >>> print('reserve at', 'seat name', 'owner', 'is validated', 'is checked in', 'start', 'end', sep='\t')
        >>> for user_record in user_records:
        ...     reserve_at = user_record.reserve_at.strftime('%Y-%m-%d_%H:%M:%S')
        ...     seat_name = user_record.seat.seat_name
        ...     owner = user_record.owner
        ...     is_validated = user_record.is_validated
        ...     is_checked_in = user_record.is_checked_in
        ...     start = user_record.start.strftime('%Y-%m-%d_%H:%M:%S')
        ...     end = user_record.end.strftime('%Y-%m-%d_%H:%M:%S')
        ...     print(reserve_at, seat_name, owner, is_validated, is_checked_in, start, end, sep='\t')
        ... 

    Get the finished reservation records of the current user in the past three months:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> user_records = lib.get_reserve_history(is_new_record=False)
        >>> print('reserve at', 'seat name', 'owner', 'is validated', 'is checked in', 'is default', 'start', 'end', sep='\t')
        >>> for user_record in user_records:
        ...     reserve_at = user_record.reserve_at.strftime('%Y-%m-%d_%H:%M:%S')
        ...     seat_name = user_record.seat.seat_name
        ...     owner = user_record.owner
        ...     is_validated = user_record.is_validated
        ...     is_checked_in = user_record.is_checked_in
        ...     is_default = user_record.is_default
        ...     start = user_record.start.strftime('%Y-%m-%d_%H:%M:%S')
        ...     end = user_record.end.strftime('%Y-%m-%d_%H:%M:%S')
        ...     print(reserve_at, seat_name, owner, is_validated, is_checked_in, is_default, start, end, sep='\t')
        ... 


    Get the current user information:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> user_info = lib.get_current_user_info()
        >>> print('name:', user_info.name)
        name: xxx
        >>> print('department', user_info.department)
        department: xxx
        >>> print('score:', user_info.score)
        score: 500

    Get the real time seat information:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> library_name = 'xxx'
        >>> library_list = lib.get_library_with_name(library_name)
        >>> library = library_list[0]
        >>> # Get the realtime information of all the seats in the specified library.
        >>> seat_info_list = lib.get_seat_info(library)
        >>> 
        >>> room_name = 'xxx'
        >>> room_list = lib.get_room_with_name(room_name)
        >>> room = room_list[0]
        >>> # Get the realtime information of all the seats in the specified room.
        >>> seat_info_list = lib.get_seat_info(room)
        >>> 
        >>> seat_number = 20
        >>> seat = room.get_seat_with_number(seat_number)
        >>> # Get the realtime information of the specified seat.
        >>> seat_info_list = lib.get_seat_info(seat)
        >>> 
        >>> for seat_info in seat_info_list:
        ...     print('seat name:', seat_info.seat.seat_name)
        ...     print('is open:', seat_info.is_open)
        ...     print('free time:', seat_info.freetime, 'minutes')
        ...     print('reservation records:')
        ...     if len(seat_info.records) > 0:
        ...         print('\t', 'owner', 'is validated', 'start', 'end', sep='\t')
        ...         for record in seat_info.records:
        ...             owner = record.owner
        ...             is_validated = record.is_validated
        ...             start = record.start.strftime('%Y-%m-%d_%H:%M:%S')
        ...             end = record.end.strftime('%Y-%m-%d_%H:%M:%S')
        ...             print('\t', owner, is_validated, start, end, sep='\t')
        ... 

    Get all the reservation records today in all the libraries:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> user_records = lib.get_today_reserve_records()
        >>> for user_record in user_records:
        ...     seat_name = user_record.seat.seat_name
        ...     owner = user_record.owner
        ...     is_validated = user_record.is_validated
        ...     start = user_record.start.strftime('%Y-%m-%d_%H:%M:%S')
        ...     end = user_record.end.strftime('%Y-%m-%d_%H:%M:%S')
        ...     print(seat_name, owner, is_validated, start, end)
        ... 

    Reserve a seat:

        >>> from datetime import datetime, time
        >>> from gzhmu import GmuLib, ReserveConflictException
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> seat_name = 'xxx'
        >>> seat_list = lib.get_seat_with_name(seat_name)
        >>> seat = seat_list[0]
        >>> date = datetime.today().date()  # Set date to today
        >>> start = time(17, 0)  # Set start time to 17:00
        >>> end = time(17, 30)  # Set end time to 17:30
        >>> try:
        ...     res = lib.reserve(seat, date, start, end)
        ...     if res:
        ...         print('success')
        ... except ReserveConflictException as e:
        ...     print('failed to reserve due conflict')
        ...
        success

    Cancel the reservation record:

        >>> from datetime import datetime, time
        >>> from gzhmu import GmuLib, CanNotCancelValidatedReservationException
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> # Get reservation records
        >>> user_records = lib.get_reserve_history()
        >>> # Get the first record
        >>> record = user_records[0]
        >>> print('seat name:', record.seat.seat_name)
        seat name: xxx
        >>> print('start time:', record.start.ctime())
        start time: xxx
        >>> print('end time:', record.end.ctime())
        end time: xxx
        >>> try:
        ...     res = lib.cancel(record)
        ...     if res:
        ...         print('success')
        ... except CanNotCancelValidatedReservationException as e:
        ...     print('cannot cancel a validated reservation, please check in first or try to finish it')
        success

    Check in:

        >>> from datetime import datetime, time
        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> # Get reservation records
        >>> user_records = lib.get_reserve_history()
        >>> for record in user_records:
        ...     # Get the first valid record
        ...     if record.is_validated:
        ...         print('seat name:', record.seat.seat_name)
        ...         print('start time:', record.start.ctime())
        ...         print('end time:', record.end.ctime())
        ...         res = lib.check_in(record)
        ...         if res:
        ...             print('success')
        ...         else:
        ...             print('failed')
        ...         break
        ... 
        success

    Finish reservation:

        >>> from datetime import datetime, time
        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> # Get reservation records
        >>> user_records = lib.get_reserve_history()
        >>> for record in user_records:
        ...     # Get the first valid record
        ...     if record.is_validated:
        ...         print('seat name:', record.seat.seat_name)
        ...         print('start time:', record.start.ctime())
        ...         print('end time:', record.end.ctime())
        ...         res = lib.finish(record)
        ...         if res:
        ...             print('success')
        ...         else:
        ...             print('failed')
        ... 
        success

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
from .gmuapi import balance_cvt, flow_cvt, request_api, loadConfig, login, loadUserInfo, \
                    loadOnlineDevices, unbind, logout, checkMacBinding
from .gmulib import TargetLibraryNotFoundException, TargetRoomNotFoundException, \
                    TargetSeatNotFoundException, NotLoggedInOrLoginExpiredException, \
                    ReserveException, ReserveConflictException, \
                    ReserveLessThan30MinutesException, \
                    CanNotCancelValidatedReservationException, \
                    Seat, Room, Library, Record, UserRecord, PrivateNewUserRecord, \
                    PrivateFinishedRecord, SeatInfo, CurrentUserInfo, GmuLib


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
    'loadConfig',
    'loadUserInfo', 
    'loadOnlineDevices', 
    'unbind', 
    'logout',
    'checkMacBinding',
    'TargetLibraryNotFoundException',
    'TargetRoomNotFoundException',
    'TargetSeatNotFoundException',
    'NotLoggedInOrLoginExpiredException',
    'ReserveException',
    'ReserveConflictException',
    'ReserveLessThan30MinutesException',
    'CanNotCancelValidatedReservationException',
    'Seat',
    'Room',
    'Library',
    'Record',
    'UserRecord',
    'PrivateNewUserRecord',
    'PrivateFinishedRecord',
    'SeatInfo',
    'CurrentUserInfo',
    'GmuLib',
]
