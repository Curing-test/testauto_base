import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '../')))
from models.xiaoan_protocol import XiaoAnProtocol
from config import config

class XiaoAnJson(object):
    def __init__(self):
        self.imei    = config.IMEI
        self.XA      = XiaoAnProtocol()
        self.payload = {
                            "imei" : self.imei,
                            "async": 'false',
                            "cmd"  : {
                                "c"    : 0,
                                "param": {
                                }
                            }
                        }
        self.url = config.BASE_URL

    def c33(self, **kwargs):
        self.payload['cmd']['c'] = 33
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload)
        return ret

    def c34(self, **kwargs):
        self.payload['cmd']['c'] = 34
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload)
        return ret

    def c4(self, **kwargs):
        self.payload['cmd']['c'] = 4
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload)
        return ret

    def c40(self, **kwargs):
        self.payload['cmd']['c'] = 40
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload)
        return ret

    def c82(self, **kwargs):
        self.payload['cmd']['c'] = 82
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload)
        return ret

    def c14(self, **kwargs):
        self.payload['cmd']['c'] = 14
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload)
        return ret

    def c32(self, flatten=True,**kwargs):
        self.payload['cmd']['c'] = 32
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload,flatten=flatten)
        return ret

    def c31(self, flatten=True):
        self.payload['cmd']['c'] = 31
        ret = self.XA.send_request(self.url, self.payload, flatten=flatten)
        return ret
    
    def c21(self, **kwargs):
        self.payload['cmd']['c'] = 21
        self.payload['cmd']['param'] = kwargs
        ret = self.XA.send_request(self.url, self.payload)
        return ret