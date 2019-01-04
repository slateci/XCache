# looks for data with missing info and tries to fix it.
# possible reasons:
# * dataset does not exist any more - not fixable.
# * issue with rucio (404)

import pandas as pd
from rucio.client import DIDClient
from rucio.common import exception as rex

dc = DIDClient()

type = 'prod'  # anal
period = 'AUG'
tasks = pd.read_hdf('analytics/SchedulingWithCache/data/full_' + type + '_' + period + '.h5', key=type, mode='r')

print("tasks:", tasks.shape[0])
tasks = tasks[(tasks.inputfiles > 0) & (tasks.files_in_ds == 0)]
print("suspitious tasks:", tasks.shape[0])
noscope = 0
nodid = 0
rucio404 = 0
full_data = []
for task in tasks.itertuples():
    #     toadd = [task.taskid, 0, "", 0]
    #     print(task.taskid)
    if task.dataset.startswith('panda'):
        dataset = 'panda:' + task.dataset
    else:
        dataset = task.dataset
    if not ':' in dataset:
        print('********* no Scope? ********\n', dataset)
        noscope += 1
#         full_data.append(toadd)
        continue
    (scope, name) = dataset.split(':')
    try:
        res = dc.get_metadata(scope, name)
        print(res['length'], res['datatype'], res['bytes'])
#         toadd = [job.taskid, res['length'], res['datatype'], res['bytes']]
    except rex.DataIdentifierNotFound as dide:
        nodid += 1
        pass
        # print(dide)
    except rex.RucioException as rue:
        rucio404 += 1
        print(dataset)
        print(rue)
    # full_data.append(toadd)
print('no did:', nodid, 'noscope:', noscope, 'rucio 404:', rucio404)
# filled_tasks = pd.DataFrame(full_data)
# filled_tasks.columns = ['taskid', 'files_in_ds', 'datatype', 'ds_bytes']

# filled_tasks.set_index('taskid', drop=True, inplace=True)
# jobs.set_index('taskid', drop=True, inplace=True)
# # print(filled_tasks.head(10))
# # print(jobs.head(10))

# all_data = jobs.join(filled_tasks, how='inner')

# print(all_data.tail(10))
# # filled_tasks.sort_values('created_at', inplace=True)

# all_data.to_hdf('analytics/SchedulingWithCache/data/full_' + type + '_' + period + '.h5', key=type, mode='w', complevel=1)
