import pynmea2
import pandas as pd

gps_list = []

with open(r'D:\workspace\testauto\nmea\data.log', 'r') as f:
    nmea_datas = f.readlines()
for nmea_data in nmea_datas:
    nmea_start = nmea_data.find('$GNGGA')
    #解析北斗
    # nmea_start = nmea_data.find('$GBGSV')
    if nmea_start == -1:
        continue
    nmea_end = nmea_data[nmea_start :].find('\\r\\n') + nmea_start
    
    gnrmc = nmea_data[nmea_start:nmea_end]
    # 创建 NMEA 消息解析器
    msg = pynmea2.parse(gnrmc)

    # 提取时间信息
    time = msg.timestamp  # 输出 datetime.time(22, 5, 16)
    # utc转中国时间
    time = '{}:{}:{}'.format((time.hour + 8) % 24,time.minute,time.second)

    # 提取位置信息
    latitude = msg.latitude  # 输出 51.5636667
    longitude = msg.longitude  # 输出 -0.7040000
    GPS_state = msg.data[5]  # 输出 GPS差分状态
    GPS_NUM = msg.data[6]  # 输出 卫星数量

    print("时间:", time)
    print("纬度:", latitude)
    print("经度:", longitude)
    print("GPS状态:", GPS_state)
    gps_list.append([time, latitude, longitude, GPS_state, GPS_NUM])

df = pd.DataFrame(gps_list, columns=['时间', '经度', '纬度', 'GPS状态', 'GPS卫星数量'])
df.to_csv('data_nmea.csv', index=False)