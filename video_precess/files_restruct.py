

import os
from path import Path

def mkdirs():
    start = 72
    base_path = Path("/home/roit/bluep2/datasets/mcv5dst")
    for i in range(start,start+9):
        cmd = "mkdir "+base_path/"{:04d}s".format(i)
        print(cmd)
        os.system(cmd)
        cmd = "mkdir " + base_path / "{:04d}w".format(i)
        print(cmd)
        os.system(cmd)

        cmd = "mkdir " + base_path / "{:04d}n".format(i)
        print(cmd)
        os.system(cmd)

        cmd = "mkdir " + base_path / "{:04d}e".format(i)
        print(cmd)
        os.system(cmd)


def mvdirs():
    shader="sildurs-e-9k"
    start=0
    base_path = Path("/home/roit/bluep2/datasets/mcv4videos/split")

    src_dirs = base_path.dirs()
    src_dirs.sort()
    dst_path = Path("/home/roit/datasets/mcv4")
    for idx,item in enumerate(src_dirs):
        src_name = item
        dst_name = dst_path/"{:04d}".format(idx+start)/shader
        cmd = "mv {} {}".format(src_name,dst_name)
        os.system(cmd)
        print(cmd)

def rmdirs():
    shader = "depth"
    start = 84
    stop = 84+27
    base_path = Path("/home/roit/bluep2/datasets/mcvideo1024768/dolly/splits")
    src_dirs = base_path.dirs()
    src_dirs.sort()
    dst_path = Path("/home/roit/datasets/mcv3")
    for idx in range(start,stop):
        dst_name = dst_path / "{:04d}".format(idx + start) / shader
        cmd = "rm -rf {}".format( dst_name)
        os.system(cmd)
        print(cmd)

    pass

if __name__ == '__main__':
    # mkdirs()
    mvdirs()
    #rmdirs()



    pass
