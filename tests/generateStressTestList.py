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

USsites = ['root://fax.mwt2.org', 'root://dcdoor16.usa', 'root://gk06.atlas-s', 'root://griddev03.sl', 'root://xrootd.aglt2']
exclude = ['root://se.reef.man.', 'root://golias100.fa', 'root://grid-cert-03',
           'root://ccsrm.ihep.a', 'root://f-dpm000.gri', 'root://sdrm.t1.grid',
           'root://agh3.atlas.u', 'root://gridftp-a1-1']
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
            # print(path[:19], path[19:])
            if (co == 0 or path[0:19] in USsites) and path[0:19] not in exclude:
                print(i['rses'][r][0])
                requests.append({
                    "_index": "stress",
                    "_type": "docs",
                    "_source": {
                        "filename": scope + ':' + filen,
                        "path": i['rses'][r][0],
                        "filesize": files,
                        "timestamp": times,
                        "status": "in queue",
                        "origin": r
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
