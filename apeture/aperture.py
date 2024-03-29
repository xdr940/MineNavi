
from path import Path
import numpy as np
import json
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d

from utils.cubic_hermite import CubicHermite
from utils.formater import pose6dof2kitti






class Aperture():
    def __init__(self,input_json,out_dir,interp_type='hermite'):
        self.input_json = Path(input_json)
        self.out_dir = Path(out_dir)/self.input_json.stem
        self.out_dir.mkdir_p()
        self.eularmod = True
        if interp_type=='hermite':
            self.interp = CubicHermite
        elif interp_type =='linear':
            self.interp = interp1d


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
        pitch = -key_poses_xdof_np[:,1]
        yaw =   key_poses_xdof_np[:,2]

        x = key_poses_xdof_np[:,5]#z
        y = key_poses_xdof_np[:,3]#x
        z = key_poses_xdof_np[:,4]#y
        #fov = key_poses_7dof_np[:,6]


        time = np.linspace(start=0, stop=self.duration_ms,num= self.num_frames)
        time_full = np.linspace(start=0, stop=self.duration_ms,num= self.duration_ms/ms_per_frame+1 )


        poses=[]
        for item in [roll,pitch,yaw,x,y,z]:
            interpf = self.interp(time,item)
            item_full = interpf(time_full)
            poses.append(item_full)

        #curves color




        poses_6dof_np = np.array(poses).transpose([1,0])




        return time_full,poses_6dof_np

    def save_curves(self,time_full,poses_6dof):
        names = ['roll', 'pitch', 'yaw', 'x', 'y', 'z']
        curve_color = ['r', 'g', 'b', 'c', 'm', 'cyan']
        idx=0
        plt.figure(figsize=[10,5])
        plt.subplot(1,2,1)
        poses_6dof=poses_6dof.transpose([1,0])
        for dof in poses_6dof[:3]:
            plt.plot(time_full,dof, curve_color[idx])
            idx += 1
        plt.legend(names[:3])
        plt.ylabel('rotation(deg)')
        plt.xlabel('time(ms)')


        plt.subplot(1,2,2)
        for dof in poses_6dof[3:]:
            plt.plot(time_full,dof, curve_color[idx])
            idx += 1
        plt.legend(names[3:])
        plt.xlabel('time(ms)')
        plt.ylabel('postion(m)')

        plt.savefig(self.out_dir/'curves.png')


    def EularMod(self,full_poses6dof):
        full_poses6dof[:,:3] = np.mod(full_poses6dof[:,:3],360)
        return full_poses6dof



    def aptPath2pose6dof(self,points):
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

            point_ls.append(point['point']['x'])#x
            point_ls.append(point['point']['y'])#y
            point_ls.append(point['point']['z'])#z
            #z minecraft is using aircraft-coordination sys, change it to ground-coord sys


            points_ls.append(point_ls)

        points_np = np.array(points_ls)
        return points_np

    def aptKeyframe2pose6dof(self,points):
        pass

    def __call__(self,type='apt_path',out_format='mc'):

        dict = self.json2dict(self.input_json)  # 读取原始json文件
        main_dict = dict['fixtures'][0]
        traj_name = main_dict['name']

        # json ==> pose6dof_keypoints
        if type=='apt_path':
            points = main_dict['points']
            self.duration_ms = int(main_dict['duration'])#duration 400, 默认为400张图,时间就默认为100ms/frame
            self.num_frames = len(points)
            pose6dof_keypoints = self.aptPath2pose6dof(points)
        elif type=='apt_keyframe':
            self.duration = main_dict['duration']
            #todo
            pass

        # interpolation
        timestamp,poses_6dof = self.interpolaration_xdof(pose6dof_keypoints,ms_per_frame=1)


        if self.eularmod:
            poses_6dof = self.EularMod(poses_6dof)

        self.save_curves(timestamp,poses_6dof)


        #save the path to txt-file with mc-format or kitti-format
        if out_format =='mc':
            timestamp=np.expand_dims(timestamp,axis=1)
            poses_mc = np.concatenate([timestamp,poses_6dof],axis=1)
            np.savetxt(self.out_dir/'time_poses.txt',poses_mc,delimiter=' ', fmt='%1.8e')
        elif out_format =='kitti':
            poses_kitti = pose6dof2kitti(poses_6dof)#(n,3,4)
            np.savetxt(self.out_dir/'{}_kitti.txt'.format(traj_name),poses_kitti,delimiter=' ', fmt='%1.8e')







