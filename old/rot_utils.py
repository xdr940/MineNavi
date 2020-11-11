import numpy as np
from math import atan2
import math
from  math import cos,acos,sin,asin,pi

EPS = 1e-8
def deg2rad(dg):
    circle,dg = np.divmod(dg,360)
    return circle*2*np.pi +dg/180*np.pi

def rad2deg(rd):
    circle,rd = np.divmod(rd, 2*np.pi)
    return circle*360 +rd/np.pi*180


def expmap2rotmat(r):
    """
    :param r: Axis-angle, Nx3, yaw pitch roll?
    :return: Rotation matrix, Nx3x3
    """
    assert r.shape[1] == 3
    bs = r.shape[0]
    theta = np.sqrt(np.sum(np.square(r), 1, keepdims=True))
    cos_theta = np.expand_dims(np.cos(theta), -1)
    sin_theta = np.expand_dims(np.sin(theta), -1)
    eye = np.tile(np.expand_dims(np.eye(3), 0), (bs, 1, 1))
    norm_r = r / (theta + EPS)
    r_1 = np.expand_dims(norm_r, 2)  # N, 3, 1
    r_2 = np.expand_dims(norm_r, 1)  # N, 1, 3
    zero_col = np.zeros([bs, 1]).astype(r.dtype)
    skew_sym = np.concatenate([zero_col, -norm_r[:, 2:3], norm_r[:, 1:2],
                               norm_r[:, 2:3], zero_col,-norm_r[:, 0:1],
                               -norm_r[:, 1:2], norm_r[:, 0:1], zero_col], 1)
    skew_sym = skew_sym.reshape(bs, 3, 3)
    R = cos_theta*eye + (1-cos_theta)*np.einsum('npq,nqu->npu', r_1, r_2) + sin_theta*skew_sym
    return R
def rotmat2expmap(R):
    """
    :param R: Rotation matrix, Nx3x3
    :return: r: Rotation vector, Nx3
    """
    assert len(R.shape)==2 or len(R.shape)==3#Nx3x3
    if len(R.shape)==3:
        assert R.shape[1] == R.shape[2] == 3
        theta = np.arccos(np.clip((R[:, 0, 0] + R[:, 1, 1] + R[:, 2, 2] - 1) / 2, -1., 1.)).reshape([-1, 1])+EPS
        r = np.stack((R[:, 2, 1]-R[:, 1, 2], R[:, 0, 2]-R[:, 2, 0], R[:, 1, 0]-R[:, 0, 1]), 1) / (2*np.sin(theta))
        r_norm = r / (np.sqrt(np.sum(np.square(r), 1, keepdims=True))+EPS)
        return theta * r_norm
    if len(R.shape)==2:
        assert R.shape[0] == R.shape[1] == 3
        theta = np.arccos(np.clip((R[ 0, 0] + R[ 1, 1] + R[ 2, 2] - 1) / 2, -1., 1.)).reshape([-1, 1])+EPS
        r = np.stack((R[ 2, 1]-R[ 1, 2], R[ 0, 2]-R[ 2, 0], R[ 1, 0]-R[ 0, 1]), 0) / (2*np.sin(theta))
        r_norm = r / (np.sqrt(np.sum(np.square(r), 1, keepdims=True))+EPS)
        return (theta * r_norm).squeeze(axis=0)


def quat2expmap(quat):
    """
    :param q: quaternion, Nx4
    :return: r: Axis-angle, Nx3
    """
    assert quat.shape[1] == 4
    cos_theta_2 = np.clip(quat[:, 0: 1], -1., 1.)
    theta = np.arccos(cos_theta_2)*2
    sin_theta_2 = np.sqrt(1-np.square(cos_theta_2))
    r = theta * quat[:, 1:4] / (sin_theta_2 + EPS)
    return r
def expmap2quat(r):
    """
    :param r: Axis-angle, Nx3
    :return: q: quaternion, Nx4
        """
    assert r.shape[1] == 3
    theta = np.sqrt(np.sum(np.square(r), 1, keepdims=True))
    unit_r = r / theta
    theta_2 = theta / 2.
    cos_theta_2 = np.cos(theta_2)
    sin_theta_2 = np.sin(theta_2)
    q = np.concatenate((cos_theta_2, unit_r*sin_theta_2), 1)
    return q



def eular2rotmat(eular_rad,mode='xyz'):
    #def euler2mat(angle):
    """Convert euler angles to rotation matrix.
     Reference: https://github.com/pulkitag/pycaffe-utils/blob/master/rot_utils.py#L174
    Args:
        angle: rotation angle along 3 axis (in radians) -- size = [B, 3]
    Returns:
        Rotation matrix corresponding to the euler angles -- size = [B, 3, 3]
    """
    B = eular_rad.shape[0]
    rx, ry, rz = eular_rad[:, 0], eular_rad[:, 1], eular_rad[:, 2]
    #roll,pitch,yaw

    cosz = np.cos(rz)
    sinz = np.sin(rz)

    zeros = rz * 0
    ones = zeros + 1
    zmat = np.stack([cosz, -sinz, zeros,
                     sinz, cosz, zeros,
                     zeros, zeros, ones], axis=1).reshape([B, 3, 3])

    cosy = np.cos(ry)
    siny = np.sin(ry)

    ymat = np.stack([cosy, zeros, siny,
                    zeros, ones, zeros,
                    -siny, zeros, cosy], axis=1).reshape([B, 3, 3])

    cosx = np.cos(rx)
    sinx = np.sin(rx)

    xmat = np.stack([ones, zeros, zeros,
                     zeros, cosx, -sinx,
                     zeros, sinx, cosx], axis=1).reshape([B, 3, 3])

    rotMat = zmat@ymat @xmat
    return rotMat
def rotmat2eular2(rotmat, cy_thresh=None, seq='xyz'):
    #超过90d全部拉跨

        _FLOAT_EPS_4 = np.finfo(float).eps * 4.0
        M = np.asarray(rotmat)
        if cy_thresh is None:
            try:
                cy_thresh = np.finfo(M.dtype).eps * 4
            except ValueError:
                cy_thresh = _FLOAT_EPS_4



        r11, r12, r13, r21, r22, r23, r31, r32, r33 = M.flat
        # cy: sqrt((cos(y)*cos(z))**2 + (cos(x)*cos(y))**2)
        cy = math.sqrt(r32 * r32 + r33 * r33)
        if seq == 'zyx':
            if cy > cy_thresh:  # cos(y) not close to zero, standard form
                z = math.atan2(-r12, r11)  # atan2(cos(y)*sin(z), cos(y)*cos(z))
                y = math.atan2(r13, cy)  # atan2(sin(y), cy)
                x = math.atan2(-r23, r33)  # atan2(cos(y)*sin(x), cos(x)*cos(y))
            else:  # cos(y) (close to) zero, so x -> 0.0 (see above)
                # so r21 -> sin(z), r22 -> cos(z) and
                z = math.atan2(r21, r22)
                y = math.atan2(r13, cy)  # atan2(sin(y), cy)
                x = 0.0
            eular = np.array([z,y,x])
        elif seq == 'xyz':
            if cy > cy_thresh:
                x = math.atan2(r32, r33)
                y = math.atan2(-r31, cy)
                z = math.atan2(r21, r11)
            else:
                z = 0.0
                if r31 < 0:
                    y = np.pi / 2
                    x = atan2(r12, r13)
                else:
                    y = -np.pi / 2
                # x =
            eular = np.array([x,y,z])

        return eular
def rotmat2eular(rotmat):
    poses_6dof = []
    for idx, item in enumerate(rotmat):
        T11, T12, T13,T21, T22, T23, T31, T32, T33 = item.reshape([9])

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

        # pitch = pitch / pi * 360
        # roll = roll / pi * 360
        # yaw = yaw / pi * 360

        #x = T14
        #y = T24
        #z = T34
        poses_6dof.append([pitch, yaw, roll])#, x, y, z])

    return poses_6dof



def eular2quat(eular_rad):
    B = eular_rad.shape[0]
    rx, ry, rz = eular_rad[:, 0], eular_rad[:, 1], eular_rad[:, 2]

    z = rz / 2.0
    y = ry / 2.0
    x = rx / 2.0
    cz = np.cos(z)
    sz = np.sin(z)
    cy = np.cos(y)
    sy = np.sin(y)
    cx = np.cos(x)
    sx = np.sin(x)
    ret = np.array([
        cx * cy * cz - sx * sy * sz,
        cx * sy * sz + cy * cz * sx,
        cx * cz * sy - sx * cy * sz,
        cx * cy * sz + sx * cz * sy]).transpose([1,0])
    return ret


if __name__ == '__main__':

    eulardeg = np.array([11,13,10,2,4,5]).reshape([2,3])
    eularad = deg2rad(eulardeg)


    quat = eular2quat(eularad)


    #rotmat = eular2rotmat(eularad)
    #rot_rad_ = rotmat2eular(rotmat)

    #eular_deg_ = rad2deg(eular_rad_)
    #print(rotmat)

    print(quat)

