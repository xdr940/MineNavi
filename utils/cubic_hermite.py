import numpy as np
from numpy import floor
import matplotlib.pyplot as plt
class CubicHermite():
    def __init__(self,xi,yi):
        '''
        inited by control points
        :param xi:
        :param yi:
        '''
        self.xi=xi
        self.yi=yi
        assert len(xi)==len(yi)
        self.num = len(xi)

    def _get_arr(self,idx):
        if idx<0:
            return self.yi[0]
        elif idx>=len(self.yi):
            return self.yi[-1]
        else:
            return self.yi[idx]
    def _CubicHermite(self,A,B,C,D,t):
        '''

        '''
        a = -0.5*A  + 1.5* B - 1.5 * C +0.5* D
        b = A -2.5*B + 2*C - 0.5*D
        c = -0.5*A  + 0.5*C
        d = B
        return a * t * t * t + b * t * t + c * t + d

    def _fit(self,x,i):

        idx=0
        if x<=self.xi[0]:
            idx=0
        elif x>=self.xi[-1]:
            idx=len(self.xi)-1
        else:
            while idx< len(self.yi)-1:
                if x>=self.xi[idx] and x<self.xi[idx+1]:
                    break
                idx+=1

        x = i*self.step
        t = x - floor(x)
        A = self._get_arr(idx - 1)
        B = self._get_arr(idx + 0)
        C = self._get_arr(idx + 1)
        D = self._get_arr(idx + 2)
        y = self._CubicHermite(A, B, C, D, t)
        return y

    def __call__(self, xs):
        ys = []
        i=0
        self.num_samples = len(xs)
        self.step = (self.num-1)/(self.num_samples-1)
        for x in xs:
            ys.append(self._fit(x,i))
            i+=1

        return np.array(ys)


if __name__ == '__main__':
    xi = np.array([0, 50, 100, 150, 200])
    yi = np.array([0, -100, 0, -50, 0])
    interp_hermite = CubicHermite(xi,yi)

    x=np.linspace(0,200,29)
    #print(x)
    y = interp_hermite(x)
    print(y)

    plt.plot(x,y,'b-*')
    plt.plot(xi,yi,'ro')

    plt.show()
