import json
import pynmea2
import pandas as pd
import folium

# 将 JavaScript 数组插入到 HTML 模板中
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>模拟生成轨迹</title>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <style>
        /* 设置地图容器的样式 */
        #map {
            height: 400px;
            width: 100%;
        }
    </style>
</head>
<body>
    <h1>模拟生成轨迹示例</h1>
    <div id="map"></div>
    <script type="text/javascript" src="https://webapi.amap.com/maps?v=1.4.15&key=9a3f841b016cdf47921761561637ec18"></script>
    <script>
        // 创建地图容器
        var map = new AMap.Map('map', {
            zoom: 14,  // 设置地图缩放级别
            center: [120.0, 30.0]  // 设置地图中心点经纬度
        });
        
        // 模拟生成轨迹数据
        var points = {points_data};
        
        // 创建轨迹折线
        var polyline = new AMap.Polyline({
            path: points,
            strokeColor: "#3366FF",
            strokeWeight: 5,
            strokeOpacity: 0.8
        });
        // 多边形的坐标数组，注意坐标格式是 [经度, 纬度]
        var polygonArr = [];

        // 创建多边形对象并添加到地图上
        var polygon = new AMap.Polygon({
            path: polygonArr,  // 设置多边形的经纬度路径
            fillColor: '#FFA500',  // 多边形填充色
            strokeColor: '#FF0000',  // 边线颜色
            strokeWeight: 2  // 边线宽度
        });
        map.add(polygon);  // 将多边形添加到地图上
        
        // 将轨迹添加到地图上
        polyline.setMap(map);
    </script>
</body>
</html>
'''

def parse_json_objects(json_data):
    for json_obj in json_data.split('\n\n'):
        if json_obj:
            yield json.loads(json_obj ,strict=False)
        else:
            pass

# 读取NEMA数据文件
with open('nema_data.json', 'r') as f:
    raw_data = f.read()

nmea_data = list(parse_json_objects(raw_data))
print(nmea_data)

# 初始化数据列表
latitudes = []
longitudes = []
point_names = []

def parse_nmea_data(nmea_data):
    try:
        parsed_sentence = pynmea2.parse(nmea_data)
    except pynmea2.nmea.ChecksumError as e:
        print(f"Checksum error: {e}")
    except pynmea2.ParseError as e:
        print(f"Parse error: {e}")
    return parsed_sentence

# 遍历NEMA数据,提取经纬度和点位名称
for nmea_obj in nmea_data:
    nmea_sentences = nmea_obj['result']['nmea'].split('\r\n')
    for sentence in nmea_sentences:
        if sentence.startswith('$GNRMC'):
            gga = parse_nmea_data(sentence)
            latitudes.append(gga.latitude)
            longitudes.append(gga.longitude)
            point_names.append(f"Point {len(latitudes)}")

# 假设 longitudes 和 latitudes 是两个列表
points = [[lon, lat] for lon, lat in zip(longitudes, latitudes)]

# # 将 Python 列表转换为 JavaScript 数组格式
# points_js = json.dumps(points)

# html_content = html_template.replace('{points_data}', points_js)

# # 保存 HTML 文件
# with open('map.html', 'w', encoding='utf-8') as f:
#     f.write(html_content)

# 创建Pandas DataFrame
nema_df = pd.DataFrame({
    'latitude': latitudes,
    'longitude': longitudes,
    'point_name': point_names
})

nema_df.to_csv('nema_data.csv', index=False)

# # 创建Folium地图对象
# map_obj = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# # 在地图上添加标记
# for index, row in nema_df.iterrows():
#     folium.Marker(
#         location=[row['latitude'], row['longitude']],
#         popup=row['point_name']
#     ).add_to(map_obj)

# map_obj.save('nema_map.html')