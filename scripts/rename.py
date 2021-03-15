import argparse
from path import Path
from utils.fio import *
parser = argparse.ArgumentParser(description='combine aperture camera profiles')
parser.add_argument("--input_json",
                    default="/home/roit/datasets/MineNav/mcv5jsons/combined/block_0x0.json"# as traj_name
                    #default=None
                    )
parser.add_argument("--out_dir",default='/home/roit/datasets/MineNav/mcv5jsons/split')
