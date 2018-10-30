from rucio.client import ReplicaClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk

site = 'MWT2'

es = Elasticsearch(['atlas-kibana.mwt2.org:9200'], timeout=60)

start = 1538352000
end = 1539129600

my_query = {
    "_source": ["time_start", "time_end", "site", "event", "scope", "filename", "filesize"],
    'query': {
        'bool': {
            'must': [
                {'range': {'time_start': {'gte': start, 'lt': end}}},
                {'exists': {"field": "filename"}},
                {'wildcard': {'site': site + '*'}},
                # {'wildcard': {'filename': 'EVNT*'}},
                # {'wildcard': {'event': 'get_sm*'}},
                {'term': {'event': 'get_sm'}},
                # {'term': {'event': 'get_sm_a'}},
                # {'term': {'event': 'download'}},
            ]
        }
    }
}


rc = ReplicaClient()

USsites = ['MWT2', 'AGLT2', 'BNL-OSG2', 'SWT2_CPB', 'SLACXRD']
exclude = ['RO-07-NIPNE', 'UNI-FREIBURG', 'TOKYO-LCG2', 'TOKYO-LCG2_LOCALGROUPDISK', 'GOEGRID', 'TAIWAN-LCG2',
           'INFN-COSENZA', 'INFN-MILANO-ATLASC', 'INFN-NAPOLI-ATLAS', 'JINR-LCG2',
           'RRC-KI-T1', 'AUSTRALIA-ATLAS', 'BEIJING-LCG2', 'INFN-ROMA1', 'PRAGUELCG2', 'UAM-LCG2']
scroll = scan(client=es, index="traces", query=my_query)
count = 0
requests = []
for res in scroll:
    r = res['_source']
    # print(r)
    scope = r['scope']
    filen = r['filename']
    files = r['filesize']
    times = r['time_start'] * 1000
    gen = rc.list_replicas(dids=[{'scope': scope, 'name': filen}], schemes=['root'], client_location={'site': 'AGLT2'})
    for i in gen:
        co = 0
        for r in i['rses']:
            path = i['rses'][r][0]
            origin = r.replace('_DATADISK', '')
            # print(origin)
            if (co == 0 or origin in USsites) and origin not in exclude:
                print(i['rses'][r][0])
                requests.append({
                    "_index": "stress",
                    "_type": "docs",
                    "_source": {
                        "filename": scope + ':' + filen,
                        "path": i['rses'][r][0].replace('root://dcdoor16.usatlas.bnl.gov:1094', 'root://dcgftp.usatlas.bnl.gov:1096'),
                        "filesize": files,
                        "timestamp": times,
                        "status": "in queue",
                        "origin": origin
                    }
                })
                co += 1
            else:
                pass
                # print('skipping')

    if not count % 100:
        print(count)
        # storing in ES.
        bulk(es, requests)
        requests = []
    count = count + 1

print('Done.')
