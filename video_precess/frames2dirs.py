__author__ = 'xdr940'

'''
input a video with long time frames, split it to several dirs with same frames, and named as sorting
'''

# Python
import argparse
import matplotlib.pyplot as plt
from path import Path
from tqdm import tqdm
import os
parser = argparse.ArgumentParser(description="Video2Frames converter")
parser.add_argument('--input_dir', default='/home/roit/bluep2/datasets/mcv5_tem', help="Input video file")
parser.add_argument('--shader',default='')
parser.add_argument('--output_dir', default="/home/roit/bluep2/datasets/mcv5_tem_dirs", help="Output folder. If exists it will be removed")
parser.add_argument('--videos2frames_log',
                    #default='./videos2frames_log.txt',
                    default=None
                    )
parser.add_argument('--operation',default='mv',choices=['cp','mv'])
parser.add_argument('--framesPerDir',default=50,help='frames num of the other dirs')
parser.add_argument('--base_name',default='')

parser.add_argument('--resize',default=False)

def idx2sub_dir(idx,shader,framesPerDir):
    num = int(idx/framesPerDir)
    if shader:
        return shader+"{:04d}".format(num)
    else:
        return "{:04d}".format(num)


def main(args):
    print(args.input_dir)
    input_dir = Path(args.input_dir)
    src_files = input_dir.files()
    src_files.sort()
    output_dir = Path(args.output_dir)
    output_dir.mkdir_p()

    if args.shader:
        shader = args.shader
    else:
        shader = input_dir.stem

    print("--> {} frames".format(len(src_files)))

    for idx, file in tqdm(enumerate(src_files)):
        sub_dir = idx2sub_dir(idx,shader=None,framesPerDir=args.framesPerDir)
        frame_name = idx%args.framesPerDir
        dst_dir = output_dir/sub_dir
        dst_dir.mkdir_p()
        dst_name = dst_dir/"{:04d}.png".format(frame_name)
        command = "{} {} {}".format(args.operation,file,dst_name)
        os.system(command)


    pass


if __name__ == "__main__":
    args = parser.parse_args()
    print("Start splits frames to dirs...")
    ret = main(args)
    exit(ret)

