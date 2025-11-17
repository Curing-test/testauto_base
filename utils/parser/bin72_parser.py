class NotifyV2Parser:
    def __init__(self, config):
        self.config = config

    def parse(self, data):
        # 解析主函数，根据数据结构依次调用其他解析函数
        result = {
            "type": self.parse_field(data, "type"),
            "payload": self.parse_field(data, "payload"),
            "description": self.get_description(data)
        }
        return result

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
        else:
            return f"不支持的字段类型: {field_type}"

    def parse_int(self, value):
        return int.from_bytes(value, 'big')

    def parse_bit(self, value):
        result = {}
        for key, bit_config in self.config[field_name + "_bits"].items():
            bit = bit_config["bit"]
            result[key] = (value >> bit) & 1
        return result

    def get_description(self, data):
        notify_type = self.parse_field(data, "type")
        for key, value in self.config["notify_types"].items():
            if value["type"] == notify_type:
                return value["description"]
        return f"未知通知类型: {notify_type}"