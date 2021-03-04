import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
x=np.linspace(0,10*np.pi,num=20)
y=np.sin(x)
f1=interp1d(x,y,kind='linear')#线性插值
f2=interp1d(x,y,kind='cubic')#三次样条插值
x_pred=np.linspace(0,10*np.pi,num=1000)
y1=f1(x_pred)
y2=f2(x_pred)
plt.figure()
plt.plot(x_pred,y1,'r',label='linear')
plt.plot(x,f1(x),'b--','origin')
plt.legend()
plt.show()

plt.figure()
plt.plot(x_pred,y2,'b--',label='cubic')
plt.legend()
plt.show()  