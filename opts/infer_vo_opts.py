

import argparse

class infer_vo_opts:
    def __init__(self):


        self.parser = argparse.ArgumentParser(description='Script for visualizing depth map and masks',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.add_argument("--pretrained-posenet",
                            type=str, help="pretrained PoseNet path",
                            #default="/home/roit/models/SCBian/exp_pose_model_best.pth",
                            #default='/home/roit/models/SCBian/dispnet_model_best.pth'
                            default='/home/roit/models/SCBian_official/k_pose.tar'
                            )
        self.parser.add_argument('--scale_factor',default=32.4)

        self.parser.add_argument("--img-height", default=256, type=int, help="Image height")
        self.parser.add_argument("--img-width", default=832, type=int, help="Image width")
        self.parser.add_argument("--dataset-dir", type=str, help="Dataset directory",
                            #default='/mnt/datasets/kitti_odo_gray/dataset/sequences/'
                            #default='/home/roit/bluep2/datasets/kitti_odo_color/sequences/',
                            default="/home/roit/datasets/MC/0000/p1/color"#mc

                            )
        self.parser.add_argument("--output-dir", type=str,
                            help="Output directory for saving predictions in a big 3D numpy file",
                            default='./pred')
        self.parser.add_argument("--img-exts", default=['png', 'jpg', 'bmp'],
                            nargs='*', type=str, help="images extensions to glob")
        self.parser.add_argument('--type',default='color',choices=['gray','color'])
        self.parser.add_argument("--sequence", default='03',
                            type=str, help="sequence to test")

        self.parser.add_argument("--split",default='mc',choices=['kitti','mc'])

        self.parser.add_argument("--save_fmt",default='pose6dof',choices=['pose6dof','kitti'])

    def parse(self):
        self.options = self.parser.parse_args()
        return self.options