import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils import excel_util
from config import config
from datetime import datetime


def generator_header(file_name, sheet_name="接口测试", test_content="基本功能测试"):
    """生成excel报告头
    """
    time_str = str(datetime.now())[0:19].replace(":", "-")
    sheet_name = "接口测试"
    title = [{"content": "序号"},
             {"content": "操作描述"},
             {"content": "URL"},
             {"content": "方式"},
             {"content": "时间"},
             {"content": "参数/请求体"},
             {"content": "预期返回值"},
             {"content": "实测访问状态码"},
             {"content": "实测JSON返回值"},
             {"content": "实测BIN上报"},
             {"content": "判断"},
             ]
    sheet1 = excel_util.create_sheet(file_name=file_name, sheet_name=sheet_name)
    excel_util.remove_sheet(file_name=file_name, sheet_name='Sheet')
    excel_util.write_line(file_name=file_name, sheet_name=sheet_name, row=1, line=[
                          {"content": "IMEI"}, {"content": config.IMEI}])
    excel_util.write_line(file_name=file_name, sheet_name=sheet_name, line=[
                          {"content": "测试时间"}, {"content": time_str}])
    excel_util.write_line(file_name=file_name, sheet_name=sheet_name, line=[
                          {"content": "测试项目"}, {"content": test_content}])
    excel_util.write_line(file_name=file_name, sheet_name=sheet_name, line=[
                          {"content": "错误计数"},{"content": '=COUNTIF(K:K,"fail")'}])
    excel_util.merge_cells(
        file_name=file_name, sheet_name=sheet_name, row_count=2, column_count=len(title))
    excel_util.write_line(file_name=file_name, sheet_name=sheet_name, row=5, line=[
                          {"content": "测试详情"}])
    excel_util.write_line(file_name=file_name,
                          sheet_name=sheet_name, line=title)

def write_line(file_name, sheet_name, row=0, line=None):
    """
    往excel中加入一行数
    Args:
        file_name (_type_): _description_
        sheet_name (_type_): _description_
        row (int, optional): _description_. Defaults to 0.
        line (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """    
    return excel_util.write_line(file_name=file_name, sheet_name=sheet_name, row=row, line=line)

if __name__ == "__main__":
    generator_header("test.xlsx")
