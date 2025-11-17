import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.parser.tlv_parser import TLVParserFactory

bin68_sw_status = {
    "isDefendOn" : {
        0 : "撤防状态",
        1 : "设防状态"
    },
    "isAccOn" : {
        0 : "电门关闭",
        1 : "电门开启"
    },
    "isWheelLocked" : {
        0 : "后轮未锁",
        1 : "后轮已锁"
    },
    "isSeatLocked" : {
        0 : "电池仓未锁",
        1 : "电池仓已锁"
    },
    "isPowerExist" : {
        0 : "电源不在位",
        1 : "电源在位"
    },
    "isFastGPS" : {
        0 : "慢速上报",
        1 : "快速上报"
    },
    "isMoving" : {
        0 : "车辆静止",
        1 : "车辆移动"
    },
    "isWheelSpin" : {
        0 : "后轮静止",
        1 : "后轮转动"
    },
    "isHelmetUnlock" : {
        0 : "头盔在位",
        1 : "头盔离位"
    },
    "isSleepMode" : {
        0 : "非休眠模式",
        1 : "休眠模式"
    },
    "isMoveAlarmOn" : {
        0 : "禁止主动告警",
        1 : "使能主动告警"
    },
    "isOverSpeedOn" : {
        0 : "超速提示失能",
        1 : "超速提示使能"
    },
    "isGPSUnfixed" : {
        0 : "GPS已定位",
        1 : "GPS未定位"
    },
    "isGyroFixed" : {
        0 : "陀螺仪方向未知",
        1 : "陀螺仪方向确定"
    },
    "isFenceEnable" : {
        0 : "内置围栏未使能",
        1 : "内置围栏使能"
    },
    "isOutofServArea" : {
        0 : "未定位或定位在服务区内",
        1 : "已定位且在服务区外"
    },
    "isRFIDlegal " : {
        0 : "RFID读卡无效",
        1 : "RFID读卡有效"
    },
    "isRTK" : {
        0 : "非高精度定位",
        1 : "高精度定位"
    },
    "isPowerCut" : {
        0 : "非断动力状态",
        1 : "断动力状态"
    }
}

bin68_tlv_type = {
    0x00: {'name': 'angle', 'len': 6},
    0x01: {'name': 'SOC', 'len': 1},
    0x02: {'name': 'bmsVoltage', 'len': 2},
    0x03: {'name': 'etcSpeed', 'len': 2},
    0x04: {'name': 'bmsSN', 'len': 20},
    0x05: {'name': 'rfidCardId'},
    0x09: {'name': 'headingAngle', 'len': 2},
    0x0A: {'name': 'voltageState', 'len': 1},
    0x0B: {'name': 'helmetLockState', 'len': 1},
    0x0C: {'name': 'kickStandState'},
    0x0D: {'name': 'tBeaconRealRssi', 'len': 1},
    0x0E: {'name': 'mile', 'len': 2},
    0x0F: {'name': 'bikeState', 'len': 1},
    0x10: {'name': 'parkState', 'len': 1},
    0x11: {'name': 'remainMiles', 'len': 4},
    0x12: {'name': 'SHelmet', 'len': 8},
    0x13: {'name': 'overload', 'len': 8},
    0x14: {'name': 'kickStand', 'len': 8},
    0x15: {'name': 'elv', 'len': 2},
    0x16: {'name': 'fixLocation', 'len': 10},
    0x17: {'name': 'assetID'},
    0x18: {'name': 'assetType'},
    0x19: {'name': 'helmetLock', 'len': 11},
    0x20: {'name': 'electricEnergy', 'len': 2},
    0x21: {'name': 'bmsManufacturer', 'len': 16},
    0x22: {'name': 'gpsFixType', 'len': 1},
    0x23: {'name': 'ovldFilmState', 'len': 2},
    0x24: {'name': 'rtkCoordinate', 'len': 10},
    0x25: {'name': 'ecuInstallType', 'len': 1},
    0x27: {'name': 'antMixData'},
    0x28: {'name': 'antMixCheck', 'len': 32},
    0x29: {'name': 'currentData', 'len': 9},
    0x2A: {'name': 'bmsMixedType', 'len': 1},
    0x2B: {'name': 'cameraState', 'len': 1},
    0x2C: {'name': 'tBeaconState', 'len': 8},
    0x2D: {'name': 'gpsSourceFlag', 'len': 1},
    0x2E: {'name': 'orgGps', 'len': 8},
    0x2F: {'name': 'fireBoxStatus', 'len': 1},
    0x30: {'name': 'positionList'}
}

class CMD_GPS_V6_Parser:
    def __init__(self):
        self.BINDATA = ''
        self.result = {}
    def parse(self, data):
        self.BINDATA = data
        """主解析入口"""
        self.result['sw']           = self.BIN68_SW(int(self.BINDATA[12:20], base=16))
        self.result['gsm']          = int(self.BINDATA[20:22], base=16)
        self.result['voltage']      = int(self.BINDATA[22:30], base=16)
        self.result['timestamp']    = int(self.BINDATA[30:38], base=16)
        self.result['longitude']    = int(self.BINDATA[38:46], base=16)
        self.result['latitude']     = int(self.BINDATA[46:54], base=16)
        self.result['speed']        = int(self.BINDATA[54:58], base=16)
        self.result['course']       = int(self.BINDATA[58:62], base=16)
        self.result['hdop']         = int(self.BINDATA[62:66], base=16)
        self.result['satellite']    = int(self.BINDATA[66:68], base=16)
        self.result['totalMiles']   = int(self.BINDATA[68:76], base=16)
        self.result['fenceVersion'] = int(self.BINDATA[76:84], base=16)
        
        # TLV 数据解析
        tlv_data = self.BIN68_tlv_decode(self.BINDATA[84:])
        self.result['tlv'] = tlv_data

        return self.result

    def BIN68_SW(self, sw_int):
        """解析sw"""
        #按位解析一个bit32的数
        sw_bits_list = [int(bit) for bit in format(sw_int, '032b')]
        #反转bit顺序
        sw_bits_list.reverse()
        # 确保字典中的键和位的顺序一致
        bin68_sw_bits = list(bin68_sw_status.keys())

        # 创建一个字典来存储每个状态的值
        sw_dict = {bit: sw_bits_list[i] for i, bit in enumerate(bin68_sw_bits)}

        # 创建一个新的字典来存储每个状态的描述
        new_dict = {}
        for bit, value in sw_dict.items():
            description = bin68_sw_status[bit][value]
            new_dict[bit] = description

        return new_dict
    
    def BIN68_tlv_decode(self, data):
        tlv_list = {}
        while data:
            # 从原始数据中提取Type字段（1字节）
            tlv_type = int(data[:2], 16)

            # 从原始数据中提取Length字段（1字节）
            tlv_length = int(data[2:4], 16)

            # 计算Value字段的结束位置
            end_pos = 4 + tlv_length * 2

            # 提取Value字段
            tlv_value = data[4:end_pos]

            # 获取解析器
            parser = TLVParserFactory.get_parser(tlv_type, tlv_length)
            if parser:
                # parsed_value = parser.parse(tlv_value)
                # print(tlv_value)
                parsed_value = parser.parse(bytes.fromhex(tlv_value))
                # print(parsed_value, type(parsed_value))
                field_name = bin68_tlv_type.get(tlv_type, {}).get('name', f"unknown_{tlv_type:02x}")
                tlv_list[field_name] = parsed_value
            else:
                tlv_list[f"unknown_{tlv_type:02x}"] = tlv_value

            # 更新data以处理下一个TLV数据
            data = data[end_pos:]

        return tlv_list