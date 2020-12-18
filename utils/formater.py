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
from  numpy import cos, sin,pi
from utils.rotation import rotmat2eular,eular2rotmat,rotmat2eular2
#
#
# def eular2cvec(eular,vmin=-pi,vmax=pi):
#     '''
#     rpy seq,radin
#     :param rot3:
#     :return:
#     '''
#
#     roll,pitch,yaw = eular[:,0],eular[:,1],eular[:,2]
#     thetaz = -yaw
#     thetay = pitch+np.pi/2
#     x_ = np.sin(thetay)*np.cos(thetaz)
#     y_ = np.sin(thetay)*np.sin(thetaz)
#     z_ = np.cos(thetay)
#
#     bottom = np.sqrt(x_**2+y_**2+z_**2)
#     x_ = np.expand_dims(x_/bottom,axis=1)
#     y_ = np.expand_dims(y_/bottom,axis=1)
#     z_ = np.expand_dims(z_/bottom,axis=1)
#
#     color =roll/(vmax-vmin)+0.5 #[-n*pi, n*pi] -> [-pi,pi]-->[0,1] for colormap 处理
#
#     color = np.expand_dims(color,axis=1)
#     cvec = np.concatenate([x_,y_,z_,color],axis=1)
#
#
#     return cvec

def eular2rotcoord(eular):
    # eular to coord
    cvec = eular2rotmat(eular)  # rpy
    # adjust
    cvec = cvec @ np.array([1, 0, 0,
                            0, 1, 0,
                            0, 0, 1]).reshape([3, 3])
    # due to left times
    cvec =  np.linalg.inv(cvec)

    return cvec




def mc2pose6dof(poses_mc):
    return poses_mc[:,1:]


def str2pose_6dof(pose_line,fmt='mc'):
    pose = np.array([float(item) for item in pose_line.split(' ')])

    if fmt=='mc':
        return pose[1:]

def line2np(str):
    '''
    :param pose: NxM
    :return:
    '''
    temp = './temp2.txt'
    ftemp = open(temp,'w')
    ftemp.write(str)
    ftemp.close()
    ret = np.loadtxt(temp)
    ret = np.expand_dims(ret,axis=0)
    return  ret

def np2line(pose):
    '''
    :param pose: NxM
    :return:
    '''
    temp = './temp.txt'
    np.savetxt(temp, pose,fmt='%.6e')
    ftemp = open(temp,'r')
    line = ftemp.readline()
    ftemp.close()
    return line




def pose6dof2kitti(pose6dof):
    '''
    eular2mat,
    :param poses:
    :return:
    '''
    eular_deg = pose6dof[:,:3]
    eular_rad = np.deg2rad(eular_deg)
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
    rots = np.rad2deg(rots)
    position = mat34[:,:, 3]
    return np.concatenate([rots,position],axis=1)


if __name__ == '__main__':
    arr = np.array([0,90,90,4,5,6]).reshape([1,6])
    kitti_  = pose6dof2kitti(arr)
    arr_ = kitti2pose6dof(kitti_)


    print(arr_)


