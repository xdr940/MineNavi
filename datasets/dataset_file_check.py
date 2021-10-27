
from path import Path

def main():
    data_path = Path('/home/roit/datasets/mcv1')
    dirs =data_path.dirs()
    dirs.sort()
    shaders ={}
    for idx,scence in enumerate(dirs):
        for shader in scence.dirs():
            if shader.stem not in shaders.keys():
                shaders[shader.stem]=[]
                shaders[shader.stem].append(idx)
            else:
                shaders[shader.stem].append(idx)

    print(shaders)



    pass


if __name__ == '__main__':
    main()
