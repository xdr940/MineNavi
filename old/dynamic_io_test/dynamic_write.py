


from path import Path
name = Path('./pipline.txt')
from time import time
import time

import os
def main():

    cnt =0
    while True:
        f = open(name,'a')
        line = 'pose:'+str(cnt)+'\n'
        f.writelines(line)
        print(line)
        f.close()
        time.sleep(0.5)
        cnt+=1


if __name__ == '__main__':
    main()


