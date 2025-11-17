# 项目整体文档

## 项目概述

本项目是一个自动化测试框架，用于测试小安（XiaoAn）电动车控制系统的各种功能模块。项目通过模拟硬件设备（如RFID、BMS、电机控制器、头盔锁等）与中控系统进行通信，实现对中控功能的自动化测试。

## 项目结构

```
testauto_base/
├── config/              # 配置文件目录
│   ├── config.py        # 配置文件解析
│   └── config.conf      # 配置文件
├── models/              # 设备模拟模块
│   ├── xiaoan_485_bus.py     # 485总线处理核心
│   ├── rfid.py               # RFID设备模拟
│   ├── bms.py                # BMS电池管理系统模拟
│   ├── moter_controller.py   # 电机控制器模拟
│   ├── helmetLock.py          # 头盔锁模拟
│   ├── saddle.py              # 电池仓锁模拟
│   ├── overload.py            # 超载模拟
│   ├── externalPower.py       # 外部电源控制
│   ├── xiaoan_json.py         # JSON协议封装
│   ├── xiaoan_protocol.py     # 协议处理核心
│   └── excel_report.py        # Excel报告生成
├── testcases/           # 测试用例目录
│   ├── test_rfid.py     # RFID测试用例
│   ├── test_bms.py      # BMS测试用例
│   ├── test_ovld.py     # 超载测试用例
│   ├── test_headlight.py # 大灯测试用例
│   └── ...
├── utils/               # 工具类目录
│   ├── http_util.py     # HTTP请求工具
│   ├── aliyun_util.py   # 阿里云日志服务工具
│   ├── xa_serial_tool.py # 串口工具
│   └── ...
├── main.py              # 主入口文件
└── requirements.txt     # 依赖包列表
```

---

## 整体调用流程

### 1. 测试执行流程

```
main.py (入口)
    ↓
testcases/test_*.py (测试用例类)
    ↓
setup_class() - 测试类初始化
    ├── 创建Excel报告文件
    ├── 初始化XiaoAnJson执行器
    ├── 初始化外部电源
    ├── 启动485总线处理 (xiaoan_485_bus.main())
    └── 获取设备对象引用
    ↓
setup_method() - 每个测试方法前初始化
    ├── 连接外部电源 (external_power.connect())
    ├── 执行初始化命令 (excutor.c4(defend=1))
    └── 准备测试参数
    ↓
test_*() - 执行测试用例
    ├── 操作模拟设备 (rfid.set_card(), motor_controller.speed = x)
    ├── 执行中控命令 (excutor.c33(), excutor.c34(), excutor.c4())
    ├── 等待响应 (time.sleep())
    └── 断言验证 (assert)
    ↓
teardown_method() - 每个测试方法后清理
    ├── 重置设备状态
    └── 断开连接
    ↓
teardown_class() - 测试类结束
    └── 更新Excel报告
```

### 2. 485总线通信流程

```
中控系统 (ECU)
    ↓ (通过串口 /dev/ttyUSB0 发送命令)
xiaoan_485_bus.serial_reading() 线程
    ├── 读取串口数据
    └── 放入 serial_queue 队列
    ↓
xiaoan_485_bus.deal_serial_data() 线程
    ├── 从队列取出数据
    └── 调用 deal_one_frame() 异步处理
    ↓
deal_one_frame() 解析数据帧
    ├── 识别协议类型
    │   ├── AA 55 (小安协议)
    │   │   ├── 地址 10 → motor_controller.deal_one_serial()
    │   │   ├── 地址 06 → helmet.deal_serial_data()
    │   │   └── 地址 20 → rfid.deal_serial()
    │   ├── 3A 16 (星恒BMS协议) → bms.deal_serial()
    │   ├── FF 02 (RFID协议) → rfid.deal_serial()
    │   └── A0 03 (RFID协议) → rfid.deal_serial()
    └── 设备响应
    ↓ (通过串口发送响应)
中控系统 (ECU) 接收响应
```

### 3. HTTP API调用流程

```
测试用例
    ↓
XiaoAnJson.c33/c34/c4() (命令封装)
    ↓
XiaoAnProtocol.send_request() (协议处理)
    ↓
HttpClient.request() (HTTP请求)
    ↓
中控系统 API 服务器
    ↓ (返回JSON响应)
XiaoAnProtocol.flatten_dict() (扁平化处理)
    ↓
返回给测试用例
    ↓
测试用例进行断言验证
```

### 4. 断言验证流程

```
测试用例执行断言
    ├── assert ret['result.RFID.event'] == 1  # RFID事件状态
    ├── assert ret['result.RFID.cardID'] == expected_card_id  # RFID卡ID
    ├── assert ret['code'] == 0  # API返回码
    ├── assert ret['result.BmsComm'] == 1  # BMS通信状态
    ├── assert ret['result.powerState'] == 1  # 电源状态
    └── assert 'result.RFID.cardID' not in ret  # 字段不存在验证
    ↓
断言失败 → pytest显示错误信息
断言成功 → 测试通过
    ↓
记录到Excel报告
```

---

## 核心文件详解

### 1. models/xiaoan_485_bus.py

**功能**: 485总线核心处理模块，负责串口通信和设备模拟管理

**关键实现**:
- **延迟初始化**: 串口和设备对象在导入时不会立即初始化，避免设备不存在时报错
- **串口读取线程**: `serial_reading()` 持续读取串口数据并放入队列
- **数据处理线程**: `deal_serial_data()` 从队列取出数据并异步处理
- **协议解析**: `deal_one_frame()` 根据协议头识别设备并分发到对应处理器

**关键变量**:
- `serial_queue`: 串口数据队列，最大200条
- `ser`: 串口对象（延迟初始化）
- `motor_controller`: 电机控制器模拟对象
- `bms`: BMS电池管理系统模拟对象
- `helmet`: 头盔锁模拟对象
- `rfid`: RFID模拟对象
- `ovld`: 超载模拟对象

**关键函数**:
- `init_serial_port(port, baudrate)`: 初始化串口和设备对象
- `main(port, baudrate)`: 启动485总线处理（会先调用初始化）
- `serial_reading()`: 串口读取线程函数
- `deal_serial_data()`: 数据处理线程函数
- `deal_one_frame(serial_data)`: 处理单帧数据

**注意事项**:
- 串口设备路径默认为 `/dev/ttyUSB0`，可通过 `main()` 参数修改
- 如果串口不存在，`init_serial_port()` 会返回 False 并打印错误信息
- 所有设备对象在未初始化前为 `None`，使用时需要检查

### 2. models/rfid.py

**功能**: RFID设备模拟，支持多种协议格式

**支持的协议**:
- **AA 55协议**: 标准小安协议（地址0x20）
- **FF 02协议**: RFID专用协议
- **A0 03协议**: RFID替代协议

**关键实现**:
- **电压检测线程**: `check_voltage()` 持续检测RFID 5V供电引脚状态
- **连接状态管理**: `connect()`/`disconnect()` 控制RFID连接状态
- **卡片模拟**: `set_card()`/`pick_up_card()` 模拟放置/拿走卡片

**关键属性**:
- `acc_status`: RFID电源状态（通过GPIO引脚检测）
- `connect_status`: RFID连接状态（软件控制）
- `card_id`: 当前模拟的卡片ID（十六进制字符串）

**响应函数**:
- `query_module_infomation()`: 响应0x11查询模块信息命令
- `response_query_card_id_ff02()`: 响应FF 02 01查询卡片ID
- `response_query_version_ff02()`: 响应FF 02 05查询版本
- `response_query_version_a003()`: 响应A0 03 6A查询版本
- `response_query_card_id_a003()`: 响应A0 03 B8查询卡片ID

**注意事项**:
- RFID需要同时满足 `acc_status=True` 和 `connect_status=True` 才会响应命令
- 卡片ID格式根据RFID类型不同（高频8字节，超高频12字节）

### 3. models/bms.py

**功能**: BMS电池管理系统模拟（星恒BMS类型）

**支持的协议**: 3A 16 开头的星恒BMS协议

**关键实现**:
- **连接状态管理**: `connect()`/`disconnect()` 控制BMS连接状态
- **电池参数模拟**: 电压、电流、温度、容量等参数可配置
- **协议处理**: `deal_serial()` 根据命令字分发到对应响应函数

**关键属性**:
- `connect_status`: BMS连接状态
- `battery_voltage`: 电池组总电压（mV）
- `realtime_current`: 实时电流（mA）
- `relatice_capacity`: 相对容量（%）
- `remain`: 剩余容量（mAh）
- `cell_1_7_voltage`: 1-7节电池电压数组
- `cell_8_13_voltage`: 8-13节电池电压数组

**响应函数**:
- `response_battery_temperature()`: 0x08 电池温度
- `response_battery_voltage()`: 0x09 电池电压
- `response_realtime_current()`: 0x0A 实时电流
- `response_relatice_capacity()`: 0x0D 相对容量
- `response_remain()`: 0x0F 剩余容量
- `response_capacity()`: 0x10 满电容量
- `response_cycle()`: 0x17 循环次数
- `response_bms_version()`: 0x23 BMS版本
- `response_cell_1_7_voltage()`: 0x24 1-7节电压
- `response_cell_8_13_voltage()`: 0x25 8-13节电压
- `reponse_soh()`: 0x0C SOH健康度
- `response_version()`: 0x7F 版本信息
- `response_battery_id()`: 0x7E 电池ID

**注意事项**:
- 只有 `connect_status=True` 时才会响应命令
- 校验和计算使用小端字节序
- 协议帧格式: `3A 16 [命令] [长度] [数据] [校验和低] [校验和高] 0D 0A`

### 4. models/moter_controller.py

**功能**: 电机控制器模拟（类型1控制器）

**关键实现**:
- **ACC检测**: `get_acc_status()` 检测电门锁状态（通过GPIO引脚）
- **轮动信号**: `change_wheel_span()` 线程根据速度控制轮动信号输出
- **大灯控制**: 根据电门状态自动控制大灯（类型1控制器）

**关键属性**:
- `acc_status`: 电门状态（从GPIO读取）
- `speed`: 速度值（km/h）
- `wheel_span_status`: 轮动状态
- `headlight_status`: 大灯状态
- `defend_status`: 防盗开关状态

**响应函数**:
- `response_controller_info()`: 响应0x11查询控制器信息命令
- `deal_defend_on()`: 处理0x19防盗开关命令

**注意事项**:
- 电门未开启时不会响应控制器信息查询
- 轮动信号通过PWM输出，频率10000Hz，占空比0.8
- 速度超过15km/h时，over_speed标志为True

### 5. models/helmetLock.py

**功能**: 头盔锁模拟（支持HelmetLock6和Helmet12两种类型）

**HelmetLock6 (GPIO控制)**:
- 通过GPIO引脚检测开锁/关锁信号
- 通过GPIO输出感应状态和到位状态
- 守护线程持续检测引脚状态变化

**Helmet12 (串口通信)**:
- 通过485总线通信（地址0x06）
- 支持解锁、上锁、查询基本信息、查询实时信息等命令

**关键属性** (Helmet12):
- `lock_state`: 头盔锁逻辑状态
- `induction_state`: 头盔磁感应状态
- `ready_state`: 锁销到位状态
- `wear_state`: 头盔佩戴状态
- `restore_state`: 归还头盔结果
- `lock_block`: 锁卡住状态

**响应函数** (Helmet12):
- `serial_unlock_helmet()`: 0x05 解锁头盔锁
- `serial_lock_helmet()`: 0x06 上锁头盔锁
- `helmet_base_info()`: 0x15 获取头盔基本信息
- `helmet_info_realtime()`: 0x16 获取头盔实时信息

### 6. models/saddle.py

**功能**: 电池仓锁模拟（类型1）

**关键实现**:
- 通过GPIO引脚检测开锁/关锁信号
- 通过GPIO输出反馈状态
- 守护线程持续检测引脚状态变化

**关键函数**:
- `lock()`: 上锁操作
- `unlock()`: 解锁操作
- `set_blocked()`: 设置锁堵塞状态

### 7. models/overload.py

**功能**: 超载模拟（类型2）

**关键实现**:
- 通过GPIO输出前触点/后触点信号
- 模拟超载传感器触发

**关键函数**:
- `trig_head()`/`loose_head()`: 触发/释放前触点
- `trig_tail()`/`loose_tail()`: 触发/释放后触点

### 8. models/externalPower.py

**功能**: 外部电源（大电）控制

**关键实现**:
- 通过GPIO引脚控制大电开关
- `connect()`: 接通大电（GPIO输出高电平）
- `disconnect()`: 断开大电（GPIO输出低电平）

### 9. models/xiaoan_json.py

**功能**: JSON协议命令封装

**关键方法**:
- `c33(acc=0/1)`: 控制电门锁开关
- `c34()`: 查询设备状态
- `c4(defend, isRFID, ...)`: 设防/还车命令
- `c40()`, `c82()`, `c14()`, `c32()`, `c31()`, `c21()`: 其他命令

**返回格式**: 扁平化字典，如 `{'result.RFID.event': 1, 'result.RFID.cardID': '...'}`

### 10. models/xiaoan_protocol.py

**功能**: 协议处理核心

**关键实现**:
- `send_request()`: 发送HTTP请求并返回扁平化结果
- `flatten_dict()`: 将嵌套字典扁平化（用.分隔键名）
- `handle()`: 完整的请求处理流程（包括日志查询）

### 11. testcases/test_rfid.py

**功能**: RFID功能测试用例

**测试场景**:
1. **test_isRFIDEnable_0001**: RFID状态1（有卡，电门开）
2. **test_isRFIDEnable_0002**: RFID状态0（卡拿走，轮动）
3. **test_isRFIDEnable_0003**: RFID状态3（有卡但轮动中）
4. **test_isRFIDEnable_0004**: RFID状态转换（有卡→无卡）
5. **test_isRFIDEnable_0005**: RFID还车（断电情况）
6. **test_isRFIDEnable_0006-0012**: 各种还车场景测试

**断言示例**:
```python
assert ret['result.RFID.event'] == 1  # RFID事件状态为1（有卡）
assert ret['result.RFID.cardID'] == self.rfid.card_id  # 卡片ID匹配
assert ret['code'] == 0  # API返回码为0（成功）
assert 'result.RFID.cardID' not in ret  # 卡片ID字段不存在
```

### 12. testcases/test_bms.py

**功能**: BMS功能测试用例

**测试场景**:
1. **test_bmsType_0021_0027**: 接大电状态验证
2. **test_bmsType_0028_0029**: 未接大电状态验证
3. **test_bmsType_0030_0035**: 接大电换电场景
4. **test_bmsType_0036_0041**: 未接大电换电场景

**断言示例**:
```python
assert ret['result.BmsComm'] == 1  # BMS通信状态为1（正常）
assert ret['result.powerState'] == 1  # 电源状态为1（有电）
assert ret['voltage'] == 0  # 电压为0（断电）
```

---

## 注意事项

### 1. 串口初始化问题（已修复）

**问题**: 原代码在模块导入时就尝试打开串口 `/dev/ttyUSB0`，如果设备不存在会报错。

**解决方案**: 
- 改为延迟初始化，在 `xiaoan_485_bus.main()` 调用时才初始化串口
- 添加了 `init_serial_port()` 函数进行错误处理
- 所有设备对象初始化为 `None`，使用时检查是否为 `None`

**使用方式**:
```python
from models import xiaoan_485_bus

# 导入模块时不会初始化串口，不会报错
# 需要使用时调用 main()
xiaoan_485_bus.main()  # 此时才会初始化串口

# 如果串口不存在，会打印错误信息但不会崩溃
# 返回 False 表示初始化失败
```

### 2. 设备连接顺序

**正确顺序**:
1. 先连接外部电源 (`external_power.connect()`)
2. 然后启动485总线处理 (`xiaoan_485_bus.main()`)
3. 再操作设备对象

**错误示例**:
```python
# 错误：先操作设备，再初始化总线
self.rfid.set_card(card_id)  # 此时 rfid 可能还是 None
xiaoan_485_bus.main()
```

### 3. 线程安全

**注意事项**:
- 串口读取和处理使用两个独立的守护线程
- 使用队列 `serial_queue` 进行线程间通信
- 设备对象的属性修改需要注意线程安全

**建议**:
- 在测试用例中修改设备状态后，使用 `time.sleep()` 等待状态同步
- 避免在多个线程同时修改同一设备对象

### 4. GPIO引脚使用

**注意事项**:
- 项目使用树莓派GPIO，需要运行在树莓派上
- 确保GPIO引脚配置正确（在 `utils/gpio_util.py` 中定义）
- 某些引脚可能需要root权限或GPIO权限

### 5. 串口权限

**注意事项**:
- 确保用户有权限访问 `/dev/ttyUSB0`
- 可能需要将用户加入 `dialout` 组：
  ```bash
  sudo usermod -a -G dialout $USER
  ```
- 或者使用 `sudo` 运行程序

### 6. 测试环境要求

**硬件要求**:
- 树莓派开发板
- USB转串口模块（连接到 `/dev/ttyUSB0`）
- GPIO连线正确（RFID、电机控制器、头盔锁等）
- 外部电源控制电路

**软件要求**:
- Python 3.11+
- 安装 `requirements.txt` 中的依赖包
- 配置文件 `config/config.conf` 正确配置

### 7. 配置文件

**关键配置**:
- `IMEI`: 设备IMEI号
- `BASE_URL`: API服务器地址
- `DEVICE_TYPE`: 设备类型
- `devVsn`: 固件版本号

**配置位置**: `config/config.conf`

### 8. 测试用例编写规范

**规范**:
- 每个测试类必须实现 `setup_class()` 和 `teardown_class()`
- 每个测试方法前执行 `setup_method()`，后执行 `teardown_method()`
- 测试方法名以 `test_` 开头
- 使用 `self.excutor` 执行命令，使用 `assert` 进行断言
- 关键操作后使用 `time.sleep()` 等待响应

**示例**:
```python
def setup_method(self):
    self.external_power.connect()
    self.excutor.c4(defend=1)

def test_example(self):
    self.rfid.connect()
    self.rfid.set_card("BB"*8)
    time.sleep(5)
    ret = self.excutor.c34()
    assert ret['result.RFID.event'] == 1
```

### 9. 协议格式

**AA 55协议格式**:
```
AA 55 [地址] [命令] [长度] [数据...] [校验和]
```

**星恒BMS协议格式**:
```
3A 16 [地址] [命令] [长度] [数据...] [校验和低] [校验和高] 0D 0A
```

**注意事项**:
- 所有数据为十六进制字符串格式
- 校验和计算方式可能不同（参考各设备实现）
- 命令字和地址需要根据协议文档正确设置

### 10. 错误处理

**常见错误**:
1. **串口不存在**: 检查设备连接，确认 `/dev/ttyUSB0` 存在
2. **权限错误**: 检查用户是否有串口访问权限
3. **GPIO错误**: 检查GPIO引脚配置和权限
4. **断言失败**: 检查设备状态、等待时间、预期值是否正确

**调试建议**:
- 启用详细日志输出
- 检查串口数据收发
- 验证设备状态设置
- 确认API响应格式

---

## 测试执行

### 运行单个测试用例
```bash
python testcases/test_rfid.py
# 或
pytest testcases/test_rfid.py::RFIDTest::test_isRFIDEnable_0001
```

### 运行所有测试用例
```bash
pytest testcases/
```

### 使用main.py运行
```bash
python main.py --arg test_rfid
```

---

## 总结

本项目是一个完整的硬件在环（HIL）测试框架，通过模拟各种硬件设备与中控系统进行通信，实现对中控功能的自动化测试。核心特点是：

1. **模块化设计**: 每个设备独立模拟，便于维护和扩展
2. **异步处理**: 使用线程和队列处理串口通信，提高响应速度
3. **协议支持**: 支持多种通信协议格式
4. **自动化测试**: 完整的测试用例框架和报告生成

修复后的代码解决了串口初始化问题，现在可以在设备不存在时正常导入模块，提高了代码的健壮性。

