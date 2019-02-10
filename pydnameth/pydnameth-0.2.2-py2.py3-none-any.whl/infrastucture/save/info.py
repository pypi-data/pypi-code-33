from pydnameth.infrastucture.path import get_experiment_path
from anytree import RenderTree
import os
import codecs


def save_info(root):
    fn = get_experiment_path(root.config) + '/info.txt'

    if os.path.isfile(fn):
        fr = codecs.open(fn, 'r+', 'utf-8')
        lines = fr.read().splitlines()
        fr.close()
    else:
        lines = []

    if str(root.config.hash) not in lines:
        fa = codecs.open(fn, 'a', 'utf-8')
        fa.write(root.config.hash + '\n')
        for pre, _, node in RenderTree(root):
            fa.write(f'{pre}{node.name}\n')
        fa.write('\n\n')
        fa.close()
