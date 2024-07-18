# 广医校园网API

## 1. 概述

此项目提供了访问广医网上办公、校外VPN以、校园网门户网站和图书馆API的工具。

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
        print(device.login_ip, device.mac, time.ctime(device.login_time), sep='\t')
except FailedToLoadOnlineDevicesException:
    print('无法获取在线设备信息，查询的账号不存在')
```

- 在内网进行校园网认证

```python
from gzhmu import *

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
vpn.logou()
```

### 4.3. **gmulib**模块示例

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
room_name = '1楼自修区Ⅰ（越秀）'
room_list = lib.get_room_with_name(room_name)
room = room_list[0]
seat_number = 20
seat = room.get_seat_with_number(seat_number)
url = GmuLib.get_check_in_url(seat)  # 越秀图书馆1楼自修区Ⅰ 20号座位
print(url)
```

- 查询用户最新的预约记录

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
user_records = lib.get_reserve_history()
print('执行预约操作的时间', '座位名称', '姓名', '状态', '开始时间', '\t结束时间', sep='\t')
for record in user_records:
    print(record.reserve_at.ctime(), record.seat.seat_name, record.owner, record.state, record.start.ctime(), record.end.ctime(), sep='\t')
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
library_list = lib.get_library_with_name('越秀')
library = library_list[0]
seat_info_list = lib.get_seat_info(library)  # 获取越秀图书馆所有座位的实时信息

room_list = lib.get_room_with_name('1楼自修区Ⅰ（越秀）')
room = room_list[0]
seat_info_list = lib.get_seat_info(room)  # 获取指定研修室的所有座位的实时信息

seat_number = 20
seat = room.get_seat_with_number(seat_number)
seat_info_list = lib.get_seat_info(seat)  # 获取指定座位的实时信息

seat_info = seat_list[0]
print('座位名称：', seat_info.seat.seat_name)
print('座位状态：', seat_info.state)
print('剩余空闲时间：', seat_info.freetime, '分钟')
print('已预约记录：')
print('姓名', '状态', '开始时间', '\t结束时间', sep='\t')
for record in seat_info.records:
    print(record.owner, record.state, record.start.ctime(), record.end.ctime(), sep='\t')
```

- 获取今天的所有预约信息

```python
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
records = lib.get_today_reserve_records()
print('座位', '姓名', '状态', '开始时间', '结束时间', sep='\t')
for record in user_records:
    print(record.seat.seat_name, record.owner, record.state, record.start.ctime(), record.end.ctime())
```

- 预约一个座位

```python
from datetime import datetime, time
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
seat_list = lib.get_seat_with_name('（越秀）自修区Ⅰ-020')
seat = seat_list[0]
date = datetime.today().date()  # 日期为今天
start = time(17, 0)  # 开始时间为17:00
end = time(17, 30)  # 结束时间为17:30
res = lib.reserve(seat, date, start, end)
if res:
    print('预约成功')
```

- 取消预约

```python
from datetime import datetime, time
from gzhmu import GmuLib
username = 'xxxxxxxxxx'
password = 'xxxxxxxxxx'
lib = GmuLib(username, password)
res = lib.login()
# 获取预约记录
user_records = lib.get_reserve_history()
# 选取第一条记录
record = user_records[0]
print('座位：', record.seat.seat_name)
print('开始时间：', record.start.ctime())
print('结束时间：', record.end.ctime())
res = lib.cancel(record)
if res:
    print('成功取消预约')
```

- 签到

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
    # 选取第一条生效的预约记录进行签到
    if record.state == 'doing':
        print('座位：', record.seat.seat_name)
        print('开始时间：', record.start.ctime())
        print('结束时间：', record.end.ctime())
        res = lib.check_in(record)
        if res:
            print('成功签到')
```

- 结束使用

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
    # 选取第一条生效的预约记录进行签到
    if record.state == 'doing':
        print('座位：', record.seat.seat_name)
        print('开始时间：', record.start.ctime())
        print('结束时间：', record.end.ctime())
        res = lib.finish(record)
        if res:
            print('成功签退，结束使用')
```
## 4. 免责声明

本项目仅用于学习交流目的，请勿用于非法用途，因使用本项目造成的可能的损失由使用者承担，与本项目无关，您使用此项目代表您同意此声明。
