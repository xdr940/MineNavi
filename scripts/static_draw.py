import numpy as np
from path import Path
import matplotlib as mpl
from matplotlib.animation import FuncAnimation  # 动图的核心函数
from  matplotlib.colors import  BoundaryNorm
import matplotlib.pyplot as plt
import time
import argparse
from mpl_toolkits.mplot3d import axes3d
from utils.fio import readlines

from utils.formater import mc2pose6dof,kitti2pose6dof,pose6dof2kitti
from utils.formater import str2pose_6dof,eular2rotmat,eular2rotcoord
from utils.formater import line2np,np2line

parser = argparse.ArgumentParser(description='static draw')
parser.add_argument("--input",
                    #default="./04001000_poses/p2p.txt"
                    #default="./data_out/rotline/_mc.txt"
                    default = "./logs/mcv4.txt"


)
parser.add_argument("--input_fmt",default='mc',choices=['mc','kitti','tum','euroc'])

parser.add_argument("--azim_elev",default=[ -171,40  ],help='观察视角')
parser.add_argument("--out_dir",default='out_dir')
parser.add_argument('--interval_6dof',default=1)
parser.add_argument('--dynamic_outfile',default=False)
parser.add_argument('--dynamic_time_interval',default=0.1)
parser.add_argument('--real_time_interval',default=2)

parser.add_argument('--quiver_lenth',default=20)
parser.add_argument('--global_scale_factor',default=20.)
args = parser.parse_args()



class StaticDraw():
    def __init__(self,
                 flag_coord=True,
                 dof='6dof',
                 interval=5):
        self.dof = dof
        self.interval = interval

        fig = plt.figure(figsize=[10, 10])
        self.ax = fig.gca(projection='3d')
        self.ax.set_aspect('equal', adjustable='box')
        plt.axis('equal')
        self.flag_coord=flag_coord
        # ax.yaxis.set_ticks_position('top')
        # ax.invert_xaxis()  # x 反方向
        # ax.invert_yaxis()  # x 反方向
        # ax.invert_zaxis()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')

        self.firts_add=True





    def _point_plt(self,position,rotcoord,i):

        if i%self.interval==0:

            self.ax.plot(position[:i, 0], position[:i, 1], position[:i, 2], 'k-.')

            if self.dof=='6dof':
            #xyz to rgb
                self.ax.quiver(position[i, 0], position[i, 1], position[i, 2],
                               rotcoord[i, 0,0], rotcoord[i, 1,0], rotcoord[i, 2,0],
                               color='r',
                               norm=self.mynorm, normalize=True, length=10)
                self.ax.quiver(position[i, 0], position[i, 1], position[i, 2],
                               rotcoord[i, 0, 1], rotcoord[i, 1, 1], rotcoord[i, 2, 1],
                               color='g',
                               norm=self.mynorm, normalize=True, length=10)
                self.ax.quiver(position[i, 0], position[i, 1], position[i, 2],
                               rotcoord[i, 0, 2], rotcoord[i, 1, 2], rotcoord[i, 2, 2],
                               color='b',
                               norm=self.mynorm, normalize=True, length=10)

    def add_poses(self,poses_6dof):


        position = poses_6dof[:, 3:]  # xyz
        eular = np.deg2rad(poses_6dof[:, :3])  # Nx3

        # MC USING LEFT HAND COORD SYSTEM
        # eular[:,0] = -eular_[:,1]#roll
        # eular[:,1] = -eular_[:,0]

        # del eular_

        # eular to rot coord
        rotcoord = eular2rotcoord(eular)  # rpy

        self.ax.azim, self.ax.elev = args.azim_elev
        self.ax.axis('equal')
        # plt.title('trajectory 80_00_1')
        self.mycmap = plt.get_cmap('hsv', 100)
        self.mynorm = mpl.colors.Normalize(vmin=-180, vmax=180)

        # 绘制起点,终点,其他点
        self.ax.scatter(position[0, 0], position[0, 1], position[0, 2], c='r')  # 起点绿色
        self.ax.scatter(position[-1, 0], position[-1, 1], position[-1, 2], c='g')  # 终点黄色

        # plt limits
        if self.firts_add:
            self.center_x = np.median(poses_6dof[:, 3])
            self.center_y = np.median(poses_6dof[:, 4])
            self.center_z = np.median(poses_6dof[:, 5])
            self.firts_add=False
        else:
            self.center_x = (np.median(poses_6dof[:, 3]) +self.center_x)/2
            self.center_y = (np.median(poses_6dof[:, 4]) +self.center_y)/2
            self.center_z = (np.median(poses_6dof[:, 5])+self.center_z)/2






        i = 0
        while i < position.shape[0]:
            if i % args.interval_6dof == 0:
                # 划黑线
                self._point_plt(position,rotcoord,i)
            i += 1

    def show(self,r=150):

        self.ax.set_xlim3d([self.center_x - r, self.center_x + r])
        self.ax.set_ylim3d([self.center_y - r, self.center_y + r])
        self.ax.set_zlim3d([self.center_z - r, self.center_z + r])

        # 坐标系示意
        if self.flag_coord:
            self.ax.quiver(self.center_x, self.center_y, self.center_z, 1, 0, 0, length=20, color='r')
            self.ax.quiver(self.center_x, self.center_y, self.center_z, 0, 1, 0, length=20, color='g')
            self.ax.quiver(self.center_x, self.center_y, self.center_z, 0, 0, 1, length=20, color='b')

        plt.show()

        # fig, ax2 = plt.subplots(figsize=(1.5, 4))
        # fig.subplots_adjust(right=0.4)
        # cb = mpl.colorbar.ColorbarBase(ax2,
        #                                cmap=self.mycmap,
        #                                norm=self.mynorm,
        #                                orientation='vertical')
        #
        # cb.set_label('roll angle (degree)')


def main():
    '''
    just draw one pose line
    :return:
    '''
    poses = np.loadtxt("../data_out/mcv5/base/time_poses.txt")

    poses_6dof = mc2pose6dof(poses)
    #poses_6dof2 = mc2pose6dof(poses2)

    #
    # pose_kitti = pose6dof2kitti(poses_6dof)
    # poses_6dof_ = kitti2pose6dof(pose_kitti)

    # change to pose6dof
    # if args.input_fmt=='mc':
    #     poses_6dof =mc2pose6dof(poses)
    # elif args.input_fmt=='kitti':
    #     poses_6dof = kitti2pose6dof(poses)

    drawer = StaticDraw(
        flag_coord=True,
        dof='6dof',
        interval=5
    )

    drawer.add_poses(
        poses_6dof
    )


    drawer.show()

def main2():
    '''
    multiple pose lines drawing
    :return:
    '''
    base_path = Path("/home/roit/aws/trajectory/data_out/mcv5")
    lines = readlines('/home/roit/aws/trajectory/logs/static_draw_log.txt')
    drawer = StaticDraw(flag_coord=True,dof='6dof',interval=5)

    for line in lines:
        if not line:
            break
        path = base_path/line
        poses = np.loadtxt(path)
        poses_6dof = mc2pose6dof(poses)
        drawer.add_poses(poses_6dof)

    drawer.show()



    pass

if __name__ == '__main__':
    main()
