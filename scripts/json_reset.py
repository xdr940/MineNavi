
import json

from path import Path
#仅仅改变jsons文件的xz的位置
def reset(offset_x,offset_y):

    if offset_x<0:
        namex = '-{}'.format(-offset_x)
    else:
        namex = str(offset_x)
    if offset_y<0:
        namey = '-{}'.format(-offset_y)
    else:
        namey = str(offset_y)


    basefile = Path('/home/roit/datasets/MineNav/mcv5jsons/base.json')
    fout = '/home/roit/datasets/MineNav/mcv5jsons/{}.json'.format(namex+'x'+namey)
    f = open(basefile, encoding='utf-8')
    content = f.read()
    dict = json.loads(content)
    for fixture in dict['fixtures']:
        for pose in fixture['points']:
            pose['point']['z'] += offset_x
            pose['point']['x'] += offset_y

    js = json.dumps(dict, indent=2)
    with open(fout, 'w') as fp:
        fp.write(js)
    print('ok')

    pass

if __name__ == '__main__':
    #这里的xy采用论文的而不是Minecraft的

    pass
    rng = range(-5,6)
    offxs = [i*100 for i in rng]
    offys = [i*100 for i in rng]

    for offx in offxs:
        for offy in offys:
            reset(offx,offy)
