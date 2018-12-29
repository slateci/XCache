# Extracts datasets info

import pandas as pd
from rucio.client import DIDClient
from rucio.common import exception as rex

dc = DIDClient()

type = 'prod'  # anal
period = 'SEP'
jobs = pd.read_hdf('analytics/SchedulingWithCache/data/jobs_' + type + '_' + period + '.h5', key=type, mode='r')

print("jobs:", jobs.shape[0])

count = 0
full_data = []
for job in jobs.itertuples():
    # if count > 1000:
    #     break
    if not count % 1000:
        print(count)
    count += 1
    toadd = [job.taskid, 0, "", 0]
    print(job.taskid)
    if job.inputfiles == 0:
        full_data.append(toadd)
        continue
    if not ':' in job.dataset:
        print('********* no Scope? ********\n', job.dataset)
        full_data.append(toadd)
        continue
    (scope, name) = job.dataset.split(':')
    try:
        # gen = dc.list_files(scope, name)
        # for f in gen:
        #     print(f['guid'], f['bytes'])
        res = dc.get_metadata(scope, name)
        print(res['length'], res['datatype'], res['bytes'])
        toadd = [job.taskid, res['length'], res['datatype'], res['bytes']]
    except rex.DataIdentifierNotFound as dide:
        pass
        # print(dide)
    except rex.RucioException as rue:
        print(rue)
    full_data.append(toadd)

filled_tasks = pd.DataFrame(full_data)
filled_tasks.columns = ['taskid', 'files_in_ds', 'datatype', 'ds_bytes']

filled_tasks.set_index('taskid', drop=True, inplace=True)
jobs.set_index('taskid', drop=True, inplace=True)
# print(filled_tasks.head(10))
# print(jobs.head(10))

all_data = jobs.join(filled_tasks, how='inner')

print(all_data.tail(10))
# filled_tasks.sort_values('created_at', inplace=True)

all_data.to_hdf('analytics/SchedulingWithCache/data/full_' + type + '_' + period + '.h5', key=type, mode='w', complevel=1)
