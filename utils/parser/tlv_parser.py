class TLVParser:
    def __init__(self, tlv_type, length):
        self.tlv_type = tlv_type
        self.length = length

    def parse(self, value):
        raise NotImplementedError("Subclasses should implement this method")

class AngleParser(TLVParser):
    def parse(self, value):
        return [int.from_bytes(value[i:i+2], 'big', signed=True) * 0.1 for i in range(0, len(value), 2)]

class SOCParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class BMSVoltageParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big') * 0.01

class ETCSpeedParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big') * 0.01

class BMSSNParser(TLVParser):
    def parse(self, value):
        return value.hex() 

class RFIDCardIdParser(TLVParser):
    def parse(self, value):
        rfid_status = {
                "0000000000000000": "RFID读卡模块正常, 但未扫描到标签",
                "ffff": "已通电, RFID读卡模块无信号",
                "fffe": "已通电, RFID读卡模块内部故障",
                "fffd": "中控未给RFID模块供电",
                "fffc": "识别到标签, 但校验规则不匹配"
            }
            
        return rfid_status.get(value.hex(), value)

class HeadingAngleParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big', signed=True) * 0.1

class VoltageStateParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class HelmetLockStateParser(TLVParser):
    def parse(self, value):
        return {
            "lock_type": "四芯头盔锁" if value[0] & 0b1 == 0 else "六芯头盔锁",
            "in_position_detection": "无检测" if value[0] & 0b10 == 0 else "有检测",
            "lock_in_position": "未在位" if value[0] & 0b100 == 0 else "在位",
            "locked": "未上锁" if value[0] & 0b1000 == 0 else "已上锁",
            "connected": "未连接" if value[0] & 0b10000 == 0 else "已连接"
        }

class KickStandStateParser(TLVParser):
    def parse(self, value):
        return {
            "type": int.from_bytes(value[0:1], 'big'),
            "magnetic_state": int.from_bytes(value[1:2], 'big') if value[0] == 1 else None,
            "rfid_state": int.from_bytes(value[2:3], 'big') if value[0] == 0 else None,
            "rfid_tag": value[3:].hex() if value[0] == 0 else None
        }

class TBeaconRealRssiParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class MileParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big') * 0.1

class BikeStateParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class ParkStateParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class RemainMilesParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class SHelmetParser(TLVParser):
    def parse(self, value):
        return {
            "battery_percentage": int.from_bytes(value[0:1], 'big'),
            "helmet_status": int.from_bytes(value[1:2], 'big'),
            "function_flags": int.from_bytes(value[2:3], 'big'),
            "posture_angle": int.from_bytes(value[3:4], 'big'),
            "capacitance_status": int.from_bytes(value[4:5], 'big'),
            "infrared_status": int.from_bytes(value[5:6], 'big'),
            "pressure_status": int.from_bytes(value[6:7], 'big'),
            "fault_status": int.from_bytes(value[7:8], 'big')
        }

class OverloadParser(TLVParser):
    def parse(self, value):
        return {
            "overload_type": int.from_bytes(value[0:1], 'big'),
            "overload_status": int.from_bytes(value[1:2], 'big')
        }

class KickStandParser(TLVParser):
    def parse(self, value):
        return {
            "stand_type": int.from_bytes(value[0:4], 'big'),
            "site_number": int.from_bytes(value[4:6], 'big'),
            "parking_number": int.from_bytes(value[6:8], 'big')
        }

class ELVParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big', signed=True)

class FixLocationParser(TLVParser):
    def parse(self, value):
        return {
            "source": int.from_bytes(value[0:1], 'big'),
            "confidence": int.from_bytes(value[1:2], 'big'),
            "longitude": int.from_bytes(value[2:6], 'big') * 0.000001,
            "latitude": int.from_bytes(value[6:10], 'big') * 0.000001
        }

class AssetIDParser(TLVParser):
    def parse(self, value):
        return value.decode()

class AssetTypeParser(TLVParser):
    def parse(self, value):
        return value.decode()

class HelmetLockParser(TLVParser):
    def parse(self, value):
        return {
            "status": int.from_bytes(value[0:1], 'big'),
            "fault": int.from_bytes(value[1:3], 'big'),
            "voltage": int.from_bytes(value[3:5], 'big') * 0.01,
            "helmet_id": value[5:11].hex()
        }

class ElectricEnergyParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big') * 0.1

class BMSManufacturerParser(TLVParser):
    def parse(self, value):
        return value.decode()

class GPSFixTypeParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class OvldFilmStateParser(TLVParser):
    def parse(self, value):
        return {
            "change_status": int.from_bytes(value[0:1], 'big'),
            "switch_status": int.from_bytes(value[1:2], 'big')
        }

class RTKCoordinateParser(TLVParser):
    def parse(self, value):
        return {
            "longitude_int": int.from_bytes(value[0:1], 'big'),
            "longitude_frac": int.from_bytes(value[1:5], 'big') * 0.00000001,
            "latitude_int": int.from_bytes(value[5:6], 'big'),
            "latitude_frac": int.from_bytes(value[6:10], 'big') * 0.00000001
        }

class ECUInstallTypeParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class AntMixDataParser(TLVParser):
    def parse(self, value):
        return value.hex()

class AntMixCheckParser(TLVParser):
    def parse(self, value):
        return value.hex()

class CurrentDataParser(TLVParser):
    def parse(self, value):
        return {
            "realtime_current": int.from_bytes(value[0:4], 'big'),
            "energy_consumption": int.from_bytes(value[4:8], 'big'),
            "consumption_time": int.from_bytes(value[8:9], 'big')
        }

class BMSMixedTypeParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class CameraStateParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class TBeaconStateParser(TLVParser):
    def parse(self, value):
        return {
            "strongest_signal": int.from_bytes(value[0:1], 'big'),
            "threshold": int.from_bytes(value[1:2], 'big'),
            "mac_address": value[2:8].hex()
        }

class GPSSourceFlagParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class OrgGPSParser(TLVParser):
    def parse(self, value):
        return {
            "longitude": int.from_bytes(value[0:4], 'big') * 0.000001,
            "latitude": int.from_bytes(value[4:8], 'big') * 0.000001
        }

class FireBoxStatusParser(TLVParser):
    def parse(self, value):
        return int.from_bytes(value, 'big')

class PositionListParser(TLVParser):
    def parse(self, value):
        return {
            "number": int.from_bytes(value[0:1], 'big'),
            "positions": [
                {
                    "type": int.from_bytes(value[i+1:i+2], 'big'),
                    "confidence": int.from_bytes(value[i+2:i+3], 'big'),
                    "latitude": int.from_bytes(value[i+3:i+7], 'big') * 0.000001,
                    "longitude": int.from_bytes(value[i+7:i+11], 'big') * 0.000001
                } for i in range(1, 1 + 10 * value[0], 10)
            ]
        }


class TLVParserFactory:
    @staticmethod
    def get_parser(tlv_type, length):
        parsers = {
            0x00: AngleParser,
            0x01: SOCParser,
            0x02: BMSVoltageParser,
            0x03: ETCSpeedParser,
            0x04: BMSSNParser,
            0x05: RFIDCardIdParser,
            0x09: HeadingAngleParser,
            0x0A: VoltageStateParser,
            0x0B: HelmetLockStateParser,
            0x0C: KickStandStateParser,
            0x0D: TBeaconRealRssiParser,
            0x0E: MileParser,
            0x0F: BikeStateParser,
            0x10: ParkStateParser,
            0x11: RemainMilesParser,
            0x12: SHelmetParser,
            0x13: OverloadParser,
            0x14: KickStandParser,
            0x15: ELVParser,
            0x16: FixLocationParser,
            0x17: AssetIDParser,
            0x18: AssetTypeParser,
            0x19: HelmetLockParser,
            0x20: ElectricEnergyParser,
            0x21: BMSManufacturerParser,
            0x22: GPSFixTypeParser,
            0x23: OvldFilmStateParser,
            0x24: RTKCoordinateParser,
            0x25: ECUInstallTypeParser,
            0x27: AntMixDataParser,
            0x28: AntMixCheckParser,
            0x29: CurrentDataParser,
            0x2A: BMSMixedTypeParser,
            0x2B: CameraStateParser,
            0x2C: TBeaconStateParser,
            0x2D: GPSSourceFlagParser,
            0x2E: OrgGPSParser,
            0x2F: FireBoxStatusParser,
            0x30: PositionListParser,
        }
        parser_class = parsers.get(tlv_type, None)
        if parser_class is not None:
            return parser_class(tlv_type, length)
        else:
            return None
