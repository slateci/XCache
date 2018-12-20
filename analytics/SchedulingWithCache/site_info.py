import requests

r = requests.get('http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/?json&preset=schedconf.all')

res = r.json()
for r in res:
    print(r,res[r]['nodes'])
