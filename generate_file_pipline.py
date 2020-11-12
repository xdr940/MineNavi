
from path import Path
from time import time
import numpy as np
import time

from utils.formater import np2line

if __name__ == '__main__':
    fin = Path('./data_out/circle/sqrt_mc.txt')
    pipline = Path('./pipline.txt')

    pose_mc = np.loadtxt(fin)


    cnt = 0
    fout = open(pipline, 'a')
    for cnt,pose in enumerate(pose_mc):
        line = np2line(np.expand_dims(pose,axis=0))
        fout.write(line)
        time.sleep(0.5)
        cnt += 1
    fout.close()




