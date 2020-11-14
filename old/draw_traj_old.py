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
from utils.formater import eular2cvec,str2pose_6dof
from utils.formater import line2np,np2line

parser = argparse.ArgumentParser(description='KITTI evaluation')
parser.add_argument("--input",
                    #default="./04001000_poses/p2p.txt"
                    default="/home/roit/aws/trajectory/data_out/circle/sqrt_mc.txt"
                    #default = "./datasets/kitti_gt_poses/04.txt"


)
parser.add_argument("--input_fmt",default='mc',choices=['mc','kitti','tum','euroc'])
parser.add_argument("--output_style",
                    default='draw_6dof',
                    choices=['draw_2dof',
                             'draw_3dof',
                             'draw_6dof',
                             'dynamic_draw_2dof',
                             "dynamic_draw_2dof_outfile",
                             'dynamic_draw_6dof',
                             "real_time_draw_6dof",
                             "real_time_draw_3dof"
                             ])
parser.add_argument("--azim_elev",default=[ -171,40  ],help='观察视角')
parser.add_argument("--out_dir",default='out_dir')
parser.add_argument('--interval_6dof',default=1)
parser.add_argument('--dynamic_outfile',default=False)
parser.add_argument('--dynamic_time_interval',default=0.1)
parser.add_argument('--real_time_interval',default=2)

parser.add_argument('--quiver_lenth',default=10)
parser.add_argument('--global_scale_factor',default=20.)
parser.add_argument('--watch_matrix_file',default='./watch_matrix.txt',help='for infer with drawing2d')
parser.add_argument('--file_pip',default='./data_out/eight/_mc.txt')
args = parser.parse_args()




def draw_6dof(poses_6dof):#poses_6dof
    print('points_num:',poses_6dof.shape[0])

    fig = plt.figure(figsize=[10, 10])
    ax = fig.gca(projection='3d')
    ax.set_aspect('equal', adjustable='box')
    plt.axis('equal')

    # ax.yaxis.set_ticks_position('top')
        #ax.invert_xaxis()  # x 反方向
        # ax.invert_yaxis()  # x 反方向
        #ax.invert_zaxis()
    ax.set_xlabel('X')  # X不变
    ax.set_ylabel('y')  # yz交换
    ax.set_zlabel('z')  #

    position = poses_6dof[:, 3:]  # xyz
    eular = np.deg2rad(poses_6dof[:, :3])
    cvec = eular2cvec(eular)#rpy


    ax.azim,ax.elev = args.azim_elev
    plt.axis('equal')
    # plt.title('trajectory 80_00_1')
    mycmap = plt.get_cmap('hsv', 100)
    mynorm = mpl.colors.Normalize(vmin=-180, vmax=180)

    # 绘制起点,终点,其他点
    ax.scatter(position[0, 0], position[0, 1], position[0, 2], c='r')  # 起点绿色
    ax.scatter(position[-1, 0], position[-1, 1], position[-1, 2], c='g')  # 终点黄色


    # plt limits
    #ax.set_xlim3d([-100, 100])
    #ax.set_ylim3d([-100, 100])
    ax.set_zlim3d([-100, 100])

    ceter_x = np.median(poses_6dof[:, 3])
    ceter_y = np.median(poses_6dof[:, 4])
    ceter_z = np.median(poses_6dof[:, 5])

    #坐标系示意
    ax.quiver(ceter_x, ceter_y, ceter_z, 1, 0, 0, length=20, color='r')
    ax.quiver(ceter_x, ceter_y, ceter_z, 0, 1, 0, length=20, color='g')
    ax.quiver(ceter_x, ceter_y, ceter_z, 0, 0, 1, length=20, color='b')

    # 绘制箭头
    i = 0
    while i < position.shape[0]:
        if i % args.interval_6dof == 0:
            # 划黑线
            ax.plot(position[:i, 0], position[:i, 1], position[:i, 2], 'k-')
            ax.quiver(position[i, 0], position[i, 1], position[i, 2],
                      cvec[i, 0], cvec[i, 1], cvec[i, 2],
                      color=mycmap(cvec[i, 3]), norm=mynorm,normalize=True,length=10)
            i += 1
    fig, ax2 = plt.subplots(figsize=(1.5, 4))
    fig.subplots_adjust(right=0.4)

    # color bar
    cb = mpl.colorbar.ColorbarBase(ax2,
                                   cmap=mycmap,
                                   norm=mynorm,
                                   orientation='vertical')

    cb.set_label('roll angle (degree)')

    plt.show()
def draw_3dof(poses_6dof):#poses_6dof
    poses_np = np.array(poses_6dof)#200,6
    position = poses_np[:,3:]#xyz

    fig = plt.figure(figsize=[8, 5])
    ax = fig.gca(projection='3d')
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('X')  # X不变
    ax.set_ylabel('Y')  # yz交换
    ax.set_zlabel('Z')  #
    plt.axis('equal')


    ax.plot(position[:, 0], position[:, 1], position[:, 2], 'k-')
    ax.scatter(position[0, 0], position[0, 1], position[0, 2], c='r')  # 起点绿色
    ax.scatter(position[-1, 0], position[-1, 1], position[-1, 2], c='g')  # 终点黄色



    plt.show()
def draw_2dof(poses_6dof):#poses_6dof
    poses_np = np.array(poses_6dof)#200,6
    poses_np += np.random.rand()
    position = poses_np[:,3:]#xyz

    fig = plt.figure(figsize=[8, 5])
    ax = fig.gca()
    ax.set_xlabel('X')  # X不变
    ax.set_ylabel('y')  # yz交换
    plt.axis('equal')


    ax.plot(position[:, 0], position[:, 1], 'k-')
    ax.plot(position[0, 0], position[0, 1],  'ro')  # 起点绿色
    ax.plot(position[-1, 0], position[-1, 1], 'go')  # 终点黄色
    plt.show()



def dynamic_draw_2dof(poses_6dof):
    position = poses_6dof[:, 3:]  # xyz

    fig = plt.figure(figsize=[8, 5])
    ax = fig.gca()
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.axis('equal')

    i = 1
    print(position.shape[0])
    ax.plot(position[0, 0], position[0, 1],'r-*')  # 起点绿色
    while i < position.shape[0]:
        if i %args.interval_6dof==0:
            ax.plot(position[i, 0], position[i, 1], 'g-*')
            print(i)
            if i !=args.interval_6dof:
                ax.plot(position[i-args.interval_6dof, 0], position[i-args.interval_6dof, 1], 'k-*')
            plt.pause(args.dynamic_time_interval)
        i += 1
    plt.pause(100)
def dynamic_draw_6dof(poses_6dof):
    def update(i):
        label = 'timestep {0}'.format(i)
        #print(label)
        # 更新直线和x轴（用一个新的x轴的标签）。
        # 用元组（Tuple）的形式返回在这一帧要被重新绘图的物体
        ax.plot(position[:i, 0], position[:i, 1], position[:i, 2], 'k-')

        ax.quiver(position[i, 0], position[i, 1], position[i, 2],
                  cvec[i, 0], cvec[i, 1], cvec[i, 2],
                  color=mycmap(cvec[i,3]), norm=mynorm,length = args.quiver_lenth)
        return fig, ax


    #fig init
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('equal', adjustable='box')

    ax.set_xlabel('X')  # X不变
    ax.set_ylabel('y')  # yz交换
    ax.set_zlabel('z')  #

    plt.axis('equal')

    # plt limits
    ax.set_xlim3d([-100, 100])
    ax.set_ylim3d([-100, 100])
    ax.set_zlim3d([-100, 100])

    ceter_x = np.median(poses_6dof[:, 3])
    ceter_y = np.median(poses_6dof[:, 4])
    ceter_z = np.median(poses_6dof[:, 5])

    ax.quiver(ceter_x, ceter_y, ceter_z, 1, 0, 0, length=20, color='r')
    ax.quiver(ceter_x, ceter_y, ceter_z, 0, 1, 0, length=20, color='g')
    ax.quiver(ceter_x, ceter_y, ceter_z, 0, 0, 1, length=20, color='b')

    #data in
    position = poses_6dof[:, 3:]  # xyz
    eular = np.deg2rad(poses_6dof[:, :3])
    cvec = eular2cvec(eular)  # rpy

    #视角改变
    ax.azim,ax.elev = args.azim_elev
    ax.scatter(position[0, 0], position[0, 1], position[0, 2], c='r')  # 起点绿色
    ax.scatter(position[-1, 0], position[-1, 1], position[-1, 2], c='g')  # 终点黄色
    plt.title('Aircraft Ego-motion')
    mycmap = plt.get_cmap('hsv', 100)
    mynorm = mpl.colors.Normalize(vmin=-180, vmax=180)



    anim = FuncAnimation(fig, update, frames=range(0, position.shape[0]), interval=100)

    #save or show
    if args.dynamic_outfile==True:
        same_name = Path(args.input).relpath('./').strip('.txt').replace('/','_')+'.mp4'
        anim.save(same_name, dpi=80, writer='imagemagick')
    else:
        plt.show()



class RealTimeDraw():
    def __init__(self,fin,dof='6dof'):
        self.fin = open(fin, 'r')

        self.fig = plt.figure()
        self.ax = self.fig.gca(projection='3d')
        self.ax.set_aspect('equal', adjustable='box')

        self.dof=dof


        # ax.yaxis.set_ticks_position('top')
        self.ax.invert_xaxis()  # x 反方向
        self.ax.set_xlabel('X')  # X不变
        self.ax.set_ylabel('z')  # yz交换
        self.ax.set_zlabel('y')  #

        plt.axis('equal')
        # 视角改变
        self.ax.azim, self.ax.elev = args.azim_elev
        plt.title('Aircraft Ego-motion')
        # plt.title('trajectory 80_00_1')
        self.mycmap = plt.get_cmap('hsv', 100)
        self.mynorm = mpl.colors.Normalize(vmin=-180, vmax=180)
        #data first row
        pose_6dof_str = self.fin.__next__()
        pose_mc = line2np(pose_6dof_str)
        self.pose6dof = mc2pose6dof(pose_mc)

        #self.ax.set_xlim3d([-100, 100])
        #self.ax.set_ylim3d([-100, 100])
        self.ax.set_zlim3d([-100, 100])



    def _update(self,i):
        self.ax.plot(self.pose6dof[:i,3], self.pose6dof[:i,4], self.pose6dof[:i,5], 'k-.')

        if self.dof=='6dof' and i%args.real_time_interval==0:
            eular = np.deg2rad(self.pose6dof[i, :3])
            cvec = eular2cvec(np.expand_dims(eular,axis=0))  # rpy
            self.ax.quiver(
                self.pose6dof[i, 3], self.pose6dof[i, 4], self.pose6dof[i, 5],
                      cvec[0,0], cvec[0,1], cvec[0,2],
                      color=self.mycmap(cvec[0,3]), norm=self.mynorm, normalize=True, length=args.quiver_lenth)
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

    def __call__(self,):

        anim = FuncAnimation(fig=self.fig, func=self._update, frames=self._frames_gen, interval=100)

        # save or show
        if args.dynamic_outfile == True:
            same_name = Path(args.input).relpath('./').strip('.txt').replace('/', '_') + '.mp4'
            anim.save(same_name, dpi=80, writer='imagemagick')
        else:
            plt.show()
        pass




def real_time_write(fin):

    cnt =0
    while True:
        f = open(fin,'a')
        line = 'pose:'+str(cnt)+'\n'
        f.writelines(line)
        print(line)
        f.close()
        time.sleep(0.5)
        cnt+=1
if __name__ == '__main__':
    poses = np.loadtxt(args.input)


    #change to pose6dof
    if args.input_fmt=='mc':
        poses_6dof =mc2pose6dof(poses)
    elif args.input_fmt=='kitti':
        poses_6dof = kitti2pose6dof(poses)



    #draw
    if args.output_style=='draw_2dof':
        draw_2dof(poses_6dof)
    elif args.output_style == 'draw_3dof':
        draw_3dof(poses_6dof)
    elif args.output_style == 'draw_6dof':

        draw_6dof(poses_6dof)

    #dynamic draw
    elif args.output_style=='dynamic_draw_2dof':
        dynamic_draw_2dof(poses_6dof)
    elif args.output_style == 'dynamic_draw_6dof':
        dynamic_draw_6dof(poses_6dof)

    #realtime draw
    elif args.output_style =="real_time_draw_6dof":
        rtd = RealTimeDraw(args.file_pip, dof='6dof')
        rtd()
    elif args.output_style == "real_time_draw_3dof":
        rtd = RealTimeDraw(args.file_pip,dof='3dof')
        rtd()



