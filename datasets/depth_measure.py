from path import Path
import matplotlib.pyplot as plt
import numpy as np
import cv2
from  sklearn.linear_model import LinearRegression

#对不同depth shader, 计算灰度-距离函数曲线

root = Path('/home/roit/datasets/mctest/screenshots')

ext ='png'


def main():
    dirs = root.dirs()
    len = dirs.__len__()#待处理的文件夹个数
    fmt=['r*','go','b','y','m','c','k']
    names = []
    dis_gries=[]
    name_dis_gra={}
    for i in range(len):
        name,dis_gray = read_dir(dirs[i])
        name_dis_gra[name] = dis_gray
        #names.append(name)
        #dis_gries.append(dis_gray)


    #reg



    i=0
    for key in name_dis_gra.keys():
        if key =='cpdepth_fov70_48insane':
            #print(name_dis_gra[key])
            linear_reg(name_dis_gra[key][:60])
            plt.plot(name_dis_gra[key][0,:],name_dis_gra[key][1,:],fmt[i],label=key)
        i+=1
    print(name_dis_gra['cpdepth_fov70_48insane'])
    hist = np.histogram(name_dis_gra['cpdepth_fov70_48insane'][1],bins=255)
    print(hist)
    plt.ylabel('gray(1)')
    plt.xlabel('distances(m)')
    plt.legend()
    plt.show()

    print('ok')
def imread(p):
    img = cv2.imread(p)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    return img

def imread2(p):
    img = plt.imread(p)
    img = img[:,:,0]*0.2989 + img[:,:,1]*0.5870 + img[:,:,2]*0.1440
    return img

def read_dir(path):
    name = path.stem
    files = path.files('*.{}'.format(ext))
    files.sort()
    img=cv2.imread(files[0])
    h,w=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY).shape
    gray=[]
    dis=[]
    for img_p in files:
        img = imread2(img_p)
        #img = plt.imread(img_p)
        gray.append(img[int(h/2)+1,int(w/2)+1])#图像中心灰度
        dis.append(float(img_p.stem))

    dis =np.expand_dims( np.array(dis),axis=0)
    gray = np.expand_dims(np.array(gray),axis=0)
    dis_gray = np.concatenate([dis,gray],axis=0)
    return name,dis_gray

def linear_reg(arr):
    x = np.expand_dims(arr[0,:],axis=1)# 81,1
    x = x@np.ones([1,2])

    y= np.expand_dims(arr[1,:],axis=1)
    linreg = LinearRegression()
    model = linreg.fit(x,y)


    y_ = model.coef_[0][0]*x[:,0] +model.intercept_

    #plt.plot(x[:,0],y_,'b-')

    print(model.coef_)
    print(linreg.intercept_)


if __name__ == '__main__':
    main()


