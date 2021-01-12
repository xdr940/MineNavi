import json


def readlines(filename):
    """Read all the lines in a text file and return as a list
    """
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    return lines

def json2dict(path):
    '''
    json file 2 dict
    :param path:
    :return:
    '''
    f = open(path, encoding='utf-8')
    content = f.read()
    dict = json.loads(content)
    return dict

def dict2json(dict,fpath):
    js = json.dumps(dict, indent=2)
    with open(fpath, 'w') as fp:
        fp.write(js)

