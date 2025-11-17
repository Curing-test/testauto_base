import json
from enum import Enum

from utils.parser.bin5_parser import BIN5InfoParser
from utils.parser.bin66_parser import BIN66InfoParser
from utils.parser.bin72_parser import NotifyV2Parser
from utils.parser.bin68_parser import CMD_GPS_V6_Parser
from utils.parser.tlv_parser import TLVParser

class BIN(Enum):
    PING = 2
    ALARM = 5
    BMS_INFO = 66
    GPS_V6 = 68
    NOTIFY_V2 = 72

class ParserFactory:
    def __init__(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in config file: {config_path}")

    def get_parser(self, cmd):
        if cmd == BIN.ALARM.value:
            return BIN5InfoParser(self.config['ALARM'])
        elif cmd == BIN.BMS_INFO.value:
            return BIN66InfoParser(self.config['BIN_66_INFO'])
        if cmd == BIN.GPS_V6.value:
            return CMD_GPS_V6_Parser()
        elif cmd == BIN.NOTIFY_V2.value:
            return NotifyV2Parser(self.config['NOTIFY_V2'])

