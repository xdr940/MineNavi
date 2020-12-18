
import numpy as np
import matplotlib.pyplot as plt
if __name__ == '__main__':

    time = np.linspace(start=0,stop=364,num=365)
    time = np.expand_dims(time,axis=1)



    x = np.linspace(start=0,stop=364,num=365)
    x = np.expand_dims(x,axis=1)
    y = np.linspace(start=0,stop=20,num=365)
    y = np.expand_dims(y,axis=1)
    z = np.ones(365)*80
    z = np.expand_dims(z,axis=1)

    position = np.concatenate([x,y,z],axis=1)
    print(position.shape)

    pitch = np.ones(365)*90
    pitch = np.expand_dims(pitch,axis=1)

    yaw = np.ones(365)*90
    yaw = np.expand_dims(yaw,axis=1)

    roll = np.ones(365)*90
    roll = np.expand_dims(roll,axis=1)


    rotation = np.concatenate([pitch,yaw,roll],axis=1)



    print(rotation.shape)

    pose_6dof = np.concatenate([rotation,position],axis=1).astype(np.float)
    #rand = np.random.random([365,6])

    xx = np.linspace(0,5,365)
    rand = np.cos(xx)*np.sin(xx)

    plt.plot(rand)
    plt.show()

    pose_6dof+=rand

    pose_mc = np.concatenate([time, pose_6dof],axis=1)


    print(pose_6dof.shape)


    np.savetxt('line.txt',pose_mc,fmt='%1.8e')






