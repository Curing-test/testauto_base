import asyncio
from construct import Struct, Int8ub, Int32ub, Bytes, Checksum, Default, this, Optional, CString
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.ble_util import BLEDeviceSync

CMD_MAPPING = {
    0x20: "启动/设防",
    0x21: "获取状态信息",
    0x22: "更改服务器地址",
    0x24: "控制电池仓锁",
    0x25: "控制后轮锁",
    0x26: "重启",
    0x27: "启动/熄火",
    0x28: "播放语音",
    0x29: "PKEON",
    0x2A: "查询状态信息",
    0x2B: "设防",
    0x2C: "启动",
    0x2D: "熄火",
    0x2E: "后轮锁解锁",
    0x2F: "后轮锁上锁",
    0x30: "关机",
    0x31: "PKEOFF",
    0x32: "查询GPS信息",
    0x33: "查询设备IMSI",
    0x34: "电池仓锁解锁",
    0x35: "电池仓锁上锁",
    0x36: "配置测速参数",
    0x37: "配置勿扰模式",
    0x38: "配置钥匙关联",
    0x39: "自动设防配置",
    0x3A: "查询自动落锁配置",
    0x3B: "查询测速参数",
    0x3C: "进入bootDFU",
    0x3D: "查询设备CCID",
    0x3E: "配置APN",
    0x3F: "查询网络状态",
    0x40: "进入存储模式",
    0x41: "查询状态信息_V3",
    0x42: "查询上次道钉信息",
    0x43: "操作头盔锁",
    0x44: "有道钉设防",
    0x45: "有道钉启动",
    0x46: "打开电池锁",
    0x47: "解锁钢丝锁",
    0x48: "上锁钢丝锁",
    0x49: "查询状态信息_V4",
    0x4A: "启动车辆(指定类型)",
    0x4B: "小品出行查询脚撑信息",
    0x4c: "蓝牙数据透传",
    0x50: "查询状态信息_V5",
    0x51: "蓝牙状态报告_V5",
    0x52: "设防车辆(指定类型)",
    0x53: "设置动力模式（F810特订）",
    0x54: "查询RFID信息",
    0x55: "查询摄像头信息",
    0x5D: "开始蓝牙固件升级",
    0x5E: "升级包传输",
    0x5F: "升级包传输完成",
    0x60: "开始L610固件升级",
    0x61: "升级包传输",
    0x62: "升级包传输完成获取电机信息（F810特订）",
    0x68: "头盔锁控制（带参数）",
    0x69: "查询状态信息_V6",
    0x6A: "设置或查询仪表信息",
    0x6B: "设置精准电量的电压曲线",
    0x6C: "查询中控固件版本号",
    0x70: "触发GPS_V6上报",
    0x71: "蓝牙头盔MAC绑定和解绑",
    0x72: "查询头盔佩戴状态信息",
    0xF0: "扩展蓝牙透传命令",
}

CMD_DATA_STRUCTS = {
    0x20: Struct(
        "token" / Int32ub,
        "defend" / Int8ub,
        "idx" / Optional(Int8ub),
        "volumn" / Optional(Int8ub)
    ),
    0x21: Struct(
        "token" / Int32ub,
    ),
    0x22: Struct(
        "token" / Int32ub,
        "server" / CString("ascii")
    ),
    0x24: Struct(
        "token" / Int32ub,
        "saddle"/ Int8ub,
        "idx" / Optional(Int8ub),
        "volumn" / Optional(Int8ub)
    ),
    0x34: Struct(
        "token" / Int32ub,
        "idx" / Optional(Int8ub),
        "volumn" / Optional(Int8ub)
        ),

}
RSP_DATA_STRUCTS = {
    0x20: Struct(
        "cmd" / Int8ub,
        "length" / Int8ub,
        "error_code" / Int8ub,
        "sum" / Int8ub
    ),
    0x21: Struct(
        "cmd" / Int8ub,
        "length" / Int8ub,
        "mode" / Int8ub,
        "gsm" / Int8ub,
        "sw" / Int8ub,
        "voltage" / Int32ub,
        "sum" / Int8ub
    ),
    0x22: Struct(
        "cmd" / Int8ub,
        "length" / Int8ub,
        "error_code" / Int8ub,
        "sum" / Int8ub
    ),
    0x24: Struct(
        "cmd" / Int8ub,
        "length" / Int8ub,
        "error_code" / Int8ub,
        "sum" / Int8ub
    ),
}


class XiaoAnBLEDeviceSync:
    def __init__(self, imei, device_type='share', write_uuid="0783B03E-8535-B5A0-7140-A304D2495CBA", notify_uuid="0783B03E-8535-B5A0-7140-A304D2495CB8", token="168428805"):
        self.imei = imei
        self.device_type = device_type
        self.address     = self.imei_to_address()
        self.write_uuid  = write_uuid
        self.notify_uuid = notify_uuid
        self.token       = token
        self.ble_device  = BLEDeviceSync(self.address, write_uuid, notify_uuid)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def imei_to_address(self) -> str:
        mac = ":".join(f"{self.imei[::-1][i:i+2][::-1]}" for i in range(0, 12, 2))
        if self.device_type == "rent":
            mac = "1"+ mac[1:]
        return mac
    
    def check_sum(self, data: bytes):
        return sum(data) & 0xFF

    def build_full_packet(self, cmd: int, data_dict: dict):
        if cmd not in CMD_DATA_STRUCTS:
            raise ValueError(f"未知命令: {cmd}")
        data_struct = CMD_DATA_STRUCTS[cmd]
        if "token" not in data_dict.keys():
            data_dict["token"] = int(self.token)
        data_bytes = data_struct.build(data_dict)
        def checksum_source(ctx):
            return bytes([ctx.cmd]) + bytes([ctx.data_length]) + ctx.data
        full_struct = Struct(
            "cmd" / Int8ub,
            "data_length" / Default(Int8ub, lambda ctx: len(ctx.data)),
            "data" / Bytes(this.data_length),
            "sum" / Checksum(Int8ub, self.check_sum, checksum_source)
        )
        packet = full_struct.build({"cmd": cmd, "data": data_bytes})
        return packet

    def send_command(self, cmd: int, data_dict: dict, timeout: float = 5.0):
        """同步接口"""
        packet = self.build_full_packet(cmd, data_dict)
        print(f"蓝牙发送[0x{cmd:02X} - {CMD_MAPPING.get(cmd, '未知命令')}]: {packet.hex().upper()}",)
        resp = self.loop.run_until_complete(
            self.ble_device._send_and_wait_async(packet, timeout)
        )
        
        rsp_struct  = RSP_DATA_STRUCTS.get(cmd)
        resp_raw = resp.get("raw")
        print(f"蓝牙接收: {resp_raw.hex().upper()}")
        if rsp_struct:
            resp_data = {k: rsp_struct.parse(resp_raw)[k] for k in rsp_struct.parse(resp_raw) if not k.startswith('_')}
            print(f"蓝牙接收消息解析结果: {resp_data}")
        return resp_data

    def disconnect(self):
        """主动断开连接"""
        self.loop.run_until_complete(self.ble_device.disconnect())
        self.loop.run_until_complete(asyncio.sleep(0.2))  # 让Bleak后台彻底释放
        self.loop.close()

if __name__ == "__main__":
    ble_device = XiaoAnBLEDeviceSync(imei="868222072085724", device_type="share")
    response = ble_device.send_command(0x20, {"defend": 1, "idx": 3, "volumn": 50})
    print("Response:", response)
    # time.sleep(2)
    ble_device.disconnect()