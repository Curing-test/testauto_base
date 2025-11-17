import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import binascii
from utils.parser.command_parser import CommandParser

config_path = 'utils/parser/config.json'

class BIN_api(object):
    def __init__(self):
        self.magic   = ''
        self.cmd     = ''
        self.seq     = ''
        self.lenth   = ''
        self.BINDATA = ''
        self.result  = {
            'cmd'   : int,
            'result': dict
        }
    
    def cmd_init(self):
        self.magic = self.BINDATA[:4]
        print(self.BINDATA)
        self.cmd = int(self.BINDATA[4:6], base=16)
        self.seq = self.BINDATA[6:8]
        self.lenth = self.BINDATA[8:12]
    
    def cmd_decode(self):
        parser = CommandParser(self.cmd, self.BINDATA, config_path)
        parser.decode()
        self.result = parser.result

    def data_clean(self):
        self.result['cmd'] = 0
        self.result['result'] = {}
    
    def get_cmd_decode(self, arg : str):
        self.BINDATA = arg.rstrip('\\') #去掉多余的换行符
        self.data_clean()
        self.cmd_init()
        self.cmd_decode()
        return self.result
        


if __name__ == '__main__':
    data68 = 'aa5544a700a90000093a1f0000befa67e6775006d20b2e01d17064000500d3004b140000001000000000030200000902ffff0414000000000000000000000000000000000000000005184242424242424242424242424242424200000000000000000a01010b01031308020000000000000021100000000000000000000000000000000001014b23020000250102301f03005c06d20b2e01d17064025006d20b8a01d17006034a06d20b3601d1701e'
    data5 = 'aa550575000108'
    data73 = 'aa554903005538363636353130363735373530373900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    data72 = 'aa55480300080008000400000000'
    data66 = 'aa5542e4002f544230423534433930303030303136533230000000000000000000000064000000003048640001cf9e0000676fcf07'

    bin_decode = BIN_api()
    res = bin_decode.get_cmd_decode(data68)
    print(res)