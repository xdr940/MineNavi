import torch
import torch.nn as nn
from torch import sigmoid
from torch.nn.init import xavier_uniform_, zeros_


def conv(in_planes, out_planes, kernel_size=3):
    return nn.Sequential(
        nn.Conv2d(in_planes, out_planes, kernel_size=kernel_size,
                  padding=(kernel_size-1)//2,#for half output
                  #padding=1,

                  stride=2),
        nn.ReLU(inplace=True)
    )

def upconv(in_planes, out_planes):
    return nn.Sequential(
        nn.ConvTranspose2d(in_planes, out_planes, kernel_size=4, stride=2, padding=1),
        nn.ReLU(inplace=True)
    )

class PoseNet(nn.Module):

    def __init__(self):
        super(PoseNet, self).__init__()

        conv_planes = [16, 32, 64, 128, 256, 256, 256]
        self.conv1 = conv(6, conv_planes[0], kernel_size=7)#6,16,7
        self.conv2 = conv(conv_planes[0], conv_planes[1], kernel_size=5)#16,32,5
        self.conv3 = conv(conv_planes[1], conv_planes[2])
        self.conv4 = conv(conv_planes[2], conv_planes[3])
        self.conv5 = conv(conv_planes[3], conv_planes[4])
        self.conv6 = conv(conv_planes[4], conv_planes[5])
        self.conv7 = conv(conv_planes[5], conv_planes[6])

        self.pose_pred = nn.Conv2d(conv_planes[6], 6, kernel_size=1, padding=0)#strid = 1 pading =0-->output不变, 仅仅channel变化

    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
                xavier_uniform_(m.weight.data)
                if m.bias is not None:
                    zeros_(m.bias)

    def forward(self, target_image, ref_img=None):
        input = [target_image, ref_img]
        input = torch.cat(input, 1)#input.shape = 1,6,256,832
        out_conv1 = self.conv1(input)#out_conv1.shape = 1,16,128,416
        out_conv2 = self.conv2(out_conv1)#
        out_conv3 = self.conv3(out_conv2)#out_conv2.shape = 1,32,64,208
        out_conv4 = self.conv4(out_conv3)#out_conv3.shape = 1,64,32,104
        out_conv5 = self.conv5(out_conv4)#out_conv4.shape = 1,128,16,52
        out_conv6 = self.conv6(out_conv5)##out_conv5 = 1,256,8,26
        out_conv7 = self.conv7(out_conv6)#out_conv6.shape = 1,256,4,13
        pose = self.pose_pred(out_conv7)#out_conv7.shape = 1,256,2,7, pose.shape = 1,6,2,7
        pose = pose.mean(3).mean(2)#pose.shape=1,6
        pose = 0.01 * pose.view(pose.size(0), 6)#
        #pose = 0.01 * pose.reshape(1, 6)#

 
        return pose
