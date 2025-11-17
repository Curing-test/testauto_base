from app.parsers.parser_factory import ParserFactory

class CommandParser:
    def __init__(self, cmd, bindata, config_path):
        self.cmd = cmd
        self.BINDATA = bindata
        self.factory = ParserFactory(config_path)
        self.result = {'cmd': cmd, 'result': None}


    def decode(self):
        parser = self.factory.get_parser(self.cmd)
        if parser:
            self.result['result'] = parser.parse(self.BINDATA)
        else:
            self.result['result'] = None
    
    
