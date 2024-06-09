# for i in range(2,11):
#     print(i)

config = {}
config = {"devices":  {"address": "00:11:22:33:44:55", "paths": [], "address": "00:11:43:33:44:88", "paths": []} }

# config["devices"].append({"address": "00:11:43:33:44:88", "paths": ['path/to/data2']})
# print(config)
# print(config["devices"]["address": "00:11:22:33:44:55"])

from datetime import datetime

t = 1714054293.641348
local_time = datetime.fromtimestamp(t)
print(local_time.strftime('%Y-%m-%d %H:%M:%S'))