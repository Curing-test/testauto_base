# 设备通信方式分类文档

本文档详细说明项目中各个设备的通信方式，区分哪些可以直接通过485串口运行测试，哪些需要GPIO引脚模拟。

---

## 一、通信方式分类

### 1. 纯485串口通信设备（无需GPIO）

这些设备**仅通过485串口**与中控通信，不需要GPIO引脚。

| 设备 | 协议格式 | 地址/命令 | 测试用例 |
|------|---------|----------|---------|
| **Helmet12** (头盔锁类型12) | AA 55 | 地址: 06 | `test_helmet.py` (如果使用Helmet12) |
| **XingHengBMS** (星恒BMS) | 3A 16 | 地址: 16 | `test_bms.py` |
| **RFID通信部分** | AA 55 / FF 02 / A0 03 | 地址: 20 | `test_rfid.py` (通信部分) |

**特点**：
- ✅ 只需要USB转串口模块连接到 `/dev/ttyUSB0`
- ✅ 可以直接在非树莓派环境运行（只要有串口）
- ✅ 不依赖GPIO引脚

---

### 2. 纯GPIO控制设备（无需485串口）

这些设备**完全通过GPIO引脚**控制，不通过485串口通信。

| 设备 | GPIO引脚 | 功能 | 测试用例 |
|------|---------|------|---------|
| **HelmetLock6** (头盔锁类型6) | PIN 26/19 (输入)<br>PIN 13/6 (输出) | 检测开锁/关锁信号<br>输出感应/到位状态 | `test_helmet.py` |
| **SaddleType1** (电池仓锁类型1) | PIN 21/20 (输入)<br>PIN 16 (输出) | 检测开锁/关锁信号<br>输出反馈状态 | `test_saddle.py` |
| **Overload2** (超载模拟) | PIN 23/24 (输出) | 输出前/后触点信号 | `test_ovld.py` |
| **ExternalPower** (外部电源) | PIN 14 (输出) | 控制大电开关 | 所有测试用例 |

**特点**：
- ✅ 只需要树莓派GPIO连接
- ✅ 不依赖串口485通信
- ❌ 必须在树莓派上运行

---

### 3. 混合模式设备（需要GPIO + 485串口）

这些设备**同时需要GPIO和485串口**。

| 设备 | GPIO引脚 | 485串口 | 功能说明 |
|------|---------|---------|---------|
| **MotorController1** (电机控制器) | PIN 15 (输入)<br>PIN 18 (PWM输出) | AA 55 地址10 | **GPIO**: ACC检测、轮动信号<br>**485**: 控制器信息查询、大灯控制 |
| **RFID** | PIN 12 (输入) | AA 55 地址20<br>FF 02<br>A0 03 | **GPIO**: ACC电源状态检测<br>**485**: RFID通信、卡片ID查询 |

**特点**：
- ✅ GPIO用于状态检测/控制
- ✅ 485串口用于数据通信
- ❌ 必须在树莓派上运行（需要GPIO）
- ❌ 需要同时连接GPIO和串口

---

## 二、测试用例分类

### ✅ 仅需485串口即可运行

#### 1. BMS测试用例 (`test_bms.py`)

**设备依赖**：
- ✅ **XingHengBMS** (纯485通信)
- ✅ **ExternalPower** (需要GPIO，但可以模拟)
- ⚠️ **MotorController1** (需要GPIO检测ACC，但测试中未直接使用ACC状态)

**运行条件**：
- ✅ USB转串口模块连接到 `/dev/ttyUSB0`
- ⚠️ 建议有外部电源控制（可通过GPIO或其他方式）

**可运行性**: **90%** (主要功能通过485，但外部电源控制需要GPIO)

---

#### 2. RFID测试用例 (`test_rfid.py`) - 部分功能

**设备依赖**：
- ✅ **RFID** (485通信部分)
- ⚠️ **RFID ACC检测** (需要GPIO PIN 12)
- ✅ **MotorController1** (轮动状态通过软件设置，但ACC检测需要GPIO)

**运行条件**：
- ✅ USB转串口模块连接到 `/dev/ttyUSB0`
- ❌ 需要GPIO检测RFID ACC状态（否则无法判断RFID是否上电）
- ❌ 需要GPIO检测电机控制器ACC状态

**可运行性**: **70%** (通信功能可用，但状态检测依赖GPIO)

---

### ❌ 需要GPIO引脚才能运行

#### 1. 超载测试用例 (`test_ovld.py`)

**设备依赖**：
- ❌ **Overload2** (完全依赖GPIO输出)
- ❌ **MotorController1** (需要GPIO检测ACC状态)
- ❌ **ExternalPower** (需要GPIO控制大电)

**GPIO引脚需求**：
```
PIN 23: 超载前触点输出
PIN 24: 超载后触点输出
PIN 15: 电机控制器ACC检测（输入）
PIN 18: 电机控制器轮动信号（PWM输出）
PIN 14: 外部电源控制（输出）
```

**可运行性**: **0%** (完全依赖GPIO)

---

#### 2. 头盔锁测试用例 (`test_helmet.py`) - HelmetLock6

**设备依赖**：
- ❌ **HelmetLock6** (完全依赖GPIO)
- ❌ **ExternalPower** (需要GPIO控制大电)

**GPIO引脚需求**：
```
PIN 26: 头盔锁开锁信号（输入）
PIN 19: 头盔锁关锁信号（输入）
PIN 13: 头盔锁感应状态（输出）
PIN 6:  头盔锁到位状态（输出）
PIN 14: 外部电源控制（输出）
```

**可运行性**: **0%** (完全依赖GPIO)

**注意**: 如果使用Helmet12（通过485通信），则不需要GPIO

---

#### 3. 电池仓锁测试用例 (`test_saddle.py`)

**设备依赖**：
- ❌ **SaddleType1** (完全依赖GPIO)
- ❌ **ExternalPower** (需要GPIO控制大电)

**GPIO引脚需求**：
```
PIN 21: 电池仓锁开锁信号（输入）
PIN 20: 电池仓锁关锁信号（输入）
PIN 16: 电池仓锁反馈状态（输出）
PIN 14: 外部电源控制（输出）
```

**可运行性**: **0%** (完全依赖GPIO)

---

#### 4. 电机控制器测试用例 (`test_motor_controller.py`)

**设备依赖**：
- ❌ **MotorController1** (需要GPIO检测ACC、输出轮动信号)
- ❌ **ExternalPower** (需要GPIO控制大电)

**GPIO引脚需求**：
```
PIN 15: 电机控制器ACC检测（输入）
PIN 18: 电机控制器轮动信号（PWM输出）
PIN 14: 外部电源控制（输出）
```

**可运行性**: **0%** (完全依赖GPIO)

---

## 三、详细设备通信方式分析

### 设备通信方式矩阵

| 设备模块 | GPIO引脚 | 485串口 | 必须树莓派 | 可独立运行 |
|---------|---------|---------|-----------|-----------|
| **HelmetLock6** | ✅ PIN 26,19,13,6 | ❌ | ✅ 是 | ❌ 否 |
| **Helmet12** | ❌ | ✅ AA 55 地址06 | ❌ 否 | ✅ 是 |
| **SaddleType1** | ✅ PIN 21,20,16 | ❌ | ✅ 是 | ❌ 否 |
| **Overload2** | ✅ PIN 23,24 | ❌ | ✅ 是 | ❌ 否 |
| **MotorController1** | ✅ PIN 15,18 | ✅ AA 55 地址10 | ✅ 是 | ⚠️ 部分 |
| **RFID** | ✅ PIN 12 (ACC检测) | ✅ AA 55/FF 02/A0 03 | ✅ 是 | ⚠️ 部分 |
| **XingHengBMS** | ❌ | ✅ 3A 16 地址16 | ❌ 否 | ✅ 是 |
| **ExternalPower** | ✅ PIN 14 | ❌ | ✅ 是 | ❌ 否 |

---

## 四、运行环境要求总结

### 场景1: 仅485串口环境（无GPIO）

**可运行的测试用例**：
- ✅ `test_bms.py` - **90%可用** (BMS通信功能，但缺少外部电源控制)
- ⚠️ `test_rfid.py` - **70%可用** (通信功能可用，但ACC状态检测不准确)

**无法运行的测试用例**：
- ❌ `test_ovld.py` - 完全依赖GPIO
- ❌ `test_helmet.py` (HelmetLock6) - 完全依赖GPIO
- ❌ `test_saddle.py` - 完全依赖GPIO
- ❌ `test_motor_controller.py` - 完全依赖GPIO

**硬件要求**：
- USB转串口模块（连接到 `/dev/ttyUSB0`）
- 485总线连接

**软件要求**：
- Python 3.11+
- `pyserial` 库
- 不需要 `RPi.GPIO` 或 `lgpio`

---

### 场景2: 完整树莓派环境（GPIO + 485串口）

**可运行的测试用例**：
- ✅ `test_bms.py` - **100%可用**
- ✅ `test_rfid.py` - **100%可用**
- ✅ `test_ovld.py` - **100%可用**
- ✅ `test_helmet.py` - **100%可用**
- ✅ `test_saddle.py` - **100%可用**
- ✅ `test_motor_controller.py` - **100%可用**

**硬件要求**：
- 树莓派开发板
- USB转串口模块（连接到 `/dev/ttyUSB0`）
- GPIO连线正确配置

**软件要求**：
- Python 3.11+
- `pyserial` 库
- `lgpio` 库（GPIO控制）
- 所有依赖包

---

## 五、快速判断指南

### 判断测试用例是否需要GPIO的方法

1. **查看测试用例导入的模块**：
   ```python
   # 如果导入这些模块，则需要GPIO：
   from models.overload import Overload2        # ❌ 需要GPIO
   from models.saddle import SaddleType1        # ❌ 需要GPIO
   from models.helmetLock import HelmetLock6    # ❌ 需要GPIO
   from models.externalPower import ExternalPower  # ❌ 需要GPIO
   ```

2. **查看设备初始化代码**：
   ```python
   # 如果使用这些类，则需要GPIO：
   MotorController1()    # ⚠️ 需要GPIO（ACC检测、轮动信号）
   Overload2()           # ❌ 需要GPIO
   SaddleType1()         # ❌ 需要GPIO
   HelmetLock6()         # ❌ 需要GPIO
   RFID()                # ⚠️ 需要GPIO（ACC检测）
   ```

3. **查看是否调用GPIO相关函数**：
   ```python
   # GPIO控制函数：
   .trig_head() / .trig_tail()      # Overload2
   .lock() / .unlock()              # SaddleType1, HelmetLock6
   .connect() / .disconnect()        # ExternalPower
   .get_acc_status()                # MotorController1 (读取GPIO)
   ```

---

## 六、改进建议

### 对于需要在非树莓派环境运行的场景

1. **模拟GPIO类**：
   - 创建一个 `MockGPIO` 类，模拟GPIO输入输出
   - 通过软件状态管理替代GPIO检测

2. **配置开关**：
   - 添加环境变量或配置文件开关
   - 根据环境自动选择真实GPIO或模拟GPIO

3. **分离纯串口测试**：
   - 将纯485通信的测试用例独立出来
   - 便于在没有GPIO的环境中运行

---

## 七、总结表

| 测试用例文件 | 485串口 | GPIO引脚 | 可运行环境 | 推荐运行方式 |
|------------|---------|---------|-----------|------------|
| `test_bms.py` | ✅ 必需 | ⚠️ 建议（外部电源） | 任何有串口的环境 | 485串口即可运行 |
| `test_rfid.py` | ✅ 必需 | ⚠️ 必需（ACC检测） | 树莓派环境 | 需要GPIO |
| `test_ovld.py` | ⚠️ 建议（电机控制器） | ✅ 必需 | 树莓派环境 | 必须GPIO |
| `test_helmet.py` | ⚠️ 可选（Helmet12） | ✅ 必需（HelmetLock6） | 树莓派环境 | 必须GPIO |
| `test_saddle.py` | ❌ 不需要 | ✅ 必需 | 树莓派环境 | 必须GPIO |
| `test_motor_controller.py` | ✅ 必需 | ✅ 必需 | 树莓派环境 | 必须GPIO |

**结论**：
- **纯485串口即可运行**: `test_bms.py`（90%功能）
- **需要GPIO才能运行**: 其他所有测试用例

---

## 附录：GPIO引脚详细配置

```python
# utils/gpio_util.py 中的引脚定义

class PIN:
    # TYPE1 电池仓锁
    class SADDLE_LOCK_1:
        unlock   = 21      # 开锁（输入）
        lock     = 20      # 关锁（输入）
        feedback = 16     # 反馈（输出）
    
    # TYPE6 头盔锁
    class HELMET_LOCK_6:
        unlock    = 26    # 开锁（输入）
        lock      = 19    # 关锁（输入）
        induction = 13    # 感应（输出）
        ready     = 6     # 到位（输出）
    
    # 大电控制
    class ExternalPower:
        power = 14        # 大电控制（输出）
    
    # 薄膜超载
    class OVERLOAD_2:
        head = 23         # 前触点（输出）
        tail = 24         # 后触点（输出）
    
    # RFID
    class RFID:
        acc = 12          # RFID 5V供电检测（输入）
    
    # 电机控制器
    class MOTOR_CONTROLLER1:
        acc_detect_pin     = 15  # 电门检测（输入）
        wheel_rotation_pin = 18  # 轮动信号（PWM输出）
```

**总共使用GPIO引脚**: 11个（输入5个，输出6个）

