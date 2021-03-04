

import numpy as np
from path import Path
import matplotlib as mpl
from matplotlib.animation import FuncAnimation  # 动图的核心函数
from  matplotlib.colors import  BoundaryNorm
import matplotlib.pyplot as plt
import time
import argparse
from mpl_toolkits.mplot3d import axes3d


from utils.formater import mc2pose6dof,kitti2pose6dof
from utils.formater import str2pose_6dof,eular2rotmat,eular2rotcoord
from utils.formater import line2np,np2line

parser = argparse.ArgumentParser(description='real time draw poses')

parser.add_argument("--input_fmt",default='mc',choices=['mc','kitti','tum','euroc'])

parser.add_argument("--azim_elev",default=[ -171,40  ],help='观察视角')

parser.add_argument('--file_pip',
                    #default='/home/roit/Desktop/fpose.txt',
                    default='./data_out/c/_mc.txt'
                    )

parser.add_argument('--dof',default='6dof',choices=['6dof','3dof'])
parser.add_argument('--ms_interval',default=135)
parser.add_argument('--draw_interval',default=1)




args = parser.parse_args()



class RealTimeDraw():
    def __init__(self,
                 file,
                 azim_elev =args.azim_elev,
                 ):
        self.file=file
        self.fin = open(file, 'r')
        self.fig = plt.figure(figsize=[10,8])
        self.ax = self.fig.gca(projection='3d')
        self.ax.set_aspect('equal', adjustable='box')



        # self.ax.invert_xaxis()  # x 反方向
        self.ax.set_xlabel('X')  # X不变
        self.ax.set_ylabel('y')  # yz交换
        self.ax.set_zlabel('z')  #

        plt.axis('equal')
        # 视角改变
        self.ax.azim, self.ax.elev = azim_elev
        plt.title('Aircraft Ego-motion')

        #data first row
        pose_6dof_str = self.fin.__next__()
        pose_mc = line2np(pose_6dof_str)
        self.pose6dof = mc2pose6dof(pose_mc)



        #
        #
        #self.ax.set_xlim3d([-100, 120])
        #self.ax.set_ylim3d([-10, -200])
        self.ax.set_zlim3d([0, 200])

        ceter_x=0
        ceter_y=0
        ceter_z=0
        self.ax.quiver(ceter_x, ceter_y, ceter_z, 1, 0, 0, length=20, color='r')
        self.ax.quiver(ceter_x, ceter_y, ceter_z, 0, 1, 0, length=20, color='g')
        self.ax.quiver(ceter_x, ceter_y, ceter_z, 0, 0, 1, length=20, color='b')



        #color vec draw
        # self.mycmap = plt.get_cmap('hsv', 100)
        # self.mynorm = mpl.colors.Normalize(vmin=-180, vmax=180)

    def _update(self,i):
        self.ax.plot(self.pose6dof[:i,3], self.pose6dof[:i,4], self.pose6dof[:i,5], 'k-.')

        if self.dof=='6dof' and i%self.draw_interval==0:
            # eular = np.deg2rad(self.pose6dof[i, :3])
            # cvec = eular2cvec(np.expand_dims(eular,axis=0))  # rpy
            # self.ax.quiver(
            #     self.pose6dof[i, 3], self.pose6dof[i, 4], self.pose6dof[i, 5],
            #           cvec[0,0], cvec[0,1], cvec[0,2],
            #           color=self.mycmap(cvec[0,3]), norm=self.mynorm, normalize=True, length=args.quiver_lenth)

            eular = np.deg2rad(self.pose6dof[i,:3])
            self.rotcoord = eular2rotcoord(np.expand_dims(eular,axis=0)).reshape([3,3])

            self.ax.plot(self.pose6dof[:i, 3], self.pose6dof[:i, 4], self.pose6dof[:i, 5], 'k-')

            # xyz to rgb
            self.ax.quiver(self.pose6dof[i, 3], self.pose6dof[i, 4], self.pose6dof[i, 5],
                           self.rotcoord[0, 0], self.rotcoord[1, 0], self.rotcoord[ 2, 0],
                           color='r',normalize=True, length=10)
            self.ax.quiver(self.pose6dof[i, 3], self.pose6dof[i, 4], self.pose6dof[i, 5],
                           self.rotcoord[0, 1], self.rotcoord[1, 1], self.rotcoord[ 2, 1],
                           color='g', normalize=True, length=10)
            self.ax.quiver(self.pose6dof[i, 3], self.pose6dof[i, 4], self.pose6dof[i, 5],
                           self.rotcoord[ 0, 2], self.rotcoord[1, 2], self.rotcoord[ 2, 2],
                           color='b',normalize=True, length=10)




        return self.fig, self.ax

    def _frames_gen(self):
        cnt = 0
        while True:
            try:
                pose_6dof_str = self.fin.__next__()
            except:
                pass
            #if cnt%args.real_time_interval==0:
            pose_mc = line2np(pose_6dof_str)
            pose6dof = mc2pose6dof(pose_mc)
            self.pose6dof = np.concatenate([self.pose6dof, pose6dof])

            cnt += 1
            yield cnt

    def __call__(self,
                 ms_interval=50,
                 draw_interval=5,
                 out_file=False,
                 dof='3dof',
                 ):

        self.dof=dof
        self.draw_interval=draw_interval
        anim = FuncAnimation(fig=self.fig, func=self._update, frames=self._frames_gen, interval=ms_interval)

        # save or show
        if out_file == True:
            print('saving...')
            same_name = Path(self.file).relpath('./').strip('.txt').replace('/', '_') + '.gif'
            anim.save(same_name, dpi=150, writer='imagemagick')
        else:
            plt.show()
        pass


if __name__ == '__main__':
    drawer=RealTimeDraw(file=args.file_pip)
    drawer(ms_interval=args.ms_interval,
           draw_interval=args.draw_interval,
           dof=args.dof,
           out_file=False
           )