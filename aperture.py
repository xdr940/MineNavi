
from path import Path
import argparse
from utils.formater import pose6dof2kitti
import numpy as np
import json

import matplotlib.pyplot as plt
from utils.cubic_hermite import CubicHermite as interp1d

parser = argparse.ArgumentParser(description='MineCraft Aperture Tools')
parser.add_argument("--input_json",
                    default="./datasets/jsons/circle.json"# as traj_name
                    )
parser.add_argument("--out_dir",default='./data_out')
parser.add_argument("--traj_curve_out",default=True)
parser.add_argument("--out_format",default='mc',choices=['mc','kitti','tum','bag','euroc'])
args = parser.parse_args()


#
# def load_poses_from_txt(filename):
#     poses=[]
#     with open(filename,'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             pose = line.split()
#             pose = [float(item) for item in pose]
#             poses.append(pose)
#         print('ok')
#
#     return poses
#
# def save_as_txt(filename,poses,shape='matrix'):
#     #poses (n,3,4)
#     with open(filename,'w') as f:
#         for pose in poses:
#             if shape=='matrix':
#                 #pose = pose.reshape([12])
#                 pose = str(pose).replace('\n',' ')
#                 f.writelines(pose[1:-1]+'\n')
#             if shape =='6dof':
#                 pose = str(pose)
#                 f.writelines(pose[1:-1]+'\n')
#



class Aperture():
    def __init__(self,options):
        self.input_json = Path(options.input_json)
        self.out_dir = Path(args.out_dir)/self.input_json.stem
        self.out_dir.mkdir_p()


    def json2dict(self,path):
        '''
        json file 2 dict
        :param path:
        :return:
        '''
        f = open(path, encoding='utf-8')
        content = f.read()
        dict = json.loads(content)
        return dict

    def interpolaration_xdof(self,key_poses_xdof_np,ms_per_frame):
        '''
            读取txt 然后进行插值， 并返回list
        :param path: "timelines_p1.txt"
        :return:
        '''
        names = ['roll', 'pitch', 'yaw', 'x', 'y', 'z']
        roll = key_poses_xdof_np[:,0]
        pitch = key_poses_xdof_np[:,1]
        yaw = key_poses_xdof_np[:,2]

        x = key_poses_xdof_np[:,3]
        y = key_poses_xdof_np[:,4]
        z = key_poses_xdof_np[:,5]
        #fov = key_poses_7dof_np[:,6]


        time = np.linspace(start=0, stop=self.duration_ms,num= self.num_frames)
        time_full = np.linspace(start=0, stop=self.duration_ms,num= self.duration_ms/ms_per_frame+1 )


        poses=[]
        for item in [roll,pitch,yaw,x,y,z]:
            interp = interp1d(time,item)
            item_full = interp(time_full)
            poses.append(item_full)

        #curves color

        if args.traj_curve_out:
            curve_color = ['r', 'g', 'b', 'c', 'k', 'y']
            names = ['roll', 'pitch', 'yaw', 'x', 'y', 'z']
            idx=0
            plt.figure(figsize=[10,5])
            plt.subplot(1,2,1)
            for dof in poses[:3]:
                plt.plot(dof, curve_color[idx])
                idx += 1
            plt.legend(names[:3])

            plt.subplot(1,2,2)
            for dof in poses[3:]:
                plt.plot(dof, curve_color[idx])
                idx += 1
            plt.legend(names[3:])
            plt.savefig(self.out_dir/'curves.png')


        poses_6dof_np = np.array(poses).transpose([1,0])




        return time_full,poses_6dof_np




    def apature_points_dict_to_numpy(self,points):
        '''
        saved as rpy, zyx seq,
        :param points:
        :return:
        '''
        points_ls=[]
        for point in points:
            point_ls = []
            point_ls.append(point['angle']['roll'])#
            point_ls.append(point['angle']['pitch'])#
            point_ls.append(point['angle']['yaw'])#

            point_ls.append(point['point']['z'])#x
            point_ls.append(point['point']['x'])#y
            point_ls.append(point['point']['y'])#z
            #z minecraft is using aircraft-coordination sys, change it to ground-coord sys


            points_ls.append(point_ls)

        points_np = np.array(points_ls)
        return points_np




    def __call__(self):

        dict = self.json2dict(self.input_json)#读取原始json文件
        traj_name = dict['fixtures'][0]['name']
        points = dict['fixtures'][0]['points']
        self.duration_ms = int(dict['fixtures'][0]['duration']/20*1000)
        self.num_frames = len(points)


        pose6dof_keypoints = self.apature_points_dict_to_numpy(points)
        timestamp,poses_6dof = self.interpolaration_xdof(pose6dof_keypoints,ms_per_frame=100)


        if args.out_format =='mc':
            timestamp=np.expand_dims(timestamp,axis=1)
            poses_mc = np.concatenate([timestamp,poses_6dof],axis=1)
            np.savetxt(self.out_dir/'{}_mc.txt'.format(traj_name),poses_mc,delimiter=' ', fmt='%1.8e')
        elif args.out_format =='kitti':
            poses_kitti = pose6dof2kitti(poses_6dof)#(n,3,4)
            np.savetxt(self.out_dir/'{}_kitti.txt'.format(traj_name),poses_kitti,delimiter=' ', fmt='%1.8e')











if __name__ == '__main__':
    aperture = Aperture(args)
    aperture()
