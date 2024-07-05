# 广医校园网API

## 1. 概述

此项目提供了访问广医网上办公、校外VPN以及校园网门户网站API的工具。

本项目主要包含2大模块，分别是gzhmu和gmuapi模块：

- **gzhmu** 模块提供了网上办公和校外VPN的接口，主要用于模拟登录以及使用WebVPN访问内网资源。

- **gmuapi** 模块提供校园网门户网站的接口，主要用于登录、解绑和登出连接校园网的设备，以及查询特定账号的用户信息和已登录的设备信息。

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

以下是**gzhmu**模块的示例：

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

以下是**gmuapi**模块的示例：

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

## 4. 免责声明

本项目仅用于学习交流目的，请勿用于非法用途，因使用本项目造成的可能的损失由使用者承担，与本项目无关，您使用此项目代表您同意此声明。
