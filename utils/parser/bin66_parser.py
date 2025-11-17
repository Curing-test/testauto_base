class BIN66InfoParser:
    def __init__(self, config):
        self.config = config
    
    def parse_field(self, data, field_name):
        field_config = self.config[field_name]
        start = field_config["start"]
        end = field_config["end"]
        field_type = field_config["type"]
        value = bytes.fromhex(data[start:end])
        if field_type == "int":
            return self.parse_int(value)
        elif field_type == "bytes":
            return value
        elif field_type == "bit":
            return self.parse_bit(value)
        elif field_type == "str":
            return self.parse_str(value)
        else:
            return f"不支持的字段类型: {field_type}"
    
    def parse_int(self, value):
        return int.from_bytes(value, 'big')
    
    def parse_str(self, value):
        return value.decode('utf-8')


    def parse(self, data):
        result = {}
        for field_name in self.config:
            result[field_name] = self.parse_field(data, field_name)
        return result
