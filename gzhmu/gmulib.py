import re
import datetime
from urllib.parse import urlparse, urlencode, quote, unquote
from typing import Optional, Union, List

from .gzhmu import Gzhmu


class TargetLibraryNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class TargetRoomNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class TargetSeatNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class NotLoggedInOrLoginExpiredException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ReserveException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ReserveConflictException(ReserveException):
    def __init__(self, *args):
        super().__init__(*args)


class ReserveLessThan30MinutesException(ReserveException):
    def __init__(self, *args):
        super().__init__(*args)


class Seat:
    """A seat.

    :param & data lib_id: Library ID.
    :param & data lib_name: Library name.
    :param & data room_id: Room ID.
    :param & data room_name: Room name.
    :param & data seat_id: Seat ID.
    :param & data seat_name: Seat name.

    :data seat_number: The seat number in a room.
    """
    def __init__(self, 
            lib_id: int, lib_name: str, 
            room_id: int, room_name: str, 
            seat_id: int, seat_name: str):
        self.lib_id = lib_id
        self.lib_name = lib_name
        self.room_id = room_id
        self.room_name = room_name
        self.seat_id = seat_id
        self.seat_name = seat_name
        self.seat_number = int(re.search(r'\D(\d+)$', seat_name).group(1))

    def __repr__(self):
        return f'{__name__}.{Seat.__name__}(seat_id = {self.seat_id}, seat_name = {repr(self.seat_name)})'


class Room:
    """A room.

    :param & data lib_id: Library ID.
    :param & data lib_name: Library name.
    :param & data room_id: Room ID.
    :param & data room_name: Room name.
    :param & data seats: A list of Seat objects.

    :func get_seat_with_number: Get a Seat object using a seat number.
    """
    def __init__(self, 
            lib_id: int, lib_name: str, 
            room_id: int, room_name: str, 
            seats: List[Seat]):
        self.lib_id = lib_id
        self.lib_name = lib_name
        self.room_id = room_id
        self.room_name = room_name
        self.seats = seats
    
    def get_seat_with_number(self, no: int) -> Seat:
        no = int(no)
        for seat in self.seats:
            if seat.seat_number == no:
                return seat
        raise TargetSeatNotFoundException()

    def __repr__(self):
        return f'{__name__}.{Room.__name__}(room_id = {self.room_id}, room_name = {repr(self.room_name)})'


class Library:
    """A library.

    :param & data lib_id: Library ID.
    :param & data lib_name: Library name.
    :param & data rooms: A list of Room objects in the library.
    """
    def __init__(self, lib_id: int, lib_name: str, rooms: Room):
        self.lib_id = lib_id
        self.lib_name = lib_name
        self.rooms = rooms

    def __repr__(self):
        return f'{__name__}.{Library.__name__}(lib_id = {self.lib_id}, lib_name = {repr(self.lib_name)})'


class Record:
    """Reservation record of a seat.

    :param & data seat: Seat object.
    :param & data accno: Unique ID of the person who reserved the seat.
    :param & data owner: Name of the person who reserved the seat.
    :param & data is_validated: True means the reservation is validated 
        and not finished. False means not validated or finished.
    :param & data title: Description of the usage of the seat.
    :param & data start: The start time of the reservation.
    :param & data end: The end time of the reservation.
    """
    def __init__(self, 
            seat: Seat, accno: int, owner: str, is_validated: bool, 
            title: Union[None, str], start: datetime.datetime, 
            end: datetime.datetime):
        self.seat = seat
        self.accno = accno
        self.owner = owner
        self.is_validated = is_validated
        self.title = title
        self.start = start
        self.end = end

    def __repr__(self):
        return f'{__name__}.{Record.__name__}(owner = {repr(self.owner)}, seat = {repr(self.seat.seat_name)})'


class UserRecord(Record):
    """Public reservation record with reserve_id and reserve_at data.

    :param & data reserve_id: The ID of this reservation record.
    :param & data seat: Seat object.
    :param & data accno: Unique ID of the person who reserved the seat.
    :param & data owner: Name of the person who reserved the seat.
    :param & data is_validated: True means the reservation is validated 
        and not finished. False means not validated or finished.
    :param & data title: Description of the usage of the seat.
    :param & data start: The start time of the reservation.
    :param & data end: The end time of the reservation.
    """
    def __init__(self, reserve_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reserve_id = reserve_id

    def __repr__(self):
        return f'{__name__}.{UserRecord.__name__}(owner = {repr(self.owner)}, seat = {repr(self.seat.seat_name)})'


class PrivateNewUserRecord(UserRecord):
    """Current user new reservation record with reserve_id, reserve_at and is_checked_in data.

    :param & data reserve_id: The ID of this reservation record.
    :param & data reserve_at: The time when reserve the seat.
    :param & data seat: Seat object.
    :param & data accno: Unique ID of the person who reserved the seat.
    :param & data owner: Name of the person who reserved the seat.
    :param & data is_validated: True means the reservation is validated 
        and not finished. False means not validated or finished.
    :param & data is_checked_in: Whether check in or not.
    :param & data title: Description of the usage of the seat.
    :param & data start: The start time of the reservation.
    :param & data end: The end time of the reservation.
    """
    def __init__(self, 
            reserve_id: int, reserve_at: datetime.datetime, 
            seat: Seat, accno: int, owner: str, is_validated: bool, 
            is_checked_in: bool, title: Union[None, str], 
            start: datetime.datetime, end: datetime.datetime):
        super().__init__(reserve_id, seat, accno, owner, is_validated, title, start, end)
        self.reserve_at = reserve_at
        self.is_checked_in = is_checked_in

    def __repr__(self):
        return f'{__name__}.{PrivateNewUserRecord.__name__}(owner = {repr(self.owner)}, seat = {repr(self.seat.seat_name)}, reserve_at = {self.reserve_at.ctime()})'


class PrivateFinishedRecord(Record):
    """Current user finished reservation record.

    :param & data reserve_at: The time when reserve the seat.
    :param & data seat: Seat object.
    :param & data accno: Unique ID of the person who reserved the seat.
    :param & data owner: Name of the person who reserved the seat.
    :param & data is_validated: Always False since it's a finished reservation.
    :param & data is_checked_in: Whether check in or not.
    :param & data is_default: True means not checking in or leaving without 
        checking out. False means have checked in and checked out successfully.
    :param & data title: Description of the usage of the seat.
    :param & data start: The start time of the reservation.
    :param & data end: The end time of the reservation.
    :param & data leave_at: Actual leaving time.
    """
    def __init__(self, 
            reserve_at: datetime.datetime, seat: Seat, accno: int, 
            owner: str, is_validated: bool, is_checked_in: bool, 
            is_default: bool, title: Union[None, str], 
            start: datetime.datetime, end: datetime.datetime, 
            leave_at: datetime.datetime):
        super().__init__(seat, accno, owner, is_validated, title, start, end)
        self.reserve_at = reserve_at
        self.is_validated = is_validated
        self.is_checked_in = is_checked_in
        self.is_default = is_default
        self.leave_at = leave_at

    def __repr__(self):
        return f'{__name__}.{PrivateFinishedRecord.__name__}(owner = {repr(self.owner)}, seat = {repr(self.seat.seat_name)}, reserve_at = {self.reserve_at.ctime()})'


class SeatInfo:
    """Seat information.

    :param & data seat: A Seat object.
    :param & data is_open: True means the seat is open to everyone. False means close.
    :param & data freetime: The remaining available time for using this seat.
    :param & data records: A list of Record objects, specifying the 
        reservation records of the seat.
    """
    def __init__(self, 
            seat: Seat, is_open: bool, freetime: int, records: List[Record]):
        self.seat = seat
        self.is_open = is_open
        self.freetime = freetime
        self.records = records

    def __repr__(self):
        return f'{__name__}.{SeatInfo.__name__}(seat = {repr(self.seat.seat_name)}, is_open = {repr(self.is_open)})'


class CurrentUserInfo:
    """The information of the current user.

    :param & data username: User account.
    :param & data accno: The unique ID of the current user.
    :param & data name: Name of the user.
    :param & data department: The department of the user.
    :param & data score: The remaining credit score.
    """
    def __init__(self, 
            username: str, accno: int, name: str, department: str, score: int):
        self.username = username
        self.accno = accno
        self.name = name
        self.department = department
        self.score = score

    def __repr__(self):
        return f'{__name__}.{CurrentUserInfo.__name__}(username = {repr(self.username)}, name = {repr(self.name)}, department = {repr(self.department)}, score = {self.score})'


class GmuLib(Gzhmu):
    """Interface to library of GMU.

    To log in, query reservation information, reserve a seat, check in, 
    check out and etc.

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

    Get a check in URL of the specific seat:

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

    Get the latest reservation records of the current user:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> user_records = lib.get_reserve_history()
        >>> for record in user_records:
        ...     print(record.reserve_at.ctime(), record.seat.seat_name, record.owner, record.is_open, record.is_checked_in, record.start.ctime(), record.end.ctime(), sep='\t')
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
        >>> seat_info = seat_list[0]
        >>> print('seat name:', seat_info.seat.seat_name)
        seat name: xxx
        >>> print('is open:', seat_info.is_open)
        is open: True
        >>> print('free time:', seat_info.freetime, 'minutes')
        free time: 840 minutes
        >>> for record in seat_info.records:
        ...     print(record.owner, record.is_validated, record.start.ctime(), record.end.ctime(), sep='\t')
        ... 

    Get all the reservation records today in all the libraries:

        >>> from gzhmu import GmuLib
        >>> username = 'xxxxxxxxxx'
        >>> password = 'xxxxxxxxxx'
        >>> lib = GmuLib(username, password)
        >>> res = lib.login()
        >>> records = lib.get_today_reserve_records()
        >>> for record in user_records:
        ...     print(record.seat.seat_name, record.owner, record.is_validated, record.start.ctime(), record.end.ctime())
        ... 

    Reserve a seat:

        >>> from datetime import datetime, time
        >>> from gzhmu import GmuLib
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
        >>> lib.reserve(seat, date, start, end)
        True

    Cancel the reservation record:

        >>> from datetime import datetime, time
        >>> from gzhmu import GmuLib
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
        >>> lib.cancel(record)
        True

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
        ...             print('succeeded')
        ...         else:
        ...             print('failed')
        ...         break
        ... 

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
        ...             print('succeeded')
        ...         else:
        ...             print('failed')
        ... 

    See gzhmu.Gzhmu for more details.

    :param username: The username to log in the portal.
    :param password: The password to log in the protal.
    :param webvpn: Whether to use web VPN or not.
    :param proxies: Use a proxy for every individual requests.
        See `https://docs.python-requests.org/en/latest/user/advanced/#proxies` in detail.
    :param timeout: Timeout for every individual requests.
    """

    LIBRARY_ID_PANYU = 100492446
    LIBRARY_NAME_PANYU = '番禺校区图书馆'
    LIBRARY_ID_YUEXIU = 100492751
    LIBRARY_NAME_YUEXIU = '越秀校区图书馆'

    def __init__(self, 
            username: Optional[Union[None, str, int]] = None, 
            password: Optional[Union[None, str]] = None, 
            webvpn: Optional[bool] = False, 
            proxies: Optional[Union[None, dict]] = None, 
            timeout: Optional[Union[int ,float]] = 10):
        super().__init__(username, password, webvpn, proxies, timeout)
        self.__libraries = None
        self.__user_info = None

    @staticmethod
    def get_check_in_url(seat: Seat) -> str:
        """Get a URL to check in a secific seat.

        :param seat: A Seat object.
        :return A check in URL.
        """
        return f'http://update.unifound.net/wxnotice/s.aspx?c={seat.lib_id}_Seat_{seat.seat_id}_1EQ'

    def login(self):
        """Login library website.

        :return Always True if log in successfully.
        """
        url = 'http://ggyy.gzhmu.edu.cn'
        res = super().login(service=url)
        return res

    def get_libraries(self) -> List[Library]:
        """Get a list of objects of class Library.

        :return A list of Library objects.
        """
        if self.__libraries is not None:
            return self.__libraries
        home_url = 'https://ggyy.gzhmu.edu.cn/clientweb/xcus/ic2/Default.aspx'
        response = self.get(home_url)
        if urlparse(response.url).hostname == 'sso.gzhmu.edu.cn':
            raise NotLoggedInOrLoginExpiredException()
        room_info = re.findall(r'lab_(\d+).+?roomId=(\d+)&roomName=([^"]+)"', 
                               response.text)
        panyu_lib_rooms = []
        yuexiu_lib_rooms = []
        for lib_id, room_id, room_name in room_info:
            query_params = {
                'byType': 'devcls',
                'classkind': 8,
                'display': 'fp',
                'md': 'd',
                'room_id': room_id,
                'purpose': '',
                'selectOpenAty': '',
                'cld_name': 'default',
                'act': 'get_dev_coord',
            }
            url = 'https://ggyy.gzhmu.edu.cn/ClientWeb/pro/ajax/device.aspx?'\
                  + urlencode(query_params)
            response = self.get(url)
            seats = []
            resp_json = response.json()
            ret_code = resp_json['ret']
            if ret_code == 1:
                pass
            elif ret_code == -1:
                raise NotLoggedInOrLoginExpiredException()
            else:
                raise Exception(resp_json['msg'])

            lib_id = int(lib_id)
            room_id = int(room_id)
            room_name = unquote(room_name)

            if lib_id == GmuLib.LIBRARY_ID_PANYU:
                lib_name = GmuLib.LIBRARY_NAME_PANYU
            else:
                lib_name = GmuLib.LIBRARY_NAME_YUEXIU

            for seat_json in response.json()['data']['objs']:
                seat_id = int(seat_json['id'])
                seat_name = seat_json['name']
                seat = Seat(lib_id, lib_name, room_id, room_name, seat_id, seat_name)
                seats.append(seat)

            room = Room(lib_id, lib_name, room_id, room_name, seats)
            if lib_id == GmuLib.LIBRARY_ID_PANYU:
                panyu_lib_rooms.append(room)
            elif lib_id == GmuLib.LIBRARY_ID_YUEXIU:
                yuexiu_lib_rooms.append(room)

        panyu_library = Library(GmuLib.LIBRARY_ID_PANYU, GmuLib.LIBRARY_NAME_PANYU, 
                                panyu_lib_rooms)
        yuexiu_library = Library(GmuLib.LIBRARY_ID_YUEXIU, GmuLib.LIBRARY_NAME_YUEXIU, 
                                 yuexiu_lib_rooms)
        self.__libraries = (panyu_library, yuexiu_library)
        
        return self.__libraries

    def get_library_with_id(self, lib_id: int) -> Library:
        """Get a Library with library ID.

        :param lib_id: The library ID.
        :return A Library object.
        """
        lib_id = int(lib_id)
        for library in self.get_libraries():
            if library.lib_id == lib_id:
                return library
        raise TargetLibraryNotFoundException()

    def get_library_with_name(self, lib_name: str) -> List[Library]:
        """Get a list of Librarys with library name.

        :param lib_name: The library name.
        :return A list of Library objects whose names match 
            with the specified library name.
        """
        libraries = []
        for library in self.get_libraries():
            if library.lib_name == lib_name:
                libraries.append(library)
        return libraries

    def get_room_with_id(self, room_id: int) -> Room:
        """Get a Room with room ID.

        :param room_id: The room ID.
        :return A Room object.
        """
        room_id = int(room_id)
        for library in self.get_libraries():
            for room in library.rooms:
                if room.room_id == room_id:
                    return room
        raise TargetRoomNotFoundException()

    def get_room_with_name(self, room_name: str) -> List[Room]:
        """Get a list of Rooms with with room name.

        :param room_name: The room name.
        :return A list of Room objects whose names match 
            with the specifed room name.
        """
        rooms = []
        for library in self.get_libraries():
            for room in library.rooms:
                if room_name in room.room_name:
                    rooms.append(room)
        return rooms

    def get_seat_with_id(self, seat_id: int) -> Seat:
        """Get a Seat with seat ID.

        :param seat_id: The seat ID.
        :param A Seat object.
        """
        seat_id = int(seat_id)
        for library in self.get_libraries():
            for room in library.rooms:
                for seat in room.seats:
                    if seat.seat_id == seat_id:
                        return seat
        raise TargetSeatNotFoundException()

    def get_seat_with_name(self, seat_name: str) -> List[Seat]:
        """Get a list of seats with seat name.

        :param seat_name: A seat name.
        :return A list of Seat objects whose names match 
            with the specified seat name.
        """
        seats = []
        for library in self.get_libraries():
            for room in library.rooms:
                for seat in room.seats:
                    if seat_name in seat.seat_name:
                        seats.append(seat)
        return seats

    def get_seat_with_check_in_url(self, url: str) -> Seat:
        """Get a Seat object from a check in URL.

        :param url: The URL to check in.
        :return A Seat object.
        """
        result = re.search(r'c=(\d+)_Seat_(\d+)_1EQ', url)
        if result is None:
            raise Exception(f'not a check in URL, "{url}"')
        lib_id = int(result.group(1))
        seat_id = int(result.group(2))
        try:
            library = self.get_library_with_id(lib_id)
            seat = self.get_seat_with_id(seat_id)
            if library.lib_id == seat.lib_id:
                return seat
        except (TargetLibraryNotFoundException, TargetSeatNotFoundException):
            pass
        raise Exception(f'not a valid check in URL, "{url}"')

    def get_seat_info(self, 
            target: Optional[Union[None, Library, Room, Seat]] = None, 
            date: Optional[datetime.date] = None, 
            starttime: Optional[datetime.time] = None, 
            endtime: Optional[datetime.time] = None) -> List[SeatInfo]:
        """Get a list of seat information.

        :param target: To specify the extent of the seats to query. 
            Default is all the seats.
        :param data: Specify the date to query. Should be today 
            or tomorrow. Default is today.
        :param starttime: Specify the start time to query. Default 
            is the current time.
        :param endtime: Specify the end time to query. Default 
            is the library closing time.
        :return A list of SeatInfo objects, containing reservation 
            information of the seat.
        """
        now = datetime.datetime.now()
        if date is None:
            date = now.date()
        if starttime is None:
            starttime = now.time()
        if endtime is None:
            endtime = datetime.time(23, 59)
        formatted_date = date.strftime('%Y-%m-%d')
        formatted_starttime = starttime.strftime('%H:%M')
        formatted_endtime = endtime.strftime('%H:%M')

        query_params = {
            'byType': 'devcls',
            'classkind': 8,
            'display': 'fp',
            'md': 'd',
            'purpose': '',
            'selectOpenAty': '',
            'cld_name': 'default',
            'date': formatted_date,
            'fr_start': formatted_starttime,
            'fr_end': formatted_endtime,
            'act': 'get_rsv_sta',
        }

        if target is None:
            pass
        elif isinstance(target, Seat):
            query_params['dev_id'] = target.seat_id
        elif isinstance(target, Room):
            query_params['room_id'] = target.room_id
        elif isinstance(target, Library):
            query_params['lab_id'] = target.lab_id
        else:
            raise TypeError(f'should be of type None, Library, Room or Seat, but {type(target)} found.')

        url = f'https://ggyy.gzhmu.edu.cn/ClientWeb/pro/ajax/device.aspx?'
        url += urlencode(query_params)
        response = self.get(url)

        resp_json = response.json()
        ret_code = resp_json['ret']
        if ret_code == 1:
            pass
        elif ret_code == -1:
            raise NotLoggedInOrLoginExpiredException()
        else:
            raise Exception(resp_json['msg'])

        seat_info_list = []
        for seat_json in resp_json['data']:
            lab_id = int(seat_json['labId'])
            lab_name = seat_json['labName']
            room_id = int(seat_json['roomId'])
            room_name = seat_json['roomName']
            seat_id = int(seat_json['devId'])
            seat_name = seat_json['devName']
            seat = Seat(lab_id, lab_name, room_id, room_name, seat_id, seat_name)
            if seat_json['state'] is None:
                is_open = seat_json['ops'][0]['state'] == 'open'
            else:
                is_open = seat_json['state'] == 'open'
            freetime = seat_json['freeTime']

            records = []
            for record_json in seat_json['ts']:
                accno = int(record_json['accno'])
                owner = record_json['owner']
                is_validated = record_json['state'] == 'doing'
                title = record_json['title']
                start = datetime.datetime.strptime(record_json['start'], '%Y-%m-%d %H:%M')
                end = datetime.datetime.strptime(record_json['end'], '%Y-%m-%d %H:%M')
                record = Record(seat, accno, owner, is_validated, title, start, end)
                records.append(record)

            seat_info = SeatInfo(seat, is_open, freetime, records)
            seat_info_list.append(seat_info)

        return seat_info_list

    def get_current_user_info(self) -> CurrentUserInfo:
        """Get the information of current user.

        :return A CurrentUserInfo object, containing the 
            information of the current user.
        """
        url = 'https://ggyy.gzhmu.edu.cn/clientweb/xcus/a/center.aspx'
        response = self.get(url)
        accno = re.search(r'acc.accno = "(\d+)";', response.text)
        if accno is None:
            raise NotLoggedInOrLoginExpiredException()
        accno = accno.group(1)
        name = re.search(r'acc.name = "(\S+)";', response.text).group(1)
        department = re.search(r'acc.dept = "(\S+)";', response.text).group(1)
        score = re.search(r'acc.score = "(\d+)";', response.text).group(1)

        user_info = CurrentUserInfo(self.get_username(), accno, name, department, score)
        self.__user_info = user_info
        return user_info

    def get_today_reserve_records(self) -> List[UserRecord]:
        """Get all the not outdated reservation records today.

        :return A list of UserRecord objects that contain a reserve_id.
        """
        url = 'https://ggyy.gzhmu.edu.cn/clientweb/xcus/ic2/index.aspx'
        response = self.get(url)
        start_index = response.text.find('<ul class="dyn_resv">')
        end_index = response.text.find('</ul>', start_index)
        text = response.text[start_index:end_index]
        seat_info_list = self.get_seat_info()
        seat_info_dict = {seat_info.seat.seat_name: seat_info for seat_info in seat_info_list}
        records = []
        for record_raw_text in re.findall(r'<li date=.+?</li>', text):
            reserve_id = int(re.search(r"id='rsv_(\d+?)'", record_raw_text).group(1))
            room_name = re.search(r'<div><div class=.+>(.+?)&nbsp;<span', 
                                  record_raw_text).group(1)
            is_validated = '已生效' in record_raw_text
            start = re.search(r"<li date='([\d\- :]+?)'", record_raw_text).group(1)
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M')
            end = re.search(r' - ([\d\- :]+?)</div></li>', record_raw_text).group(1)
            end = str(start.year) + '-' + end
            end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M')
            seat_info = seat_info_dict[room_name]
            for record in seat_info.records:
                if start == record.start and end == record.end:
                    user_record = UserRecord(reserve_id, seat_info.seat, 
                                             record.accno, record.owner, 
                                             record.is_validated, record.title, 
                                             record.start, record.end)
                    records.append(user_record)
                    break

        return records

    def get_reserve_history(self, is_new_record: bool = True) -> \
            List[Union[PrivateNewUserRecord, PrivateFinishedRecord]]:
        """Get reservation history of current user.

        :param is_new_record: Specify whether to query the latest reservation 
            history or the last 3 months history. Default to True.
        :return A list of PrivateNewUserRecord objects if is_new_record is True.
                Or a list of PrivateFinishedRecord objects if is_new_record is False.
        """
        stat_flag = 'NEW' if is_new_record else 'OVER'
        url = 'https://ggyy.gzhmu.edu.cn/ClientWeb/pro/ajax/center.aspx?act=get_History_resv&StatFlag='
        url += stat_flag
        response = self.get(url)
        resp_json = response.json()
        ret = resp_json['ret']

        if ret == 1:
            pass
        elif ret == -1:
            raise NotLoggedInOrLoginExpiredException()
        else:
            raise Exception(resp_json['msg'])

        msg = resp_json['msg']
        if '没有数据' in msg:
            return []

        records = []
        today_reserve_records = None
        for record_raw_text in re.findall(r'<tbody [\s\S]+?</tbody>', msg):
            reserve_at = re.search(r"date='([\d\- :]+?)'", record_raw_text).group(1)
            reserve_at = datetime.datetime.strptime(reserve_at, '%Y-%m-%d %H:%M')
            is_checked_in = '已签到' in record_raw_text
            title = re.search(r'<h3>(.*?)</h3>', record_raw_text).group(1)
            seat_name = re.search(r'<a>(.+?)</a>', record_raw_text).group(1)
            seat = self.get_seat_with_name(seat_name)[0]
            name = re.search(r'</div</div></td><td>(.+?)</td><td>', 
                                 record_raw_text).group(1)
            start = re.search(r"开始:</span> <span class='text-primary'>([\d\- :]+?)</span>", 
                                  record_raw_text).group(1)
            start = str(reserve_at.year) + '-' + start
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M')
            end = re.search(r"结束:</span> <span class='text-primary'>([\d\- :]+?)</span>", 
                                record_raw_text).group(1)
            end = str(reserve_at.year) + '-' + end
            end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M')

            if self.__user_info is None:
                self.get_current_user_info()
            accno = self.__user_info.accno

            if is_new_record:
                if '未生效' in record_raw_text:
                    is_validated = False
                    reserve_id = int(re.search(r"rsvId='(\d+?)'", record_raw_text).group(1))
                else:
                    is_validated = True
                    reserve_id = re.search(r'pro\.j\.rsv\.finish\((\d+)\);', record_raw_text)
                    if reserve_id is None:
                        if today_reserve_records is None:
                            today_reserve_records = self.get_today_reserve_records()
                        for record in today_reserve_records:
                            if (record.seat.seat_id == seat.seat_id
                                    and record.start == start
                                    and record.end == end):
                                reserve_id = record.reserve_id
                                break
                    else:
                        reserve_id = int(reserve_id.group(1))

                record = PrivateNewUserRecord(reserve_id, reserve_at, seat, 
                                              accno, name, is_validated, 
                                              is_checked_in, title, start, end)

            else:
                leave_at = end
                end = re.search(r"原始结束:</span> <span class='text-primary'>([\d\- :]+?)</span>", 
                                record_raw_text).group(1)
                end = str(reserve_at.year) + '-' + end
                end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M')
                is_validated = False
                is_default = '已违约' in record_raw_text
                record = PrivateFinishedRecord(reserve_at, seat, accno, name, 
                                               is_validated, is_checked_in, 
                                               is_default, title, start, end, 
                                               leave_at)

            records.append(record)
        return records

    def reserve(self, seat: Seat, date: datetime.date, 
            start: datetime.time, end: datetime.time) -> bool:
        """Reserve a specified seat with specified time.

        :param seat: A Seat object designating the seat.
        :param date: The date to reserve, should be today or tomorrow.
        :param start: To specify the start time.
        :param end: To specify the end time.
        :return Whether reserve successfully or not.
        """
        if end.hour * 60 + end.minute - (start.hour * 60 + start.minute) < 30:
            raise ReserveLessThan30MinutesException()

        date_str = date.strftime('%Y-%m-%d')
        start_str = date_str + ' ' + start.strftime('%H:%M')
        start_time = start.hour * 100 + start.minute
        end_str = date_str + ' ' + end.strftime('%H:%M')
        end_time = end.hour * 100 + end.minute

        query_params = {
            'dialogid': '',
            'dev_id': seat.seat_id,
            'lab_id': '',
            'kind_id': '',
            'room_id': '',
            'type': 'dev',
            'prop': '',
            'test_id': '',
            'term': '',
            'number': '',
            'test_name': '',
            'start': start_str,
            'end': end_str,
            'start_time': start_time,
            'end_time': end_time,
            'up_file': '',
            'memo': '',
            'act': 'set_resv',
        }

        url = 'https://ggyy.gzhmu.edu.cn/ClientWeb/pro/ajax/reserve.aspx?'\
              + urlencode(query_params)
        response = self.get(url)
        resp_json = response.json()
        ret = resp_json['ret']
        if ret == 1:
            return True
        elif ret == 0:
            if 'ERRMSG_RESV_CONFLICT' in msg:
                raise ReserveConflictException()
        msg = resp_json['msg']

        ret = response.json()['ret']
        return ret == 1

    def check_in(self, reserve_record: UserRecord) -> bool:
        """Check in the reserved seat.

        :param reserve_record: A UserRecord object specifying the reservation record.
        :return Whether check in successfully or not.
        """
        check_in_url = GmuLib.get_check_in_url(reserve_record.seat)
        response = self.get(check_in_url)
        if '操作成功' in response.text:
            return False
        if response.url == 'https://sso.gzhmu.edu.cn/cas/login?service=http://ggyy.gzhmu.edu.cn/pages/WxSeatSign.aspx':
            raise NotLoggedInOrLoginExpiredException()

        url = 'https://ggyy.gzhmu.edu.cn/Pages/WxSeatSign.aspx?Userin=true'
        response = self.get(url)
        return '签到成功' in response.text

    def cancel(self, reserve_record: UserRecord) -> bool:
        """Cancel the reservation before the start of it."""
        url = f'https://ggyy.gzhmu.edu.cn/ClientWeb/pro/ajax/reserve.aspx?act=del_resv&id={reserve_record.reserve_id}'
        response = self.get(url)
        if '未找到预约' in response.text:
            return False
        resp_json = response.json()
        ret = resp_json['ret']
        if ret == 1:
            return True
        elif ret == -1:
            raise NotLoggedInOrLoginExpiredException()
        else:
            raise Exception(resp_json['ret'])

    def finish(self, reserve_record: UserRecord) -> bool:
        """Finish the reservation after the start of it.

        :param reserve_record: A UserRecord object specifying the reservation record.
        :return Whether finish the reservation successfully or not.
        """
        url = f'https://ggyy.gzhmu.edu.cn/ClientWeb/pro/ajax/reserve.aspx?act=resv_leave&type=2&resv_id={reserve_record.reserve_id}'
        response = self.get(url)
        now = datetime.datetime().now()
        if reserve_record.start > now or reserve_record.end < now:
            return False
        if '获取预约的设备失败' in response.text:
            return False
        resp_json = response.json()
        ret = resp_json['ret']
        msg = resp_json['msg']
        if ret == 1:
            return True
        elif ret == -1:
            raise NotLoggedInOrLoginExpiredException()
        elif msg == '只有正在使用的预约方可退出':
            self.check_in(reserve_record)
            response = self.get(url)
            resp_json = response.json()
            ret = resp_json['ret']
            msg = resp_json['msg']
            if ret == 1:
                return True

        raise Exception(resp_json['msg'])
