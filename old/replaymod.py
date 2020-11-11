
from path import Path
import argparse
import numpy as np
import json
import math
from scipy.interpolate import interp1d
from  math import cos,acos,sin,asin,pi
parser = argparse.ArgumentParser(description='KITTI evaluation')
parser.add_argument("--input_json",
                    default="./datasets/jsons/circle.json"
                    )
parser.add_argument('--steps',
                    help='ms, 不同路径名字对应着不同帧时间',
                    default={
                        'p1':1000,
                        'p1p':1000,
                        'p2':5000,
                        'p2p':1000,
                        'p3':5000,
                        'p4':5000,
                        'p5':1000,
                        'p6':2000,
                        'p6_2':2000,
                        'p6_3':2000,
                        'p7':1000
                        })
parser.add_argument("--out_dir",default=None)


args = parser.parse_args()

#json format: yaw pitch roll x, y, z
#_6dof formate pitch yaw roll x,y,z
def load_poses_from_txt(filename):
    poses=[]
    with open(filename,'r') as f:
        lines = f.readlines()
        for line in lines:
            pose = line.split()
            pose = [float(item) for item in pose]
            poses.append(pose)
        print('ok')

    return poses

def save_as_txt(filename,poses,shape='matrix'):
    #poses (n,3,4)
    with open(filename,'w') as f:
        for pose in poses:
            if shape=='matrix':
                #pose = pose.reshape([12])
                pose = str(pose).replace('\n',' ')
                f.writelines(pose[1:-1]+'\n')
            if shape =='6dof':
                pose = str(pose)
                f.writelines(pose[1:-1]+'\n')




class TimeLine():
    def __init__(self,options):
        self.input_json = Path(options.input_json)

        if args.out_dir:
            self.out_dir = Path(args.out_dir)
        else:
           self.out_dir = Path(self.input_json.stem + '_poses')
        self.out_dir.mkdir_p()


    def readjson(self,path):
        f = open(path, encoding='utf-8')
        content = f.read()
        dict = json.loads(content)
        return dict

    def interpolaration(self,key_poses_7dof_np,ms_per_frame):
        '''
            读取txt 然后进行插值， 并返回list
        :param path: "timelines_p1.txt"
        :return:
        '''
        #timelines = readlines(path)
        #out_p = path.stem+'_.txt'

        time = key_poses_7dof_np[:,0]
        pitch = key_poses_7dof_np[:,1]
        yaw = key_poses_7dof_np[:,2]
        roll = key_poses_7dof_np[:,3]

        x = key_poses_7dof_np[:,4]
        y = key_poses_7dof_np[:,5]
        z = key_poses_7dof_np[:,6]


        position = np.array([x,y,z]).transpose([1,0])
        rotation = np.array([pitch,yaw,roll]).transpose([1,0])

        time_full = np.linspace(start=0, stop=time.max(),num= time.max()/ms_per_frame +1)
        poses=[]
        for item in [pitch,yaw,roll,x,y,z]:

            interp = interp1d(time,item,kind='cubic')
            item_full = interp(time_full)
            poses.append(item_full[:-1])
        poses = np.array(poses).transpose([1,0])

        #ac = CatmulRom(alpha=0.5, n_step=steps)

        #position = ac.run3d(position)
        #rotation = ac.run3d(rotation)
        #poses = [rot + pos for rot,pos in zip(rotation,position)]
        #np format
        #position = np.array(position)
        #rotation = np.array(rotation)
        #poses = np.concatenate([rotation,position],axis=1)

        return ['pitch','yaw','roll','x','y','z'], poses

    def json2trajs(self,json_path):
        pass
        print('ok')

    def format2list(self,path_name):
        # path_name is a list
        num_frames = len(path_name[1]['keyframes'])
        traj_formated_dict = []
        frame = {}
        for i in range(num_frames):
            # frame['no'] = '{:07d}'.format(i)
            # frame['no'] = i
            if i==45:
                pass
            frame['time'] = path_name[1]['keyframes'][i]['time']
            frame['pitch'] = path_name[1]['keyframes'][i]['properties']['camera:rotation'][1]#%90
            frame['yaw'] = path_name[1]['keyframes'][i]['properties']['camera:rotation'][0]#%90
            frame['roll'] = path_name[1]['keyframes'][i]['properties']['camera:rotation'][2]#%90

            frame['x'] = path_name[1]['keyframes'][i]['properties']['camera:position'][0]
            frame['y'] = path_name[1]['keyframes'][i]['properties']['camera:position'][1]
            frame['z'] = path_name[1]['keyframes'][i]['properties']['camera:position'][2]

            traj_formated_dict.append(frame.copy())

        key_frames = []
        for frame in traj_formated_dict:
            frame_ = list(frame.values())
            key_frames.append(np.array(frame_))

        key_frames = np.array(key_frames)
        return key_frames
    def dof2matrix(self,poses):
        '''
        pitch, yaw, roll, x, y, z --> T11 T12 T13 T14 T21 T22 T23 T24 T31 T32 T33 T34
        :param poses:
        :return:
        '''

        def deg2raid(x):
            return x / 360 * math.pi
        poses_format =[]
        for pose in poses:
            pitch,yaw, roll, x, y, z = pose


            roll = deg2raid(roll)
            yaw = deg2raid(yaw)
            pitch = deg2raid(pitch)

            R_roll = [cos(roll),-sin(roll),0,
                    sin(roll),cos(roll),0,
                    0,             0,       1]
            R_pitch = [1,0,0,
                       0,cos(pitch),sin(pitch),
                       0,-sin(pitch),cos(pitch)]

            R_yaw = [cos(yaw),0,-sin(yaw),
                     0,1,0,
                     sin(yaw),0,cos(yaw)]

            R_roll = np.array(R_roll).reshape([3,3])
            R_yaw = np.array(R_yaw).reshape([3,3])
            R_pitch = np.array(R_pitch).reshape([3,3])

            R= R_roll@R_yaw@R_pitch
            t = np.array([x,y,z]).reshape([3,1])
            Rt = np.concatenate([R,t],axis=1)
            Rt = Rt.reshape(12)
            poses_format.append(Rt)
        poses_format = np.array(poses_format)
        return  poses_format
    def matrix2dof(self,poses):
        poses_6dof =[]
        for item in poses:
            T11,T12,T13,T14,T21,T22,T23,T24,T31,T32,T33,T34 = item
            pitch = acos(T33)
            roll = acos((-T23)/sin(pitch))
            yaw = acos(T32/sin(pitch))
            x = T14
            y=T24
            z=T34
            poses_6dof.append([pitch,yaw,roll,x,y,z])

        return poses_6dof

    def timestamp(self,length,ms=100):
        pass

        ret = np.linspace(num=length,start=0,stop=(length-1)*ms)
        ret = np.expand_dims(ret,axis=1)
        return  ret




    def run(self):
        trajs = self.readjson(self.input_json)#读取原始json文件

        for traj_name in trajs:
            if traj_name not in ['','none'] and traj_name in args.steps.keys():
                #steps = args.steps[traj_name]
                key_poses_7dof_np = self.format2list(trajs[traj_name])#第一次格式化
                names,poses_6dof = self.interpolaration(key_poses_7dof_np,ms_per_frame=100)
                full_times = self.timestamp(length = poses_6dof.shape[0],ms = 100)
                print('ok')
                poses_mat = self.dof2matrix(poses_6dof)#(n,3,4)

                np.savetxt(self.out_dir/traj_name+'_6dof.txt',poses_6dof,delimiter=' ', fmt='%1.8e')
                np.savetxt(self.out_dir/traj_name+'.txt',poses_mat,delimiter=' ', fmt='%1.8e')
                np.savetxt(self.out_dir/traj_name+'_times.txt',full_times/1000,delimiter='',fmt='%1.8e')

            else:
                continue









if __name__ == '__main__':
    timeline = TimeLine(args)
    timeline.run()
