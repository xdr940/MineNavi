
from  path import Path
import json
import numpy as np
#for reoffset

def aptPath2pose6dof(points):
    '''
    saved as rpy, zyx seq,
    :param points:
    :return:
    '''
    points_ls = []
    for point in points:
        point_ls = []
        point_ls.append(point['angle']['roll'])  #
        point_ls.append(point['angle']['pitch'])  #
        point_ls.append(point['angle']['yaw'])  #
        #除了json文件都按照標準座標
        point_ls.append(point['point']['z'])  # x
        point_ls.append(point['point']['x'])  # y
        point_ls.append(point['point']['y'])  # z
        # z minecraft is using aircraft-coordination sys, change it to ground-coord sys

        points_ls.append(point_ls)

    points_np = np.array(points_ls)
    return points_np

def json2np(file):
    f = open(file, encoding='utf-8')
    content = f.read()
    dict = json.loads(content)

    main_dict = dict['fixtures'][0]
    #traj_name = main_dict['name']


    points = main_dict['points']
    # duration_ms = int(main_dict['duration'] / 20 * 1000)
    # num_frames = len(points)
    pose6dof_keypoints = aptPath2pose6dof(points)
    return pose6dof_keypoints
def csv2json(fin,fout):
    csv_file = np.loadtxt(fin,delimiter=',')


    default_json = './default.json'
    f = open(default_json, encoding='utf-8')
    content = f.read()
    dict = json.loads(content)
    key_points = dict['fixtures'][0]['points']
    assert len(key_points)==csv_file.shape[0]

    for i,item in enumerate(key_points):
        item['point']['x'] = csv_file[i][4]#y
        item['point']['y'] = csv_file[i][5]#z
        item['point']['z'] = csv_file[i][3]#x

        item['angle']['roll']=csv_file[i][0]
        item['angle']['pitch']=csv_file[i][1]
        item['angle']['yaw']=csv_file[i][2]

    js =  json.dumps(dict,indent=2)
    with open(fout,'w') as fp:
        fp.write(js)
def np2json(poses_6dof,fout):

    default_json = './default.json'
    f = open(default_json, encoding='utf-8')
    content = f.read()
    dict = json.loads(content)
    key_points = dict['fixtures'][0]['points']
    assert len(key_points)==poses_6dof.shape[0]

    for i,item in enumerate(key_points):
        item['point']['x'] = poses_6dof[i][4]#y
        item['point']['y'] = poses_6dof[i][5]#z
        item['point']['z'] = poses_6dof[i][3]#x

        item['angle']['roll']=poses_6dof[i][0]
        item['angle']['pitch']=poses_6dof[i][1]
        item['angle']['yaw']=poses_6dof[i][2]

    js =  json.dumps(dict,indent=2)
    with open(fout,'w') as fp:
        fp.write(js)
def log(poses_6dof):

    length = len(poses_6dof)-1
    print('avg stat: \nroll,\tpitch,\tyaw,\tx,\ty,\tz\t \n{:.2f},\t{:.2f},\t{:.2f},\t{:.2f},\t{:.2f},\t{:.2f}\t'.format(
        poses_6dof[:-1,0].sum()/length,
        poses_6dof[:-1,1].sum() / length,
        poses_6dof[:-1,2].sum() / length,
        poses_6dof[:-1,3].sum() / length,
        poses_6dof[:-1,4].sum() / length,
        poses_6dof[:-1,5].sum() / length,

    ))

    center_x =  (poses_6dof[2,3]+poses_6dof[6,3])/2
    center_y =  (poses_6dof[2,4]+poses_6dof[6,4])/2
    center_z =  (poses_6dof[2,5]+poses_6dof[6,5])/2

    r = (poses_6dof[2, 3] - center_x)**2 + (poses_6dof[2, 4] - center_y)**2
    r = r**0.5

    print('offset x:{},y:{}, z:{},r:{}'.format(center_x,center_y,center_z,r))

def change(poses_6dof):
    '''
    0,1,2,3,4,5
    roll,yaw,pitch,x,y,z
    :param poses_6dof:
    :return:
    '''




    #r change
    iscir=True
    r = 100
    if iscir ==True:
        r_ = r/(2**0.5)
        poses_6dof[0][x] = -r
        poses_6dof[0][y] = 0

        poses_6dof[1][x] = -r_
        poses_6dof[1][y] = r_

        poses_6dof[2][x] = 0
        poses_6dof[2][y] = r

        poses_6dof[3][x] = r_
        poses_6dof[3][y] = r_

        poses_6dof[4][x] = r
        poses_6dof[4][y] = 0

        poses_6dof[5][x] = r_
        poses_6dof[5][y] = -r_

        poses_6dof[6][x] = 0
        poses_6dof[6][y] = -r

        poses_6dof[7][x] = -r_
        poses_6dof[7][y] = -r_

        poses_6dof[8][x] = -r
        poses_6dof[8][y] = 0

    poses_6dof[:, pitch] = 45

    # offset


    poses_6dof[:, z] = 150
    poses_6dof[:, x] += offset_x
    poses_6dof[:, y] += offset_y



if __name__ == '__main__':
    roll, pitch, yaw, x, y, z = 0, 1, 2, 3, 4, 5
    offset_x = -400
    offset_y = 0
    MC2 = Path('/home/roit/datasets/MC2')
    base_file = Path('/home/roit/datasets/MC2/[rz2,x,y][0,0,0][0,0,150].json')
    out_dir = Path('./data_out')/base_file.stem
    out_dir.mkdir_p()

    poses_6dof= json2np(base_file)
    log(poses_6dof)
    change(poses_6dof)
    log(poses_6dof)

    out_file = Path('/home/roit/datasets/MC2/[rz2,x,y][0,{},0][{},{},{}].json'.format(
        int(45),
        int(offset_x),
        int(offset_y),
        int(150)
        )
    )



    #np.savetxt(out_dir/"keypoints.csv",poses_6dof,fmt='%.2f',delimiter=',')
    np2json(poses_6dof,MC2/out_file)

