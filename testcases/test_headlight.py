

import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models import xiaoan_485_bus
from models.externalPower import ExternalPower
from models.xiaoan_json import XiaoAnJson

xiaoan_485_bus.main()
excutor          = XiaoAnJson()
BMS              = xiaoan_485_bus.bms
external_power   = ExternalPower(bms=BMS)
motor_controller = xiaoan_485_bus.motor_controller
external_power.connect()
time.sleep(1)
excutor.c33(acc = 1) # 开电门
time.sleep(10)
external_power.disconnect()
BMS.disconnect()
print("断开电源")
time.sleep(10)
print("接入电源")
external_power.connect()
BMS.connect()
time.sleep(10)
print(f"电门状态: {motor_controller.get_acc_status()}")

