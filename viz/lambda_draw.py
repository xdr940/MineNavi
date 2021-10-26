
from path import Path
from utils.formater import mc2pose6dof,kitti2pose6dof
from utils.formater import eular2rotcoord,vec_length
import numpy as np
import matplotlib.pyplot as plt

def norm(arr):
    max = arr.max()
    min = arr.min()

    arr = (arr-min)/(max-min)
    return arr

def drawer():
    PLOT2=True

    # poses_kitti = np.loadtxt("/home/roit/datasets/kitti_odo_poses/06.txt")
    # poses_6dof = kitti2pose6dof(poses_kitti,order='xyz')
    # out_str = 'kitti_09'
    # poses = np.loadtxt("/home/roit/datasets/mcv3/0001/time_poses.txt")
    poses = np.loadtxt("../data_out/mcv2/0000/time_poses.txt")

    poses_6dof = mc2pose6dof(poses)
    out_str='mcrandom_01'


    IS_NORM=True
    position = poses_6dof[:, 3:]  # xyz
    eular = np.deg2rad(poses_6dof[:, :3])  # Nx3
    rotcoord = eular2rotcoord(eular,'mc')  # rpy


    ts=[]
    phis=[]
    step =1
    for i in range(step, len(position)-step):
        delta_t =  position[i+step]-position[i-step]
        if IS_NORM:
            delta_t/=vec_length(delta_t)
        ts.append(delta_t)
        x,y,z = rotcoord[i, 0,0], rotcoord[i, 1,0], rotcoord[i, 2,0]
        delta_phi=np.array([x,y,z])
        if IS_NORM:

            delta_phi/=vec_length(delta_phi)

        phis.append(delta_phi)
    Lambda = []#np.array(t)*np.array(phi)

    ts=np.array(ts)
    phis=np.array(phis)
    Lambda = (ts*phis).sum(1)


    hist,bins = np.histogram(Lambda,range=[-1,1],bins=100)

    bins_hist = np.array([bins[:-1],hist])
    np.savetxt('./{}_bins_hist.txt'.format(out_str),bins_hist,fmt='%.3f', delimiter=',')
    np.savetxt('./{}_lambda.txt'.format(out_str),Lambda,fmt='%.3f',delimiter=',')
    # Lambda  /= (vec_length(ts)*vec_length(phis))
    # Lambda =abs(Lambda)
    #for i in range(len(t)):
    #    Lambda.append(abs(sum(t[i]*phi[i]/vec_length(t[i]*phi[i]))))

    if PLOT2:

        plt.figure(figsize=[8,4])
        plt.subplot(1,2,1)
        plt.plot(Lambda)
        # plt.ylim([-1.5,1.5])
        plt.subplot(1,2,2)
        plt.plot(bins[:-1],hist)
    else:
        plt.plot(Lambda)
        plt.title("The $\lambda$ of a random motion sequence")
        plt.xlabel('Frames(n)')
        plt.ylabel('$\lambda$')
        plt.scatter(x = [50,168,250],
                    y = [Lambda[50],Lambda[168],Lambda[250]],c='r')
        # plt.grid()

    plt.show()



    pass

if __name__ == '__main__':
    drawer()
    pass