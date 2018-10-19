import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

fig, ax = plt.subplots(figsize=(8, 8))
bs = []
b = [1, 2, 3, 4, 5, 10, 20, 30, 100, 200, 300, 1000, 2000, 3000, 10000]
for i in b:
    bs.append(math.log(i))
print(bs)
gc=pd.Series([1,1,1,1,1,1,2,2,100,10000])
plt.xticks(bs, ["%s" % i for i in bs])
plt.hist(np.log(gc), log=True, bins=bs)
plt.show()
