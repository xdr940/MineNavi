
#
import argparse
import os, sys
import shutil
import subprocess
import json
from path import Path
import matplotlib.pyplot as plt
from tqdm import tqdm
# Opencv
import cv2
from threading import Lock,Thread

import numpy as np

parser = argparse.ArgumentParser(description="Video2Frames converter")
parser.add_argument('--input_video', default='/home/roit/bluep2/datasets/mnv0-videos/cldy-0002/depth.mp4', help="Input video file")
parser.add_argument('--out_dir',
                    default=None,
                    # default='/home/roit/bluep2/datasets/fpv_full',
                    help="Output folder. If exists it will be removed")
parser.add_argument('--save_ext',default='png')

args = parser.parse_args()

from blessings import Terminal


class Writer(object):
    """Create an object with a write method that writes to a
    specific place on the screen, defined at instantiation.

    This is the glue between blessings and progressbar.
    """

    def __init__(self, location):
        """
        Input: location - tuple of ints (x, y), the position
                        of the bar in the terminal
        """
        self.location = location
        self.t = Terminal()

    def write(self, string):
        with self.t.location(*self.location):
            sys.stdout.write("\033[K")
            print(string)

    def flush(self):
        return


class Video2Frame():
    def __init__(self,input_video,out_dir,save_ext):
        self.input_video = Path(input_video)
        if not self.input_video.exists():
            parser.error("video not exists")
        else:
            print('--> split {}'.format(input_video))
        if out_dir:
            self.out_dir=Path(out_dir)
        else:
            self.out_dir = self.input_video.parent/self.input_video.stem
            print("--> out_dir mkd as {}".format(self.out_dir))
        self.out_dir.mkdir_p()
        self.cap = cv2.VideoCapture()
        self.cap.open(self.input_video)
        if not self.cap.isOpened():
            parser.error("Failed to open input video")
            return

        self.nums_frame = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.IS_RUNNING=True
        self.lock = Lock()
        self.frameCount=0
        self.frame_list = []
        self.writer= Writer((0,10))
        pass

    def capture(self):

        while(True):  # for frameId in tqdm(range(int(frameCount))):
            try:
                ret, frame = self.cap.read()
                self.frame_list.append(frame.copy())

            # print frameId, ret, frame.shape
            except:
                print("Failed to get the frame {f}".format(f=self.frameCount))
                break

        self.IS_RUNNING=False
        print('frame split over')

    def figsave(self):

        while(self.frameCount< self.nums_frame):
            self.lock.acquire()
            ofname = self.out_dir / '{:04d}.{}'.format(self.frameCount, args.save_ext)
            ret = cv2.imwrite(ofname, self.frame_list[0])
            self.frame_list.pop(0)
            self.frameCount += 1
            #self.writer.write('save {}'.format(self.frameCount))
            #print('save {}'.format(self.frameCount))
            self.lock.release()


        pass

    def run(self):
        print("--> frame num :{}".format(self.nums_frame))
        t1 = Thread(target=self.capture())

        t2 = Thread(target=self.figsave())




        t1.start()
        t2.start()









    #maxframes = args.maxframes
    #if args.maxframes and frameCount > maxframes:#跳帧决定
    #    skipDelta =int(frameCount / maxframes)#乡下取证
    #    if args.verbose:
    #        print("Video has {fc}, but maxframes is set to {mf}".format(fc=frameCount, mf=maxframes))
    #        print("Skip frames delta is {d}".format(d=skipDelta))
    #else:
    #    skipDelta = 1






    pass


if __name__ == "__main__":
    print("Start Video2Frames script ...")
    video2frame = Video2Frame(input_video=args.input_video,out_dir=args.out_dir,save_ext=args.save_ext)
    video2frame.run()
    print('programe over')