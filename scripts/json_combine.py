
import argparse
from  utils.fio import readlines,json2dict,dict2json
from path import Path
import json
parser = argparse.ArgumentParser(description='combine aperture camera profiles')
parser.add_argument("--log_jsons",
                    default="../log_jsons.txt"# as traj_name
                    )
parser.add_argument("--base_path",default='/home/roit/datasets/mc_dolly_jsons')
parser.add_argument("--out_json",default='./out_json.json')


def main(args):
    base_path = Path(args.base_path)
    lines = readlines(args.log_jsons)

    base_dict ={"fixtures":[],"modifiers":[],"curves":[]}
    fixtures_ls = []
    for line in lines:
        dict = json2dict(base_path/line)
        fixture_ls = dict["fixtures"]
        fixtures_ls+=fixture_ls

    base_dict['fixtures'] = fixtures_ls

    dict2json(base_dict,"./combine.json")
if __name__ == '__main__':
    args = parser.parse_args()
    main(args)

