# trajectory
trajectory generation and visualization in multi-DoF


# 介绍

主要包含两部分，一个是aperture中的文件预处理(json_prep)、处理导出(aperture)
另一个是可视化(viz)
以下是不同文件夹介绍.




## aperture

根据aperture的json文件， 插值并输出不同格式的path文件

aperture json file ===**aptPath2pose6dof**===> pose6dof_keypoints 
===**interpolaration_xdof**===> timestamp,poses_6dof 

输入 json， 输出 dir/




## viz

static_draw

dynamic_draw

lambda_draw

根据输入的mc格式的path文件，画出:
静态3dpath, 动态3dpath, lambda曲线




## utils

- fio

文件工具

- rotation

处理旋转相关

- formater

处理不同数据集中path的格式相关

- cubic_hermite.py

和aperture完全一样的插值方法, 保证视频中的路径和外面导出的一致



