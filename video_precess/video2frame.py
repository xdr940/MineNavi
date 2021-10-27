__author__ = 'vfdev'

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
import numpy as np

parser = argparse.ArgumentParser(description="Video2Frames converter")
parser.add_argument('--input', default='/home/roit/bluep2/datasets/fpv_videos/fpv.mp4', help="Input video file")
parser.add_argument('--output', default='/home/roit/bluep2/datasets/fpv_full2', help="Output folder. If exists it will be removed")
parser.add_argument('--skip',default=1,help="minimum 1 is normal")
parser.add_argument('--ext',default='png')
parser.add_argument('--rotate', type=int, default=0, choices={0,90, 180, 270}, help="Rotate clock-wise output frames")
parser.add_argument('--exifmodel', default=None, help="An example photo file to fill output meta-tags")
parser.add_argument('--verbose', default=True, action='store_true', help="Enable verbose")

args = parser.parse_args()

def main():
    global args

    #io check
    root = Path(args.input)
    print(root)

    in_path = Path(args.input)
    if not in_path.exists():
        parser.error("Input video file is not found")
        return 1
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(in_path.stem)

    out_path.makedirs_p()  # without exception 'already exist'






    cap = cv2.VideoCapture()
    cap.open(args.input)
    if not cap.isOpened():
        parser.error("Failed to open input video")
        return 1

    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)#视频最大能切分几张

    if args.verbose:
        print(frameCount)
    skipDelta = args.skip

    #maxframes = args.maxframes
    #if args.maxframes and frameCount > maxframes:#跳帧决定
    #    skipDelta =int(frameCount / maxframes)#乡下取证
    #    if args.verbose:
    #        print("Video has {fc}, but maxframes is set to {mf}".format(fc=frameCount, mf=maxframes))
    #        print("Skip frames delta is {d}".format(d=skipDelta))
    #else:
    #    skipDelta = 1

    frameId = 0
    # rotateAngle
    rotateAngle = args.rotate if args.rotate else 0

    if rotateAngle > 0 and args.verbose:
        print("Rotate output frames on {deg} clock-wise".format(deg=rotateAngle))

    #exif_model
    exif_model=None
    if args.exifmodel:
        if not os.path.exists(args.exifmodel):
            parser.error("Exif model file '{f}' is not found".format(f=args.exifmodel))
            return 2
        if args.verbose:
            print("Use exif model from file : {f}".format(f=args.exifmodel))
        ret = subprocess.Popen(['exiftool', '-j', os.path.abspath(args.exifmodel)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = ret.communicate()
        if args.verbose:
            print("exiftool stdout : ", out)
        try:
            exif_model = json.loads(out)[0]
        except ValueError:
            parser.error("Exif model file can not be decoded")
            return 2
    #main cycle
    #while frameId < frameCount:
    f_cnt = 1#output num of frames
    while frameId < frameCount :    #for frameId in tqdm(range(int(frameCount))):
        # cap.set(cv2.CAP_PROP_POS_FRAMES,frameId)
        ret, frame = cap.read()
        # print frameId, ret, frame.shape
        if not ret:
            print("Failed to get the frame {f}".format(f=frameId))
            continue



        ofname = out_path/'{:05d}.{}'.format(f_cnt-1,args.ext)#补零操作
        ret = cv2.imwrite(ofname, frame)
        if not ret:
            print("Failed to write the frame {f}".format(f=frameId))
            continue

        frameId += int(skipDelta)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frameId)
        f_cnt += 1


    #post precess
    if exif_model:
        fields = ['Model', 'Make', 'FocalLength']
        if not write_exif_model(os.path.abspath(out_path), exif_model, fields):
            print("Failed to write tags to the frames")
        # check on the first file
        fname = os.path.join(os.path.abspath(out_path), 'frame_0.jpg')
        cmd = ['exiftool', '-j', fname]
        for field in fields:
            cmd.append('-' + field)
        ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = ret.communicate()
        if args.verbose:
            print("exiftool stdout : ", out)
        try:
            result = json.loads(out)[0]
            for field in fields:
                if field not in result:
                    parser.error("Exif model is not written to the output frames")
                    return 3
        except ValueError:
            parser.error("Output frame exif info can not be decoded")
            return 2

    return 0


def write_exif_model(folder_path, model, fields=None):
    cmd = ['exiftool', '-overwrite_original', '-r']
    for field in fields:
        if field in model:
            cmd.append('-' + field + "=" + model[field])
    cmd.append(folder_path)
    ret = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = ret.communicate()
    return ret.returncode == 0 and len(err) == 0


if __name__ == "__main__":
    print("Start Video2Frames script ...")
    ret = main()
    exit(ret)