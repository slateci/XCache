import random
from XCache import ServerPlacement
import time

FILES_TO_SIMULATE = 100000
START_SERVERS = 10
END_SERVERS = 9

sp1 = ServerPlacement(6)
print("=======================================")

st = time.time()
for files in range(FILES_TO_SIMULATE):
    fm = random.randint(0, ServerPlacement.MAX_HASH)
    s = sp1.getServer(fm)
print('elapsed time:', time.time() - st)
