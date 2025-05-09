# 广医校园网API

## 1. 概述

此项目提供了访问广医网上办公、校外VPN、校园网门户网站和图书馆API的工具。

本项目主要包含3大模块，分别是gzhmu，gmuapi和gmulib模块：

- **gzhmu** 模块提供了网上办公和校外VPN的接口，主要用于模拟登录以及使用WebVPN访问内网资源。

- **gmuapi** 模块提供校园网门户网站的接口，主要用于登录、解绑和登出连接校园网的设备，以及查询特定账号的用户信息和已登录的设备信息。

- **gmulib** 模块提供了广医图书馆的接口，主要用于查询图书馆座位信息、预约座位、取消预约、签到和签退等操作。

## 2. 使用要求

- Python3.5及以上

- 联网

## 3. 使用方法

1. 将此项目下载并解压进入项目根目录

2. 安装必要的Python包

```shell
pip3 install -r requirements.txt
```

3. 运行python代码

## 4. 示例

### 4.1. **gzhmu**模块示例

- 获取指定账号的联系方式

注意：从2025年4月开始，学校官网的找回密码页面已经修复了显示完整手机号和邮箱的漏洞，通过此方式获取到的手机号从第4到第7位共4位数字，邮箱的第3到第5个共3个字符会被星号"\*"取代而不可见。例如：123\*\*\*\*4567，ab\*\*\*cde@example.com。

```python
from gzhmu import *
account = 'xxxxxxxxxx'  # 将这里的xxxxxxxxxx替换为需要查询的账号
try:
    contact = Gzhmu.get_contact(account)
    print('phone:', contact.phone)
    print('email:', contact.email)
except UsernameNotExistsException:
    print('账号不存在')
```

当使用非校园网内网访问时需要使用Web VPN，即使用get_contact()方法要指定webvpn参数为**True**。使用校园网访问时则无须显式指定，因为webvpn参数默认为**False**。

- 在内网获取学籍卡片

```python
from gzhmu import *
# 网上办公的账号密码
account = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
gmu = Gzhmu(account, password)
url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
res = gmu.login(url)
url = 'https://jwgl.gzhmu.edu.cn/jsxsd/grxx/xsxx_print.do'
resp = gmu.post(url)
with open('学籍卡片.xls', 'wb') as fp:
    fp.write(resp.content)
```

- 使用Web VPN获取学籍卡片

```python
from gzhmu import *
# 网上办公的账号密码
account = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
vpn = WebVPN(account, password)
# vpn = Gzhmu(account, password, webvpn=True)  # 另一种方式
url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
res = vpn.login(url)
url = 'https://jwgl.gzhmu.edu.cn/jsxsd/grxx/xsxx_print.do'
resp = vpn.post(url)
with open('学籍卡片.xls', 'wb') as fp:
    fp.write(resp.content)
```

- 使用Web VPN和网络代理获取学籍卡片

```python
from gzhmu import *
# 网上办公的账号密码
account = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
# 假设代理的地址是127.0.0.1:7890
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}
vpn = WebVPN(account, password, proxies=proxies)
url = 'http://jwgl.gzhmu.edu.cn/jsxsd/'
res = vpn.login(url)
url = 'https://jwgl.gzhmu.edu.cn/jsxsd/grxx/xsxx_print.do'
resp = vpn.post(url)
with open('学籍卡片.xls', 'wb') as fp:
    fp.write(resp.content)
```

### 4.2. **gmuapi**模块示例

- 在内网查询校园网认证账号信息

```python
from gzhmu import *
account = 'xxxxxxxxxx'  # 将这里的xxxxxxxxxx替换为需要查询的账号
try:
    userInfo = loadUserInfo(account)

    print('姓名：', userInfo.name)
    print('余额：', userInfo.balance, '元')
    print('已使用流量：', userInfo.use_flow, 'MB')
    print('剩余流量：', userInfo.available_flow, 'MB')
except FailedToGetUserInfoException:
    print('无法获取用户信息，查询的账号不存在')
```

- 在内网查询已登录设备的信息

```python
import time
from gzhmu import *

account = 'xxxxxxxxxx'
try:
    devices = loadOnlineDevices(account)

    print('IP\t\tMAC\t\tLogin Time')
    for device in devices:
        print(device.login_ip, device.mac, time.strftime('%Y-%m-%d_%H:%M:%S'), sep='\t')
except FailedToLoadOnlineDevicesException:
    print('无法获取在线设备信息，查询的账号不存在')
```

- 在内网进行校园网认证

```python
from gzhmu import *

#登录校园网的账号密码
account = 'xxxxxxxxxx'
password = 'xxxxxxxx'

try:
    result = login(account, password)
    if result:
        print('成功登录')
except IncorrectAccountOrPasswordException:
    print('账号或密码错误')
except AlreadyLoggedInException:
    print('当前设备已登录')
```

- 使用内网登出当前设备

```python
from gzhmu import *

result = logout()
if result:
    print('当前设备已退出登录')
else:
    print('退出失败')
```

- 使用内网解绑设备（登出其他设备）

```python
from gzhmu import *

account = 'xxxxxxxxxx'
mac = 'AABBCCDDEEFF'  # 12个大写的16进制数，可以通过loadOnlineDevices接口获取到

result = unbind(account, mac)
if result:
    print('成功解绑设备')
else:
    print('解绑失败')
```

以上**gmuapi**模块的API，例如`loadUserInfo`、`loadOnlineDevices`和`unbind`都能使用Web VPN在外网进行访问，只需要传入一个`webvpn`参数即可，这个参数是一个`WebVPN`类的实例，例如：

- 在非校园网中使用Web VPN获取用户信息

```python
from gzhmu import *
# 网上办公的账号密码
account = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
vpn = WebVPN(account, password)
# 登录Web VPN
try:
    vpn.login()
    print('成功登录VPN')
except IncorrectCredentialException:
    print('账号密码错误')
    exit()
# 使用VPN获取账号信息
userInfo = loadUserInfo(account, webvpn=vpn)
print('姓名：', userInfo.name)
print('余额：', userInfo.balance, '元')
print('已使用流量：', userInfo.use_flow, 'MB')
print('剩余流量：', userInfo.available_flow, 'MB')
vpn.logout()
```

注意：当在使用**非校园网**访问校园网内网资源或调用gmuapi模块中的接口时**必须**使用Web VPN访问，相反，若连接**校园网内网**则**不能**使用Web VPN访问。而在非校园网使用gmulib模块访问图书馆接口，直接访问或使用Web VPN皆可。

### 4.3. **gmulib**模块示例

访问图书馆需要登录，所以使用本模块访问图书馆前需要进行登录。

使用本模块进行获取座位信息、获取座位签到链接、预约座位等操作都需要使用Seat类的实例作为传入参数，Seat类是对图书馆座位的封装，包含字段：lib_id, lib_name, room_id, room_name, seat_id, seat_name, seat_number，分别表示所在图书馆ID、所在图书馆名称、所在研修室ID、所在研修室名称、座位ID、座位名称、本座位在其所在研修室中的座位号。

类似的，本模块中的Library和Room类也分别是对图书馆和研修室的封装，包含了ID及名称等相关信息。不同的是，Library对象有一个rooms字段，是一个元素为Room对象的列表，表示图书馆中的所有研修室；Room对象有一个seats字段，是一个元素为Seat对象的列表，表示该研修室中的所有座位。

不同座位的座位ID(seat_id)和座位名称(seat_name)都是不同的，所以如果知道某个座位的确切ID或名称，则可以直接通过get_seat_by_id()或get_seat_by_name()方法分别获取，如果均不确定，则需要使用遍历的方法获取Seat对象，例如，可以先遍历所有研修室(Room)，然后再从某个研修室中获取特定座位(Seat)。

- 列出各图书馆的各个研修室名称

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
libraries = lib.get_libraries()
for library in libraries:
    print(library.lib_name)
    for room in library.rooms:
        print('\t', room.room_name)
```

- 获取指定座位的签到链接

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
# 具体的研修室名称可以从上个示例中获取
room_name = '1楼自修区Ⅰ(越秀）'
room = lib.get_room_by_name(room_name)
seat_number = 20
seat = room.get_seat_by_number(seat_number)
url = GmuLib.get_check_in_url(seat)  # 越秀图书馆1楼自修区Ⅰ 20号座位
print(url)
```

- 从签到链接中获取座位信息

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
check_in_url = 'http://update.unifound.net/wxnotice/s.aspx?c=100492751_Seat_100495246_1EQ'
seat = lib.get_seat_by_check_in_url(check_in_url)
print('{} {} {}号座'.format(seat.lib_name, seat.room_name, seat.seat_number))
```

- 查询用户最新的预约记录

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
user_records = lib.get_reserve_history()
print('执行预约操作的时间', '座位名称', '姓名', '是否生效', '是否签到', '开始时间', '\t结束时间', sep='\t')
for record in user_records:
    reserve_at = record.reserve_at.strftime('%Y-%m-%d_%H:%M:%S')
    seat_name = record.seat.seat_name
    owner = record.owner
    state = '已生效' if record.is_validated else '未生效'
    is_checked_in = '已签到' if record.is_checked_in else '未签到'
    start = record.start.strftime('%Y-%m-%d_%H:%M:%S')
    end = record.end.strftime('%Y-%m-%d_%H:%M:%S')
    print(reserve_at, seat_name, owner, state, is_checked_in, start, end, sep='\t')
```

- 查询用户最新的三个月已完成的预约记录

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
user_records = lib.get_reserve_history(is_new_record=False)
print('执行预约操作的时间', '座位名称', '姓名', '是否生效', '是否签到', '是否违约', '开始时间', '\t结束时间', sep='\t')
for user_record in user_records:
    reserve_at = user_record.reserve_at.strftime('%Y-%m-%d_%H:%M:%S')
    seat_name = user_record.seat.seat_name
    owner = user_record.owner
    state = '已生效' if user_record.is_validated else '未生效'
    is_checked_in = '已签到' if user_record.is_checked_in else '未签到'
    is_default = '违约' if user_record.is_default else '未违约'
    start = record.start.strftime('%Y-%m-%d_%H:%M:%S')
    end = record.end.strftime('%Y-%m-%d_%H:%M:%S')
    print(reserve_at, seat_name, owner, state, is_checked_in, is_default, start, end, sep='\t')
```

- 查询用户信息

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
user_info = lib.get_current_user_info()
print('姓名：', user_info.name)
print('部门：', user_info.department)
print('剩余信用分：', user_info.score)
```

- 获取实时座位信息

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
library = lib.get_library_by_name('越秀校区图书馆')
seat_info_list = lib.get_seat_info(library)  # 获取越秀图书馆所有座位的实时信息

room = lib.get_room_by_name('1楼自修区Ⅰ(越秀）')
seat_info_list = lib.get_seat_info(room)  # 获取指定研修室的所有座位的实时信息

# seat_number = 20
# seat = room.get_seat_by_number(seat_number)
# seat_info_list = lib.get_seat_info(seat)  # 获取指定座位的实时信息

for seat_info in seat_info_list:
    print('座位名称：', seat_info.seat.seat_name)
    print('座位状态：', '开放使用' if seat_info.is_open else '未开放使用')
    print('剩余空闲时间：', seat_info.freetime, '分钟')
    print('已预约记录：')
    if len(seat_info.records) > 0:
        print('\t', '姓名', '是否生效', '开始时间', '\t结束时间', sep='\t')
        for record in seat_info.records:
            owner = record.owner
            state = '已生效' if record.is_validated else '未生效'
            start = record.start.strftime('%Y-%m-%d_%H:%M:%S')
            end = record.end.strftime('%Y-%m-%d_%H:%M:%S')
            print('\t', owner, state, start, end, sep='\t')
    print()
```

- 获取今天的所有预约信息

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
user_records = lib.get_today_reserve_records()
print('座位', '姓名', '是否生效', '开始时间', '结束时间', sep='\t')
for user_record in user_records:
    seat_name = user_record.seat.seat_name
    owner = user_record.owner
    state = '已生效' if user_record.is_validated else '未生效'
    start = user_record.start.strftime('%Y-%m-%d_%H:%M:%S')
    end = user_record.end.strftime('%Y-%m-%d_%H:%M:%S')
    print(seat_name, owner, state, start, end, sep='\t')
```

- 预约一个座位

```python
from datetime import datetime, time
from gzhmu import GmuLib, ReserveConflictException
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
seat = lib.get_seat_by_name('（越秀）自修区Ⅰ-020')
date = datetime.today().date()  # 日期为今天
start = time(17, 0)  # 开始时间为17:00
end = time(17, 30)  # 结束时间为17:30
try:
    res = lib.reserve(seat, date, start, end)
    if res:
        print('预约成功')
except ReserveConflictException as e:
    print('座位冲突，当前作为已被预约或正在使用中')
```

- 取消一个尚未生效的预约

```python
from datetime import datetime, time
from gzhmu import GmuLib, CanNotCancelValidatedReservationException
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
# 获取预约记录
user_records = lib.get_reserve_history()
if len(user_records) == 0:
    print('未找到预约记录')
    exit()

# 选取第一条记录
record = user_records[0]
print('座位：', record.seat.seat_name)
print('开始时间：', record.start.strftime('%Y-%m-%d_%H:%M:%S'))
print('结束时间：', record.end.strftime('%Y-%m-%d_%H:%M:%S'))
try:
    res = lib.cancel(record)
    if res:
        print('成功取消预约')
except CanNotCancelValidatedReservationException as e:
    print('无法取消一个已生效的预约，请先进行签到，或直接使用finish方法取消预约')
```

注意：一个预约会在预约开始时间的前15分钟开始生效，直到预约结束，在预约生效前可以随时取消，而预约生效后无法正常取消，此时只能通过签到再结束使用来避免违约，详见以下2个示例：

- 对一个已生效预约进行签到

```python
from datetime import datetime, time
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
# 获取预约记录
user_records = lib.get_reserve_history()
for record in user_records:
    # 选取第一条已生效的预约记录进行签到
    if record.is_validated:
        print('座位：', record.seat.seat_name)
        print('开始时间：', record.start.strftime('%Y-%m-%d_%H:%M:%S'))
        print('结束时间：', record.end.strftime('%Y-%m-%d_%H:%M:%S'))
        res = lib.check_in(record)
        if res:
            print('成功签到')
```

- 结束一个已生效预约座位的使用

```python
from datetime import datetime, time
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
# 获取预约记录
user_records = lib.get_reserve_history()
for record in user_records:
    # 结束第一条已生效的预约记录
    if record.is_validated:
        print('座位：', record.seat.seat_name)
        print('开始时间：', record.start.strftime('%Y-%m-%d_%H:%M:%S'))
        print('结束时间：', record.end.strftime('%Y-%m-%d_%H:%M:%S'))
        res = lib.finish(record)
        if res:
            print('成功签退，结束使用')
```

GmuLib的finish方法能够结束一个已生效的预约，如果此时未签到，则该方法能够自动进行签到后结束使用，若此时已签到则直接结束使用。

## 4. 免责声明

本项目仅用于学习交流目的，请勿用于非法用途，因使用本项目造成的可能的损失由使用者承担，与本项目无关，您使用此项目代表您同意此声明。
