import asyncio
import threading
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))

from utils.gpio_util import PIN
from utils.gpio import DigitalInputDevice, DigitalOutputDevice, PWMOutputDevice
# from gpiozero import DigitalInputDevice, DigitalOutputDevice, PWMOutputDevice

class MotorController1:
    
    def __init__(self, serial=None):
        self.moter_controller_acc_detect_pin     = DigitalInputDevice(PIN.MOTOR_CONTROLLER1.acc_detect_pin)      # ACC检测引脚，电门锁
        self.moter_controller_wheel_rotation_pin = PWMOutputDevice(PIN.MOTOR_CONTROLLER1.wheel_rotation_pin, frequency=10000, initial_value=0.8)  # 轮动信号引脚
        self.serial           = serial
        self.magic            = "AA 55"
        self.addr             = "10"
        self.is_upgrade       = False
        self.speed            = 0
        self.pulse            = 0
        self.acc_status       = False                                                      # 电门
        self.headlight_status = False                                                      # 大灯
        self.defend_status    = False                                                      # 防盗开关
        # 助力比
        # 电池信息
        # 仪表信息
        # 电机超载
        # 限流值
        # 缓启动
        self.wheel_span_status = False  # 轮动
        threading.Thread(target=self.change_wheel_span, daemon=True).start()

    def get_acc_status(self):
        """获取电门状态
        """        
        status = self.moter_controller_acc_detect_pin.value
        # print(f"电门状态：{status}")
        if status == 1:
            self.acc_status = True
        elif status == 0:
            self.acc_status = False
        # print(f"电门状态：{self.acc_status}")
        return self.acc_status
    
    def change_headlight_status(self):
        """根据电门状态修改大灯亮灭状态；type1控制器大灯直接绑定电门
        """        
        while True:
            if self.acc_status:
                self.headlight_status = True
            else:
                self.headlight_status = False

    def deal_one_serial(self, serial_data):
        """处理电机控制器总线数据
        Args:
            serial_data (str): 电机控制器总线数据
        """        
        if not self.get_acc_status():
            print("电门未开启，无法回复控制器串口数据")
            return 
        addr = serial_data[2]
        command = serial_data[3]
        # print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{serial_data}")
        if command == "11":
            # 获取控制器信息
            self.response_controller_info()
        elif command == "19":
            # 19 防盗开关
            # asyncio.run(self.deal_defend_on(serial_data))
            pass
        elif command == "13":
            pass
        elif command == "14":
            pass
        elif command == "15":
            pass
        elif command == "16":
            # 0x16 控制大灯开关
            sw = serial_data[4]
            print("*" * 30)
            print(f"收到控制大灯开关指令，大灯状态：{sw}")
            print("*" * 30)
            if sw == "00":
                self.headlight_status = False
            elif sw == "01":
                self.headlight_status = True
           

    def change_wheel_span(self):
        """根据速度修改轮动状态，并根据轮动状态修改轮动信号输出
        """        
        while True:
            if self.speed > 0:
                self.wheel_span_status = True
            if self.wheel_span_status:
            # print(GPIO.input(moter_controller_acc_detect_pin))
                self.moter_controller_wheel_rotation_pin.value = 0.8 # 输出轮动信号
            else:
                self.moter_controller_wheel_rotation_pin.off()
            time.sleep(1)


    def checksum(self, data):
        """计算校验和
        Args:
            data (str): 数据
        Returns:
            _type_: 校验和
        """
        data_index = []
        data = data.split(' ')
        for i in data:
            data_index.append(int(i, 16))
        # 计算校验和
        checksum = sum(data_index) % 256  # 1字节
        hex_int = int(hex(checksum), 16)
        hex_number = f"{hex_int:02X}"
        return hex_number

    def response_controller_info(self, protocol_ver=5, manufacturer=3, model=6, version=14, voltage=49.2):
        """处理中控获取控制器信息命令  0x11
        """  
        if not self.get_acc_status():
            print("电门未开启，无法获取控制器信息")
            return 
        cmd               = "11"                           # 命令
        protocol_ver      = protocol_ver                   # 协议版本
        manufacturer      = manufacturer                   # 制造商
        model             = model                          # 型号
        version           = version                        # 版本
        voltage           = voltage                        # 电压
        current           = 0.7                            # 电流
        pulse             = self.pulse                     # 脉冲
        speed             = self.speed                     # 速度
        stalled           = False                          # 堵转
        turn              = False                          # 转把
        under_voltage     = False                          # 欠压
        over_voltage      = False                          # 过压
        brake             = False                          # 刹车
        hall              = False                          # 霍尔
        over_speed        = True if speed > 15 else False  # 超速
        upgrade           = self.is_upgrade                # 升级
        # controller_error  = True                          # 控制器故障
        # motor_overload    = False                          # 电机超载故障
        # motor_overweight  = False                          # 电机超重故障
        # membrane_overload = False                          # 薄膜超载故障
        fault_list        = [int(stalled), int(turn), int(under_voltage), int(over_voltage), int(brake),
                              int(hall), int(over_speed), int(upgrade)]
        fault             = f"{sum(bit << i for i, bit in enumerate(fault_list))}"     # 故障
        slow_start        = False  # 缓启动
        lock_motor        = False  # 锁电机       
        head_light        = False  # 大灯
        power_mode        = True   # 电力模式
        assist_mode       = True   # 助力模式
        power_saving_mode = False  # 省电模式
        saddle_lock       = False  # 电池仓锁上锁True，解锁False
        left_brake        = False  # 左刹把
        right_brake       = False  # 右刹把
        cruise_control    = False  # 定速巡航
        cut_power_func    = False  # 断动力功能
        cut_power_switch  = False  # 断动力开关
        function_list = [int(slow_start), int(lock_motor), int(head_light), int(power_mode), int(assist_mode), int(power_saving_mode), int(saddle_lock), int(left_brake), int(right_brake), int(cruise_control), int(cut_power_func), int(cut_power_switch)]
        function            = f"{sum(bit << i for i, bit in enumerate(function_list))}"                                                         # 功能开关
        ratio               = 0                                                                                                                     # 助力比
        info                = f"{self.int_to_hex_str(protocol_ver, 2)} {self.int_to_hex_str(manufacturer, 2)} {self.int_to_hex_str(model,2)} {self.int_to_hex_str(version, 2)} {self.int_to_hex_str(voltage*10, 4)} {self.int_to_hex_str(current*10, 4)} {self.int_to_hex_str(pulse, 4)} {self.int_to_hex_str(speed, 2)} {self.int_to_hex_str(fault, 2)} {self.int_to_hex_str(function, 2)} {self.int_to_hex_str(ratio, 2)}"
        length = self.int_to_hex_str(len(info.split(" ")), 2)
        check_sum                 = self.checksum(f"{self.addr} {cmd} {length} {info}")
        controller_info_msg = f"{self.magic} {self.addr} {cmd} {length} {info} {check_sum}"
        self.serial.write(bytes.fromhex(controller_info_msg))
        # print(f"send: {controller_info_msg}")

    def int_to_hex_str(self, data, hex_len=2):
        """_summary_
        int转16进制字符串 
        Args:
            data (_type_): _description_
            hex_len (int, optional): _description_. Defaults to 2.
        """        
         # return f"{int(hex(data),16):hex_lenX}"
        format_str = format(int(hex(int(data)),16), f"0{hex_len}X")
        return " ".join(format_str[i:i+2] for i in range(0, len(format_str), 2))
    
    async def clear_defend_status(self):
        """自动修改设防状态
        """     
        print("zidogn shefang")
        self.defend_status = True
        await asyncio.sleep(10)   
        self.defend_status = False
    
    async def deal_defend_on(self, serial_data):
        """处理防盗开关命令 0x19
        """
        if not self.get_acc_status():
            print("电门未开启，无法获取防盗开关状态")
            return 
        addr = serial_data[2]
        command = serial_data[3]
        if command == "19":
            defend_status = serial_data[4]
            if defend_status == "00":
                self.defend_status = False
            elif defend_status == "01":
                print("抱死状态")
                asyncio.run(self.clear_defend_status())
            return self.defend_status

if __name__ == "__main__":
    from common.externalPower import ExternalPower
    from serial import Serial
    power = ExternalPower()
    power.connect()
    motor_controller = MotorController1(serial=Serial("/dev/ttyUSB0", 9600, timeout=1))
    motor_controller.wheel_span_status = True
    while True:
        print(motor_controller.get_acc_status())
        motor_controller.speed = 10  # 模拟速度
        time.sleep(1) 
    # GPIO.cleanup()