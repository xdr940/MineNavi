


import argparse
from path import Path
from utils.fio import *
parser = argparse.ArgumentParser(description='combine aperture camera profiles')
parser.add_argument("--input_json",
                    default="/home/roit/datasets/MineNav/mcv5jsons/combined/block_0x0.json"# as traj_name
                    #default=None
                    )
parser.add_argument("--out_dir",default='/home/roit/datasets/MineNav/mcv5jsons/split')


def split(args):
    dict = json2dict(args.input_json)
    out_dir = Path(args.out_dir)
    out_dir.mkdir_p()
    empyt_dict = dict.copy()
    for idx,item in enumerate(dict['fixtures']):
        empyt_dict['fixtures']=[item]
        dict2json(empyt_dict,out_dir/"{:04d}.json".format(idx))
    print('ok')
    pass
if __name__ == '__main__':
    args = parser.parse_args()
    split(args)


