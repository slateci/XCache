import matplotlib.pyplot as plt
import numpy as np
import requests
import json
import pandas as pd

# service = "http://192.170.227.234:80"
service = "http://localhost:80"

GB = 1024 * 1024 * 1024
TB = 1024 * GB
PB = 1024 * TB

origreqs = int(2965000 * 0.3035)
origdata = 1054.6 * TB


res = requests.get(service + '/status')
status = json.loads(res.json())
# print(status)

tp = []
for site in status:
    tp.append([site[0], site[1]['requests_received'], site[1]['files_delivered'], site[1]['data_delivered'] / TB])

tp.append(['origin', origreqs, origreqs, origdata / TB])

sites = pd.DataFrame(tp)
# print(sites.head(20))
sites.columns = ['xcache', 'requests', 'hits', 'data delivered']
sites = sites[sites.requests != 0]
print(sites.head(20))

fig, ax = plt.subplots(figsize=(8, 8))
sites.plot(x="xcache", kind="bar", ax=ax, secondary_y='data delivered')
# sites.plot(x="xcache", y=["requests", "hits", "data delivered"], kind="bar", secondary_y='data delivered')
fig.show()
fig.savefig('xcache_sites_report.png')
