from path import Path
name = Path('./pipline.txt')
from time import time
import time



import os
def main():
    cnt=1
    f = open(name, 'r')

    while True:
        try:
            s = f.__next__()
            print(s)
        except:
            pass
        #f.writelines(str(cnt)+'\n')
        time.sleep(0.3)


if __name__ == '__main__':
    main()