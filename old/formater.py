'''
formats(numpy):

kitti:    Nx12
mc:       Nx7(timestamp,roll,pitch,yaw,x,y,z)
mat34:    Nx3x4



rots:

eular:     Nx3
quat:      Nx4
vec:       Nx3
mat:       Nx3x3
angle-axis Nx4
'''

import math
import numpy as np
from  math import cos, sin,asin,pi
from utils.rot_utils import rotmat2eular,eular2rotmat





def rot2cvec(rot3):
    yaw,pitch,roll = rot3[:,0],rot3[:,1],rot3[:,2]
    yaw = -yaw
    pitch = -pitch
    x_ = np.sin(yaw)*np.cos(pitch)
    y_ = np.sin(yaw)*np.sin(pitch)
    z_ = np.cos(yaw)
    bottom = np.sqrt(x_**2+y_**2+z_**2)
    x_ = np.expand_dims(x_/bottom,axis=1)
    y_ = np.expand_dims(y_/bottom,axis=1)
    z_ = np.expand_dims(z_/bottom,axis=1)
    color =roll/2/np.pi +0.5 #[-180,180]-->[0,1] for colormap 处理
    color = np.expand_dims(color,axis=1)
    ret = np.concatenate([x_,y_,z_,color],axis=1)


    return ret


def readlines(filename):
    """Read all the lines in a text file and return as a list
    """
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    i=0
    while(i<len(lines)):
        if lines[i][0]=='#':
            lines.pop(i)
            i-=1
        i+=1
    i=0
    ret =[]
    while(i<len(lines)):
        ret.append(lines[i].split(','))
        if len(ret[i])==1:
            ret[i] = float(ret[i][0])
        else:

            for j in range(len(ret[i])):
                ret[i][j] = float(ret[i][j])
        i+=1


    return ret


# def readjson(path):
#     f = open(path, encoding='utf-8')
#     content = f.read()
#     dict = json.loads(content)
#     return  dict

# def str2pose_6dof(pose_kitti):
#     pose_mat_12 = np.array([float(item) for item in pose_kitti.split(' ')])
#     pose_mat_34 = pose_mat_12.reshape([3,4])
#     rot33 = pose_mat_34[:,:3]
#     rot3 = rotmat2expmap(rot33).reshape(3)
#     t = pose_mat_34[:,3].reshape(3)
#     pose_6dof = np.concatenate([rot3, t], axis=0)
#
#     return pose_6dof


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
def dof2matrix(poses):

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

        return  poses_format
def matrix2dof2(pose):
    T11, T12, T13, T14, T21, T22, T23, T24, T31, T32, T33, T34 = pose
    yaw = asin(T31)
    if T32 / (cos(yaw)) > 1:
        pitch = -asin(1)
    elif T32 / (cos(yaw)) < -1:
        pitch = -asin(-1)
    else:
        pitch = -asin(T32 / (cos(yaw)))

    if T21 / cos(yaw) < -1:
        roll = asin(-1.)
    elif T21 / cos(yaw) > 1:
        roll = asin(1.)
    else:
        roll = asin(T21 / cos(yaw))

    pitch = pitch / pi * 360
    roll = roll / pi * 360
    yaw = yaw / pi * 360

    x = T14
    y = T24
    z = T34
    return  [pitch,yaw,roll,x,y,z]

def matrix2dof(poses):
    poses_6dof =[]
    for idx,item in enumerate(poses):
        T11,T12,T13,T14,T21,T22,T23,T24,T31,T32,T33,T34 = item


        yaw = asin(T31)
        if T32/(cos(yaw))>1:
            pitch = -asin(1)
        elif T32/(cos(yaw))<-1:
            pitch = -asin(-1)
        else:
            pitch = -asin(T32/(cos(yaw)))

        if T21/cos(yaw)<-1:
            roll = asin(-1.)
        elif T21/cos(yaw)>1:
            roll = asin(1.)
        else:
            roll = asin(T21/cos(yaw))


        pitch =pitch/pi *360
        roll =roll/pi *360
        yaw =yaw/pi *360

        x = T14
        y=T24
        z=T34
        poses_6dof.append([pitch,yaw,roll,x,y,z])

    return poses_6dof

def pose6dof2kitti(pose6dof):
    '''
    eular2mat,
    :param poses:
    :return:
    '''
    eular_rad = pose6dof[:,:3]/360*2*np.pi
    rotmat =eular2rotmat(eular_rad)#3x3
    rotmat = np.round(rotmat, 8)#设置精度， 以防溢出
    #rot_vec = rotmat2expmap(rot_mat)
    position = np.expand_dims(pose6dof[:,3:],axis=2)
    poses_kitti = np.concatenate([rotmat,position],axis=2)#Nx12
    poses_kitti = poses_kitti.reshape([poses_kitti.shape[0],12])
    return poses_kitti


def kitti2pose6dof(poses_kitti):
    '''
    mat2eular
    :param poses_kitti:
    :return:
    '''
    assert len(poses_kitti.shape)==2
    mat34 = poses_kitti.reshape([poses_kitti.shape[0],3,4])
    rotmat = mat34[:,:,:3]
    rots = rotmat2eular(rotmat)
    rots = np.round(rots, 8)#设置精度， 以防溢出
    np.rad2deg(rotmat)
    position = mat34[:,:, 3]
    return np.concatenate([rots,position],axis=1)
