__author__ = 'vfdev'

# Python
import argparse
import matplotlib.pyplot as plt
from path import Path
from tqdm import tqdm
import cv2
import numpy as np

parser = argparse.ArgumentParser(description="Video2Frames converter")
parser.add_argument('--input',
                    default='/home/roit/bluep2/datasets/fpv_videos',
                    help="Input video file")
parser.add_argument('--output',
                    default="/home/roit/bluep2/datasets/fpv",
                    help="Output folder. If exists it will be removed")
parser.add_argument('--videos2frames_log',
                    default='./videos2frames_log.txt',
                    )
parser.add_argument('--resize',default=False)


args = parser.parse_args()

def main():
    global args


    in_path = Path(args.input)



    if not in_path.exists():
        parser.error("Input video file is not found")
        return 1
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path('scences_frame')

    out_path.makedirs_p()

    seqs = open(args.videos2frames_log)
    seq_names = []
    for line in seqs:
        if line[0] != '#':
            seq_names.append(line.strip('\n'))
    seq_names.sort()
    print('处理场景{}个\n'.format(len(seq_names)))

    cap = cv2.VideoCapture()




    for seq in seq_names:
        file = in_path/seq

        cap.open(file)
        if not cap.isOpened():
            parser.error("Failed to open input video {}".format(file))
            continue
        traj,shader = file.stem.split('_')
        # if (out_path/traj/shader).exists():
        #     continue
        (out_path/traj/shader).makedirs_p()

        frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)#视频最大能切分几张



        for frameId in tqdm(range(int(frameCount))):
            ret, frame = cap.read()
            # print frameId, ret, frame.shape
            if not ret:
                print("Failed to get the frame {f}".format(f=frameId))
                continue

            # Rotate if needed:

            ofname = out_path / traj/shader/ '{:05d}.png'.format(frameId)  # 补零操作




            if args.resize:
                frame = cv2.resize(frame, (1024, 768))

            ret = cv2.imwrite(ofname, frame)

            if not ret:
                print("Failed to write the frame {f}".format(f=frameId))
                continue

    #post precess
    print('\n Over')
    return 0




if __name__ == "__main__":
    print("Start Video2Frames script ...")
    ret = main()
    exit(ret)

