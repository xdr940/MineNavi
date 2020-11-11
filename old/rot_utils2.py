## @package rot_utils
#  Util functions for dealing with rotations
#

import scipy.io as sio
import numpy as np
from scipy import linalg as linalg
import sys, os
import pdb
import math
from mpl_toolkits.mplot3d import Axes3D

_FLOAT_EPS_4 = np.finfo(float).eps * 4.0


##
# Convert degrees to radians
def deg2rad(dg):
    dg = np.mod(dg, 360)
    if dg > 180:
        dg = -(360 - dg)
    return ((np.pi) / 180.) * dg



def angle_axis_to_rotmat(theta, v):
    '''
           Given the axis v, and a rotation theta - convert it into rotation matrix
           theta needs to be in radian
       '''
    def axis_to_skewsym(v):
        '''
            Converts an axis into a skew symmetric matrix format.
        '''
        v = v / np.linalg.norm(v)
        vHat = np.zeros((3, 3))
        vHat[0, 1], vHat[0, 2] = -v[2], v[1]
        vHat[1, 0], vHat[1, 2] = v[2], -v[0]
        vHat[2, 0], vHat[2, 1] = -v[1], v[0]

        return vHat

    assert theta >= 0 and theta < np.pi, "Invalid theta"

    vHat = axis_to_skewsym(v)
    vHatSq = np.dot(vHat, vHat)
    # Rodrigues Formula
    rotMat = np.eye(3) + math.sin(theta) * vHat + (1 - math.cos(theta)) * vHatSq
    return rotMat


def rotmat_to_angle_axis(rotMat):
    '''
        Converts a rotation matrix into angle axis format
    '''
    aa = linalg.logm(rotMat)
    aa = (aa - aa.transpose()) / 2.0
    v1, v2, v3 = -aa[1, 2], aa[0, 2], -aa[0, 1]
    v = np.array((v1, v2, v3))
    theta = np.linalg.norm(v)
    if theta > 0:
        v = v / theta
    return theta, v


##
# Convert Euler matrices into a rotation matrix.
def euler2mat(z=0, y=0, x=0, isRadian=True):
    ''' Return matrix for rotations around z, y and x axes

    Uses the z, then y, then x convention above

    Parameters
    ----------
    z : scalar
         Rotation angle in radians around z-axis (performed first)
    y : scalar
         Rotation angle in radians around y-axis
    x : scalar
         Rotation angle in radians around x-axis (performed last)

    Returns
    -------
    M : array shape (3,3)
         Rotation matrix giving same rotation as for given angles

    Examples
    --------
    # >>> zrot = 1.3 # radians
    # >>> yrot = -0.1
    # >>> xrot = 0.2
    # >>> M = euler2mat(zrot, yrot, xrot)
    # >>> M.shape == (3, 3)
    # True
    #
    # The output rotation matrix is equal to the composition of the
    # individual rotations
    #
    # >>> M1 = euler2mat(zrot)
    # >>> M2 = euler2mat(0, yrot)
    # >>> M3 = euler2mat(0, 0, xrot)
    # >>> composed_M = np.dot(M3, np.dot(M2, M1))
    # >>> np.allclose(M, composed_M)
    # True
    #
    # You can specify rotations by named arguments
    #
    # >>> np.all(M3 == euler2mat(x=xrot))
    # True
    #
    # When applying M to a vector, the vector should column vector to the
    # right of M.  If the right hand side is a 2D array rather than a
    # vector, then each column of the 2D array represents a vector.
    #
    # >>> vec = np.array([1, 0, 0]).reshape((3,1))
    # >>> v2 = np.dot(M, vec)
    # >>> vecs = np.array([[1, 0, 0],[0, 1, 0]]).T # giving 3x2 array
    # >>> vecs2 = np.dot(M, vecs)
    #
    # Rotations are counter-clockwise.
    #
    # >>> zred = np.dot(euler2mat(z=np.pi/2), np.eye(3))
    # >>> np.allclose(zred, [[0, -1, 0],[1, 0, 0], [0, 0, 1]])
    # True
    # >>> yred = np.dot(euler2mat(y=np.pi/2), np.eye(3))
    # >>> np.allclose(yred, [[0, 0, 1],[0, 1, 0], [-1, 0, 0]])
    # True
    # >>> xred = np.dot(euler2mat(x=np.pi/2), np.eye(3))
    # >>> np.allclose(xred, [[1, 0, 0],[0, 0, -1], [0, 1, 0]])
    True

    Notes
    -----
    The direction of rotation is given by the right-hand rule (orient
    the thumb of the right hand along the axis around which the rotation
    occurs, with the end of the thumb at the positive end of the axis;
    curl your fingers; the direction your fingers curl is the direction
    of rotation).  Therefore, the rotations are counterclockwise if
    looking along the axis of rotation from positive to negative.
    '''

    if not isRadian:
        z = ((np.pi) / 180.) * z
        y = ((np.pi) / 180.) * y
        x = ((np.pi) / 180.) * x
    assert z >= (-np.pi) and z < np.pi, 'Inapprorpriate z: %f' % z
    assert y >= (-np.pi) and y < np.pi, 'Inapprorpriate y: %f' % y
    assert x >= (-np.pi) and x < np.pi, 'Inapprorpriate x: %f' % x

    Ms = []
    if z:
        cosz = math.cos(z)
        sinz = math.sin(z)
        Ms.append(np.array(
            [[cosz, -sinz, 0],
             [sinz, cosz, 0],
             [0, 0, 1]]))
    if y:
        cosy = math.cos(y)
        siny = math.sin(y)
        Ms.append(np.array(
            [[cosy, 0, siny],
             [0, 1, 0],
             [-siny, 0, cosy]]))
    if x:
        cosx = math.cos(x)
        sinx = math.sin(x)
        Ms.append(np.array(
            [[1, 0, 0],
             [0, cosx, -sinx],
             [0, sinx, cosx]]))
    if Ms:
        return reduce(np.dot, Ms[::-1])
    return np.eye(3)


def mat2euler(M, cy_thresh=None, seq='zyx'):
    '''
    Taken Forom: http://afni.nimh.nih.gov/pub/dist/src/pkundu/meica.libs/nibabel/eulerangles.py
    Discover Euler angle vector from 3x3 matrix

    Uses the conventions above.

    Parameters
    ----------
    M : array-like, shape (3,3)
    cy_thresh : None or scalar, optional
         threshold below which to give up on straightforward arctan for
         estimating x rotation.  If None (default), estimate from
         precision of input.

    Returns
    -------
    z : scalar
    y : scalar
    x : scalar
         Rotations in radians around z, y, x axes, respectively

    Notes
    -----
    If there was no numerical error, the routine could be derived using
    Sympy expression for z then y then x rotation matrix, which is::

        [                       cos(y)*cos(z),                       -cos(y)*sin(z),         sin(y)],
        [cos(x)*sin(z) + cos(z)*sin(x)*sin(y), cos(x)*cos(z) - sin(x)*sin(y)*sin(z), -cos(y)*sin(x)],
        [sin(x)*sin(z) - cos(x)*cos(z)*sin(y), cos(z)*sin(x) + cos(x)*sin(y)*sin(z),  cos(x)*cos(y)]

    with the obvious derivations for z, y, and x

         z = atan2(-r12, r11)
         y = asin(r13)
         x = atan2(-r23, r33)

    for x,y,z order
        y = asin(-r31)
        x = atan2(r32, r33)
    z = atan2(r21, r11)


    Problems arise when cos(y) is close to zero, because both of::

         z = atan2(cos(y)*sin(z), cos(y)*cos(z))
         x = atan2(cos(y)*sin(x), cos(x)*cos(y))

    will be close to atan2(0, 0), and highly unstable.

    The ``cy`` fix for numerical instability below is from: *Graphics
    Gems IV*, Paul Heckbert (editor), Academic Press, 1994, ISBN:
    0123361559.  Specifically it comes from EulerAngles.c by Ken
    Shoemake, and deals with the case where cos(y) is close to zero:

    See: http://www.graphicsgems.org/

    The code appears to be licensed (from the website) as "can be used
    without restrictions".
    '''
    M = np.asarray(M)
    if cy_thresh is None:
        try:
            cy_thresh = np.finfo(M.dtype).eps * 4
        except ValueError:
            cy_thresh = _FLOAT_EPS_4
    r11, r12, r13, r21, r22, r23, r31, r32, r33 = M.flat
    # cy: sqrt((cos(y)*cos(z))**2 + (cos(x)*cos(y))**2)
    cy = math.sqrt(r33 * r33 + r23 * r23)
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
    elif seq == 'xyz':
        if cy > cy_thresh:
            y = math.atan2(-r31, cy)
            x = math.atan2(r32, r33)
            z = math.atan2(r21, r11)
        else:
            z = 0.0
            if r31 < 0:
                y = np.pi / 2
                x = atan2(r12, r13)
            else:
                y = -np.pi / 2
            # x =
    else:
        raise Exception('Sequence not recognized')
    return z, y, x


def euler2quat(z=0, y=0, x=0, isRadian=True):
    ''' Return quaternion corresponding to these Euler angles

    Uses the z, then y, then x convention above

    Parameters
    ----------
    z : scalar
         Rotation angle in radians around z-axis (performed first)
    y : scalar
         Rotation angle in radians around y-axis
    x : scalar
         Rotation angle in radians around x-axis (performed last)

    Returns
    -------
    quat : array shape (4,)
         Quaternion in w, x, y z (real, then vector) format

    Notes
    -----
    We can derive this formula in Sympy using:

    1. Formula giving quaternion corresponding to rotation of theta radians
         about arbitrary axis:
         http://mathworld.wolfram.com/EulerParameters.html
    2. Generated formulae from 1.) for quaternions corresponding to
         theta radians rotations about ``x, y, z`` axes
    3. Apply quaternion multiplication formula -
         http://en.wikipedia.org/wiki/Quaternions#Hamilton_product - to
         formulae from 2.) to give formula for combined rotations.
    '''

    if not isRadian:
        z = ((np.pi) / 180.) * z
        y = ((np.pi) / 180.) * y
        x = ((np.pi) / 180.) * x
    z = z / 2.0
    y = y / 2.0
    x = x / 2.0
    cz = math.cos(z)
    sz = math.sin(z)
    cy = math.cos(y)
    sy = math.sin(y)
    cx = math.cos(x)
    sx = math.sin(x)
    return np.array([
        cx * cy * cz - sx * sy * sz,
        cx * sy * sz + cy * cz * sx,
        cx * cz * sy - sx * cy * sz,
        cx * cy * sz + sx * cz * sy])


def quat2euler(q):
    ''' Return Euler angles corresponding to quaternion `q`

    Parameters
    ----------
    q : 4 element sequence
       w, x, y, z of quaternion

    Returns
    -------
    z : scalar
       Rotation angle in radians around z-axis (performed first)
    y : scalar
       Rotation angle in radians around y-axis
    x : scalar
       Rotation angle in radians around x-axis (performed last)

    Notes
    -----
    It's possible to reduce the amount of calculation a little, by
    combining parts of the ``quat2mat`` and ``mat2euler`` functions, but
    the reduction in computation is small, and the code repetition is
    large.
    '''
    # delayed import to avoid cyclic dependencies
    import nibabel.quaternions as nq
    return mat2euler(nq.quat2mat(q))

if __name__ == '__main__':

    rotdeg = np.array([11,13,10]).reshape([1,3])
    rotrad = deg2rad(rotdeg)



    rotmat = eular2rotmat(rotrad)
    rot_rad_ = rotmat2eular(rotmat)

    rotdeg_ = rad2deg(rot_rad_)