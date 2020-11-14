import numpy as np


arr = np.linspace(0,100,100).reshape([2,2,25])
arr_sub = arr[:,1]
arr[:,1]=0


print(arr_sub)