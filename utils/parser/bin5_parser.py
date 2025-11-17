class BIN5InfoParser:
    def __init__(self, config):
        self.config = config

    def parse(self, data):
        # 解析主函数，根据数据结构依次调用其他解析函数
        result = {
            "type": self.parse_type(data),
            "description": self.get_description(data)
        }
        return result

    def parse_type(self, data):
        # 根据配置解析告警类型
        start = self.config["type"]["start"]
        end = self.config["type"]["end"]
        type_format = self.config["type"]["type"]
        value = bytes.fromhex(data[start:end])
        if type_format == "int":
            return int.from_bytes(value, 'big')
        else:
            raise ValueError(f"不支持的类型格式: {type_format}")

    def get_description(self, data):
        # 根据解析出的类型获取描述信息
        alarm_type = self.parse_type(data)
        for key, value in self.config["alarm_types"].items():
            if int(key) == alarm_type:
                return value
        return f"未知告警类型: {alarm_type}"