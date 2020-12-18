from imageio import imread
from skimage.transform import resize as imresize
import numpy as np
from path import Path
from opts.infer_vo_opts import infer_vo_opts
from tqdm import tqdm

from utils.inverse_warp import *
import models


device = torch.device(
    "cuda") if torch.cuda.is_available() else torch.device("cpu")


def load_tensor_image(filename, args):
    img = imread(filename).astype(np.float32)
    h, w, _ = img.shape
    if (h != args.img_height or w != args.img_width):
        img = imresize(img, (args.img_height, args.img_width)
                       ).astype(np.float32)
    img = np.transpose(img, (2, 0, 1))
    tensor_img = (
        (torch.from_numpy(img).unsqueeze(0)/255 - 0.5)/0.5).to(device)
    return tensor_img[:,:3,:,:]


@torch.no_grad()
def main(args):
    print('->model load: {}'.format(args.pretrained_posenet))
    weights_pose = torch.load(args.pretrained_posenet)
    pose_net = models.PoseNet().to(device)
    pose_net.load_state_dict(weights_pose['state_dict'], strict=False)
    pose_net.eval()


    #data load
    if args.split=='kitti':
        if args.type =='gray':
            image_dir = Path(args.dataset_dir)/args.sequence/"image_1"#gray 01, color 23
        else:
            image_dir = Path(args.dataset_dir) / args.sequence /"image_2"#gray 01, color 23
    if args.split=='mc':
        image_dir = Path(args.dataset_dir)

    output_dir = Path(args.output_dir)
    print('-> out dif {}'.format(output_dir))
    output_dir.mkdir_p()

    test_files = sum([image_dir.files('*.{}'.format(ext))
                      for ext in args.img_exts], [])
    test_files.sort()
    print('{} files to test'.format(len(test_files)))

    global_pose = np.identity(4)
    poses = [global_pose[0:3, :].reshape(1, 12)]

    n = len(test_files)
    tensor_img1 = load_tensor_image(test_files[0], args)

    for iter in tqdm(range(n - 1)):
        tensor_img2 = load_tensor_image(test_files[iter+1], args)

        #pred
        pose = pose_net(tensor_img1, tensor_img2)#1,3,256,832 --> 1.6
        pose_mat = pose_vec2mat(pose).squeeze(0).cpu().numpy()#1,6-->3x4


        pose_mat = np.vstack([pose_mat, np.array([0, 0, 0, 1])])#4X4
        global_pose = pose_mat@global_pose #这地方类似与disp， 为了限制在0~1， 训练的时候也是用的T-1， 得到的是invpose

        #global_pose = global_pose @ np.linalg.inv(pose_mat)#这地方类似与disp， 为了限制在0~1， 训练的时候也是用的T-1， 得到的是invpose

        pose = global_pose[0:3, :].reshape(1, 12)


        poses.append(pose)

        # update
        tensor_img1 = tensor_img2

    poses = np.concatenate(poses, axis=0)
    if args.scale_factor:
            poses[:,3] *=args.scale_factor#x-axis
            poses[:,11]*=args.scale_factor#z-axis


    #save
    if args.split=='kitti':
        filename = Path(args.output_dir)/"kitti_{}.txt".format(args.sequence)
    if args.split=='mc':
        filename = Path(args.output_dir)/"mc.txt"
    np.savetxt(filename, poses, delimiter=' ', fmt='%1.8e')


if __name__ == '__main__':
    args = infer_vo_opts().parse()
    main(args)
