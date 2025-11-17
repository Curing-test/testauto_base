import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import config


def read_excel_to_dict(excel_path=config.TEST_DATA_PATH, replace_list=None):
    if not replace_list:
        replace_list = [{"replace_from": "{{imei}}", "replace_to": config.IMEI},
                {"replace_from": "{{DEVICETYPE}}", "replace_to": config.DEVICE_TYPE},
                {"replace_from": "{{DEVICEFULLTYPE}}", "replace_to": config.DEVICE_TYPE_CHANGE},
                {"replace_from": "{{DEVICEVERSION}}", "replace_to": config.devVsn},
                {"replace_from": "{{COREVERSION}}", "replace_to": config.coreVersion}]
    # 读取Excel文件
    df = pd.read_excel(excel_path)
    # 将空值变成 None
    df = df.where(pd.notnull(df), None)
    for it in replace_list:
        df = df.map(lambda x: str(x).replace(it.get("replace_from"), it.get("replace_to")) if isinstance(x, str) else x)
    # 将每一行变成一个字典，key 为首行的标题
    data_list = df.to_dict(orient='records')
    # 遍历数据，确保所有的 NaN 都变成 None
    for record in data_list:
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or value is None):
                record[key] = None
    # 打印结果
    return data_list


if __name__ == "__main__":
    
    print(read_excel_to_dict())