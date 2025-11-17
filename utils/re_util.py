import re

# 给定的字符串
text = '[2024-12-26T00:05:15.660] [INFO] [deviceserver.js][biz] - [device][2][bin.5][860957074281841][{"req":"{\"lastBuff\":\"aa55054200015e\",\"header\":{\"magic\":43605,\"cmd\":5,\"seq\":66,\"len\":1,\"splice_flag\":false},\"rawBody\":{\"type\":\"Buffer\",\"data":[94]},\"body\":{\"type\":94}}"}]'

# 正则表达式模式
pattern_bin = r'\[device\]\[\d+\]\[bin.(\d+)\]'

# 搜索并提取信息
match = re.search(pattern_bin, text)
if match:
    bin_in_log = match.group(1)
    print(f'Device ID: {bin_in_log}')
else:
    print('No match found')

import re

# 给定的字符串

# 正则表达式模式
pattern_lastbuff = r'"lastBuff":"([^"]+)"'

# # 搜索并提取信息
match = re.search(pattern_lastbuff, text)
if match:
    last_buff = match.group(1)
    print(f'Last Buff: {last_buff}')
else:
    print('Last Buff not found')
# 正则表达式模式
pattern_type = r'"type":(\d+)'

# 搜索并提取信息
match = re.search(pattern_type, text)
if match:
    type_in_log = match.group(1)
    print(f'Type Value: {type_in_log}')
else:
    print('Type value not found')