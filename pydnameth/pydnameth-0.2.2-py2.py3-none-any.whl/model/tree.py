from anytree import PostOrderIter
from pydnameth.infrastucture.save.info import save_info
from pydnameth.model.context import Context
import hashlib
from anytree.exporter import JsonExporter


def calc_tree(root):

    for node in PostOrderIter(root):
        config = node.config
        configs_child = [node_child.config for node_child in node.children]
        context = Context(config)
        context.pipeline(config, configs_child)


def build_tree(root):

    for node in PostOrderIter(root):

        node_status = node.config.is_root
        node.config.is_root = True
        node.name = str(node.config)

        exporter = JsonExporter(sort_keys=True)
        node_json = exporter.export(node).encode('utf-8')
        hash = hashlib.md5(node_json).hexdigest()
        node.config.set_hash(hash)
        if node.config.is_run:
            save_info(node)

        node.config.is_root = node_status
        node.name = str(node.config)
