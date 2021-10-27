

import argparse
from apeture.aperture import Aperture


parser = argparse.ArgumentParser(description='MineCraft Aperture Tools')
parser.add_argument("--input_json",
                    # default="/home/roit/datasets/MineNav/mcv2jsons/0000.json"# as traj_name
                    default = "/home/roit/datasets/MineNav/mcrandom/traj_display.json"  # as traj_name

)
parser.add_argument("--out_dir",default='../data_out/mcrandom')
parser.add_argument("--interp_type",
                    default='hermite',
                    # default = 'linear'
                    )

parser.add_argument("--traj_curve_out",default=True)
parser.add_argument("--eularmod",default=False)

parser.add_argument("--out_format",default='mc',choices=['mc','kitti','tum','bag','euroc'])
args = parser.parse_args()



if __name__ == '__main__':
    aperture = Aperture(
        input_json=args.input_json,
        out_dir=args.out_dir,
        interp_type=args.interp_type
    )
    aperture()
