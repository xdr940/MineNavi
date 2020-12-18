import numpy as np
from path import Path
import matplotlib as mpl
from matplotlib.animation import FuncAnimation  # 动图的核心函数
from  matplotlib.colors import  BoundaryNorm
import matplotlib.pyplot as plt
import time
import argparse
from mpl_toolkits.mplot3d import axes3d


from utils.formater import mc2pose6dof,kitti2pose6dof,pose6dof2kitti
from utils.formater import str2pose_6dof,eular2rotmat,eular2rotcoord
from utils.formater import line2np,np2line

parser = argparse.ArgumentParser(description='KITTI evaluation')
parser.add_argument("--input",
                    #default="./04001000_poses/p2p.txt"
                    #default="./data_out/rotline/_mc.txt"
                    default = "./data_out/rotcircle/_mc.txt"


)
parser.add_argument("--input_fmt",default='kitti',choices=['mc','kitti','tum','euroc'])

parser.add_argument("--azim_elev",default=[ -171,40  ],help='观察视角')
parser.add_argument("--out_dir",default='out_dir')
parser.add_argument('--interval_6dof',default=2)
parser.add_argument('--dynamic_outfile',default=False)
parser.add_argument('--dynamic_time_interval',default=0.1)
parser.add_argument('--real_time_interval',default=2)

parser.add_argument('--quiver_lenth',default=10)
parser.add_argument('--global_scale_factor',default=20.)
parser.add_argument('--file_pip',default='./data_out/just_fly/_mc.txt')
args = parser.parse_args()



class StaticDraw():
    def __init__(self,poses_6dof,flag_coord=True):
        fig = plt.figure(figsize=[10, 10])
        self.ax = fig.gca(projection='3d')
        self.ax.set_aspect('equal', adjustable='box')
        plt.axis('equal')

        # ax.yaxis.set_ticks_position('top')
        # ax.invert_xaxis()  # x 反方向
        # ax.invert_yaxis()  # x 反方向
        # ax.invert_zaxis()
        self.ax.set_xlabel('X')  # X不变
        self.ax.set_ylabel('y')  # yz交换
        self.ax.set_zlabel('z')  #

        self.position = poses_6dof[:, 3:]  # xyz
        eular = np.deg2rad(poses_6dof[:, :3])#Nx3

        eular_ = np.copy(eular)



        # MC USING LEFT HAND COORD SYSTEM
        # eular[:,0] = -eular_[:,1]#roll
        # eular[:,1] = -eular_[:,0]

        #del eular_


        #eular to rot coord
        self.rotcoord = eular2rotcoord(eular)  # rpy


        self.ax.azim, self.ax.elev = args.azim_elev
        plt.axis('equal')
        # plt.title('trajectory 80_00_1')
        self.mycmap = plt.get_cmap('hsv', 100)
        self.mynorm = mpl.colors.Normalize(vmin=-180, vmax=180)

        # 绘制起点,终点,其他点
        self.ax.scatter(self.position[0, 0], self.position[0, 1], self.position[0, 2], c='r')  # 起点绿色
        self.ax.scatter(self.position[-1, 0], self.position[-1, 1], self.position[-1, 2], c='g')  # 终点黄色

        # plt limits
        # ax.set_xlim3d([-100, 100])
        # ax.set_ylim3d([-100, 100])
        self.ax.set_zlim3d([150, 300])

        ceter_x = np.median(poses_6dof[:, 3])
        ceter_y = np.median(poses_6dof[:, 4])
        ceter_z = np.median(poses_6dof[:, 5])

        # 坐标系示意
        if flag_coord:
            self.ax.quiver(ceter_x, ceter_y, ceter_z, 1, 0, 0, length=20, color='r')
            self.ax.quiver(ceter_x, ceter_y, ceter_z, 0, 1, 0, length=20, color='g')
            self.ax.quiver(ceter_x, ceter_y, ceter_z, 0, 0, 1, length=20, color='b')

    def _point_plt(self,i):

        if i%self.interval==0:

            self.ax.plot(self.position[:i, 0], self.position[:i, 1], self.position[:i, 2], 'k-.')

            if self.dof=='6dof':
            #xyz to rgb
                self.ax.quiver(self.position[i, 0], self.position[i, 1], self.position[i, 2],
                               self.rotcoord[i, 0,0], self.rotcoord[i, 1,0], self.rotcoord[i, 2,0],
                               color='r',
                               norm=self.mynorm, normalize=True, length=10)
                self.ax.quiver(self.position[i, 0], self.position[i, 1], self.position[i, 2],
                               self.rotcoord[i, 0, 1], self.rotcoord[i, 1, 1], self.rotcoord[i, 2, 1],
                               color='g',
                               norm=self.mynorm, normalize=True, length=10)
                self.ax.quiver(self.position[i, 0], self.position[i, 1], self.position[i, 2],
                               self.rotcoord[i, 0, 2], self.rotcoord[i, 1, 2], self.rotcoord[i, 2, 2],
                               color='b',
                               norm=self.mynorm, normalize=True, length=10)

    def __call__(self,
                 dof='6dof',
                 interval=5):
        self.dof=dof
        self.interval=interval

        i = 0
        while i < self.position.shape[0]:
            if i % args.interval_6dof == 0:
                # 划黑线
                self._point_plt(i)
            i += 1


        # fig, ax2 = plt.subplots(figsize=(1.5, 4))
        # fig.subplots_adjust(right=0.4)
        # cb = mpl.colorbar.ColorbarBase(ax2,
        #                                cmap=self.mycmap,
        #                                norm=self.mynorm,
        #                                orientation='vertical')
        #
        # cb.set_label('roll angle (degree)')

        plt.show()




if __name__ == '__main__':
    poses = np.loadtxt(args.input)
    poses_6dof = mc2pose6dof(poses)

    pose_kitti = pose6dof2kitti(poses_6dof)
    poses_6dof_ = kitti2pose6dof(pose_kitti)

    #change to pose6dof
    # if args.input_fmt=='mc':
    #     poses_6dof =mc2pose6dof(poses)
    # elif args.input_fmt=='kitti':
    #     poses_6dof = kitti2pose6dof(poses)




    drawer = StaticDraw(poses_6dof)
    drawer(
        dof='6dof',
        interval=5
    )


