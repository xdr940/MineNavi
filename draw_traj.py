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
from utils.formater import eular2cvec

parser = argparse.ArgumentParser(description='KITTI evaluation')
parser.add_argument("--input",
                    #default="./04001000_poses/p2p.txt"
                    default="./data_out/circle/sqrt_mc.txt"
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
                             "real_time_draw_2dof"
                             ])
parser.add_argument("--azim_elev",default=[ -171,40  ],help='观察视角')
parser.add_argument("--out_dir",default='out_dir')
parser.add_argument('--interval_6dof',default=1)
parser.add_argument('--dynamic_outfile',default=False)
parser.add_argument('--dynamic_time_interval',default=0.1)
parser.add_argument('--quiver_lenth',default=2)
parser.add_argument('--global_scale_factor',default=20.)
parser.add_argument('--watch_matrix_file',default='./watch_matrix.txt',help='for infer with drawing2d')
parser.add_argument('--file_pip',default='./pipline.txt')
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
    ax.set_xlim3d([-100, 100])
    ax.set_ylim3d([-100, 100])
    ax.set_zlim3d([-100, 100])

    ceter_x = np.median(poses_6dof[:, 3])
    ceter_y = np.median(poses_6dof[:, 4])
    ceter_z = np.median(poses_6dof[:, 5])

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
    ax.invert_xaxis()  # x 反方向
    ax.set_xlabel('X')  # X不变
    ax.set_ylabel('z')  # yz交换
    ax.set_zlabel('y')  #
    plt.axis('equal')

    i = 0

    #while i < position.shape[0]:
    ax.plot(position[:, 0], position[:, 2], position[:, 1], 'k-')
    #    i+=1

    # 绘制起点,终点,其他点
    ax.scatter(position[0, 0], position[0, 2], position[0, 1], c='r')  # 起点绿色
    ax.scatter(position[-1, 0], position[-1, 2], position[-1, 1], c='g')  # 终点黄色



    plt.show()
def draw_2dof(poses_6dof):#poses_6dof
    poses_np = np.array(poses_6dof)#200,6
    poses_np += np.random.rand()
    position = poses_np[:,3:]#xyz

    fig = plt.figure(figsize=[8, 5])
    ax = fig.gca()
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('x')  # X不变
    ax.set_ylabel('z')  # yz交换
    plt.axis('equal')

    i = 0

    #while i < position.shape[0]:
    ax.plot(position[:, 0], position[:, 2], 'k-')
    #    i+=1

    # 绘制起点,终点,其他点
    ax.plot(position[0, 0], position[0, 2],  'ro')  # 起点绿色
    ax.plot(position[-1, 0], position[-1, 2], 'go')  # 终点黄色



    plt.show()



def dynamic_draw_2dof(poses_6dof):
    poses_np = np.array(poses_6dof)  # 200,6
    position = poses_np[:, 3:]  # xyz

    fig = plt.figure(figsize=[8, 5])
    ax = fig.gca()
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('x')  # X不变
    ax.set_ylabel('z')  # yz交换
    plt.axis('equal')

    i = 1
    print(position.shape[0])
    ax.plot(position[0, 0], position[0, 2],'r-*')  # 起点绿色
    while i < position.shape[0]:
        if i %args.interval_6dof==0:
            ax.plot(position[i, 0], position[i, 2], 'g-*')
            #plt.text(x=50,y=50,s =str(i),ha = 'left',va='bottom',fontsize=22)
            print(i)
            if i !=args.interval_6dof:
                ax.plot(position[i-args.interval_6dof, 0], position[i-args.interval_6dof, 2], 'k-*')

            plt.pause(args.dynamic_time_interval)
        i += 1
    #    i+=1

    # 绘制起点,终点,其他点
    #ax.plot(position[-1, 0], position[-1, 2],'g-*')  # 终点黄色
    plt.pause(100)
def dynamic_draw_6dof(poses_6dof):
    def update(i):
        label = 'timestep {0}'.format(i)
        #print(label)
        # 更新直线和x轴（用一个新的x轴的标签）。
        # 用元组（Tuple）的形式返回在这一帧要被重新绘图的物体
        ax.plot(position[:i, 0], position[:i, 2], position[:i, 1], 'k-')

        ax.quiver(position[i, 0], position[i, 2], position[i, 1],
                  orient_vec[i, 0], orient_vec[i, 2], orient_vec[i, 1],
                  color=mycmap(roll[i]), norm=mynorm,length = args.quiver_lenth)

        return fig, ax


    #减少点数
    poses_6dof_sub = []
    cnt=0
    for pose in poses_6dof:
        if cnt%args.interval_6dof==0:
            poses_6dof_sub.append(pose)
        cnt+=1
    poses_6dof = poses_6dof_sub
    poses_6dof_np = np.array(poses_6dof)

    orient_vec = []
    roll = []
    for item in poses_6dof:
        orient_vec.append(eular2cvec(item[0], item[1]))
        roll.append(item[2])
    # draw

    position = poses_6dof_np[:,3:]
    orient_vec = np.array(orient_vec)
    roll = np.array(roll)
    # roll =(roll - roll.min())/(roll.max() - roll.min())
    roll = roll / 360 + 0.5  # [-180,180]-->[0,1] for colormap 处理


    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('equal', adjustable='box')
    # ax.yaxis.set_ticks_position('top')
    ax.invert_xaxis()  # x 反方向
    ax.set_xlabel('X')  # X不变
    ax.set_ylabel('z')  # yz交换
    ax.set_zlabel('y')  #

    plt.axis('equal')
    #视角改变
    ax.azim,ax.elev = args.azim_elev
    ax.scatter(position[0, 0], position[0, 2], position[0, 1], c='r')  # 起点绿色
    ax.scatter(position[-1, 0], position[-1, 2], position[-1, 1], c='g')  # 终点黄色
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





def real_time_draw_2dof(fin):
    """
      根据文件内容变化绘制点
      :param fliename:
      :return:
      """

    fig = plt.figure(figsize=[8, 5])
    ax = fig.gca()
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('x')  # X不变
    ax.set_ylabel('z')  # yz交换
    plt.axis('equal')
    f = open(fin, 'r')


    while True:
        try:
            pose_6dof_str = f.__next__()
            pose_6dof = str2pose_6dof(pose_6dof_str)

            ax.plot(pose_6dof[3], pose_6dof[5],  'k-*')

        except:
            pass
        plt.pause(args.dynamic_time_interval)

def real_time_draw_3dof(fin):
    """
      根据文件内容变化绘制点3d
      :param fliename:
      :return:
      """
    #poses_6dof_ls = np.ones([1,6])
    def update(i):
        ax.plot(poses_6dof_np[:i][3], poses_6dof_np[:i][5], poses_6dof_np[:i][4],'k-o')
        return fig, ax

    global poses_6dof_np
    def frames_gen():
        cnt=0
        poses_6dof_np = np.ones([1, 6])
        while True:
            pose_6dof_str = f.__next__()
            pose_6dof = str2pose_6dof(pose_6dof_str)
            pose_6dof = np.expand_dims(pose_6dof,axis=0)
            print(poses_6dof_np.shape)
            poses_6dof_np = np.concatenate([poses_6dof_np,pose_6dof])

            cnt += 1
            yield cnt
            # f.writelines(str(cnt)+'\n')

    f = open(fin, 'r')
    a= 10

    #减少点数



    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_aspect('equal', adjustable='box')
    # ax.yaxis.set_ticks_position('top')
    ax.invert_xaxis()  # x 反方向
    ax.set_xlabel('X')  # X不变
    ax.set_ylabel('z')  # yz交换
    ax.set_zlabel('y')  #

    plt.axis('equal')
    #视角改变
    ax.azim,ax.elev = args.azim_elev
    plt.title('Aircraft Ego-motion')



    anim = FuncAnimation(fig=fig, func = update, frames=frames_gen, interval=100)

    #save or show
    if args.dynamic_outfile==True:
        same_name = Path(args.input).relpath('./').strip('.txt').replace('/','_')+'.mp4'
        anim.save(same_name, dpi=80, writer='imagemagick')
    else:
        plt.show()





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

    if args.input_fmt=='mc':
        poses_6dof =mc2pose6dof(poses)
    elif args.input_fmt=='kitti':
        poses_6dof = kitti2pose6dof(poses)


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
    elif args.output_style =="real_time_draw_2dof":
        real_time_draw_2dof(args.file_pip)
    elif args.output_style == "real_time_draw_3dof":
        real_time_draw_3dof(args.file_pip)



