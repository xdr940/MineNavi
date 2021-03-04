
import argparse
from  utils.fio import readlines,json2dict,dict2json
from path import Path
import json
parser = argparse.ArgumentParser(description='combine aperture camera profiles')
parser.add_argument("--log_jsons",
                    default="../logs/mcv5_b00.txt"# as traj_name
                    #default=None
                    )
parser.add_argument("--base_path",default='/home/roit/datasets/MineNav/mcv5jsons')
parser.add_argument("--out_json",default='/home/roit/datasets/MineNav/mcv5jsons/combined/mcv5_b00.json')


def main(args):
    base_path = Path(args.base_path)

    base_dict ={"fixtures":[],"modifiers":[],"curves":[]}
    fixtures_ls = []

    if args.log_jsons:
        lines = readlines(args.log_jsons)
    else:
        lines = base_path.files()
    for line in lines:
        dict = json2dict(base_path/line)
        fixture_ls = dict["fixtures"]
        fixtures_ls+=fixture_ls

    base_dict['fixtures'] = fixtures_ls

    dict2json(base_dict,args.out_json)
if __name__ == '__main__':
    args = parser.parse_args()
    main(args)

