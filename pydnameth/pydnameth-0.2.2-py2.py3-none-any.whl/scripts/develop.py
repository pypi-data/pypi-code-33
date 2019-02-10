from anytree import Node
from pydnameth.config.experiment.experiment import Experiment
from pydnameth.config.experiment.types import DataType, Task, Method
from pydnameth.config.config import Config
from pydnameth.model.tree import build_tree, calc_tree
from pydnameth.config.attributes.attributes import Attributes, Observables, Cells
from pydnameth.infrastucture.path import get_save_path
from pydnameth.infrastucture.file_name import get_file_name
import copy
from shutil import copyfile
import os


def cpg_proc_table_linreg_dev(
    data,
    annotations,
    attributes,
    params=None
):
    config_root = Config(
        data=copy.deepcopy(data),
        experiment=Experiment(
            type=DataType.cpg,
            task=Task.table,
            method=Method.linreg,
            params=copy.deepcopy(params)
        ),
        annotations=copy.deepcopy(annotations),
        attributes=copy.deepcopy(attributes),
        is_run=True,
        is_root=True
    )

    root = Node(name=str(config_root), config=config_root)
    build_tree(root)
    calc_tree(root)


def cpg_proc_table_variance_linreg_dev(
    data,
    annotations,
    attributes,
    params=None
):
    config_root = Config(
        data=copy.deepcopy(data),
        experiment=Experiment(
            type=DataType.cpg,
            task=Task.table,
            method=Method.variance_linreg,
            params=copy.deepcopy(params)
        ),
        annotations=copy.deepcopy(annotations),
        attributes=copy.deepcopy(attributes),
        is_run=True,
        is_root=True
    )

    root = Node(name=str(config_root), config=config_root)
    build_tree(root)
    calc_tree(root)


def cpg_proc_table_polygon_dev(
    data,
    annotations,
    attributes,
    observables_list,
    child_method=Method.linreg,
    params=None
):
    config_root = Config(
        data=copy.deepcopy(data),
        experiment=Experiment(
            type=DataType.cpg,
            task=Task.table,
            method=Method.polygon,
            params=copy.deepcopy(params)
        ),
        annotations=copy.deepcopy(annotations),
        attributes=copy.deepcopy(attributes),
        is_run=True,
        is_root=True
    )
    root = Node(name=str(config_root), config=config_root)

    for d in observables_list:
        observables_child = Observables(
            name=copy.deepcopy(attributes.observables.name),
            types=d
        )

        cells_child = Cells(
            name=copy.deepcopy(attributes.cells.name),
            types=copy.deepcopy(attributes.cells.types)
        )

        attributes_child = Attributes(
            target=copy.deepcopy(attributes.target),
            observables=observables_child,
            cells=cells_child,
        )

        config_child = Config(
            data=copy.deepcopy(data),
            experiment=Experiment(
                type=DataType.cpg,
                task=Task.table,
                method=copy.deepcopy(child_method),
                params={}
            ),
            annotations=copy.deepcopy(annotations),
            attributes=attributes_child,
            is_run=True,
            is_root=False
        )
        Node(name=str(config_child), config=config_child, parent=root)

    build_tree(root)
    calc_tree(root)


def cpg_proc_table_z_test_linreg_dev(
    data,
    annotations,
    attributes,
    observables_list,
    child_method=Method.linreg,
    params=None
):
    config_root = Config(
        data=copy.deepcopy(data),
        experiment=Experiment(
            type=DataType.cpg,
            task=Task.table,
            method=Method.z_test_linreg,
            params=copy.deepcopy(params)
        ),
        annotations=copy.deepcopy(annotations),
        attributes=copy.deepcopy(attributes),
        is_run=True,
        is_root=True
    )
    root = Node(name=str(config_root), config=config_root)

    for d in observables_list:
        observables_child = Observables(
            name=copy.deepcopy(attributes.observables.name),
            types=d
        )

        cells_child = Cells(
            name=copy.deepcopy(attributes.cells.name),
            types=copy.deepcopy(attributes.cells.types)
        )

        attributes_child = Attributes(
            target=copy.deepcopy(attributes.target),
            observables=observables_child,
            cells=cells_child,
        )

        config_child = Config(
            data=copy.deepcopy(data),
            experiment=Experiment(
                type=DataType.cpg,
                task=Task.table,
                method=copy.deepcopy(child_method),
                params={}
            ),
            annotations=copy.deepcopy(annotations),
            attributes=attributes_child,
            is_run=True,
            is_root=False
        )
        Node(name=str(config_child), config=config_child, parent=root)

    build_tree(root)
    calc_tree(root)


def cpg_proc_clock_linreg_dev(
    data,
    annotations,
    attributes,
    child_method=Method.linreg,
    params=None
):
    config_root = Config(
        data=copy.deepcopy(data),
        experiment=Experiment(
            type=DataType.cpg,
            task=Task.clock,
            method=Method.linreg,
            params=copy.deepcopy(params)
        ),
        annotations=copy.deepcopy(annotations),
        attributes=copy.deepcopy(attributes),
        is_run=True,
        is_root=True
    )
    root = Node(name=str(config_root), config=config_root)

    config_child = Config(
        data=copy.deepcopy(data),
        experiment=Experiment(
            type=DataType.cpg,
            task=Task.table,
            method=copy.deepcopy(child_method),
            params={}
        ),
        annotations=copy.deepcopy(annotations),
        attributes=copy.deepcopy(attributes),
        is_run=True,
        is_root=False
    )

    Node(name=str(config_child), config=config_child, parent=root)

    build_tree(root)
    calc_tree(root)


def cpg_proc_special_clock_linreg_dev(
    data,
    annotations,
    attributes,
    file,
    params=None,
):
    if os.path.isfile(file):

        head, tail = os.path.split(file)
        fn = os.path.splitext(tail)[0]
        ext = os.path.splitext(tail)[1]

        config_root = Config(
            data=copy.deepcopy(data),
            experiment=Experiment(
                type=DataType.cpg,
                task=Task.clock,
                method=Method.linreg,
                params=copy.deepcopy(params)
            ),
            annotations=copy.deepcopy(annotations),
            attributes=copy.deepcopy(attributes),
            is_run=True,
            is_root=True
        )
        root = Node(name=str(config_root), config=config_root)

        config_child = Config(
            data=copy.deepcopy(data),
            experiment=Experiment(
                type=DataType.cpg,
                task=Task.table,
                method=Method.special,
                params={'file_name': fn}
            ),
            annotations=copy.deepcopy(annotations),
            attributes=copy.deepcopy(attributes),
            is_run=False,
            is_root=False
        )

        Node(name=str(config_child), config=config_child, parent=root)

        build_tree(root)

        new_file = get_save_path(config_child) + '/' + \
             get_file_name(config_child) + ext

        copyfile(file, new_file)

        calc_tree(root)

    else:
        raise FileNotFoundError(f'File {file} not found.')


def cpg_plot_methylation_scatter_dev(
    data,
    annotations,
    attributes,
    cpg_list,
    observables_list,
    child_method=Method.linreg,
    params=None
):
    for cpg in cpg_list:

        config_root = Config(
            data=copy.deepcopy(data),
            experiment=Experiment(
                type=DataType.cpg,
                task=Task.methylation,
                method=Method.scatter,
                params=copy.deepcopy(params)
            ),
            annotations=copy.deepcopy(annotations),
            attributes=copy.deepcopy(attributes),
            is_run=True,
            is_root=True
        )

        if config_root.experiment.params is None:
            config_root.experiment.params = dict()

        config_root.experiment.params['item'] = cpg

        root = Node(name=str(config_root), config=config_root)

        for d in observables_list:
            observables_child = Observables(
                name=copy.deepcopy(attributes.observables.name),
                types=d
            )

            cells_child = Cells(
                name=copy.deepcopy(attributes.cells.name),
                types=copy.deepcopy(attributes.cells.types)
            )

            attributes_child = Attributes(
                target=copy.deepcopy(attributes.target),
                observables=observables_child,
                cells=cells_child,
            )

            config_child = Config(
                data=copy.deepcopy(data),
                experiment=Experiment(
                    type=DataType.cpg,
                    task=Task.table,
                    method=copy.deepcopy(child_method),
                    params={}
                ),
                annotations=copy.deepcopy(annotations),
                attributes=attributes_child,
                is_run=False,
                is_root=False
            )
            Node(name=str(config_child), config=config_child, parent=root)

        build_tree(root)
        calc_tree(root)


def attributes_plot_observables_histogram_dev(
    data,
    annotations,
    attributes,
    observables_list,
    params=None
):
    config_root = Config(
        data=copy.deepcopy(data),
        experiment=Experiment(
            type=DataType.attributes,
            task=Task.observables,
            method=Method.histogram,
            params=copy.deepcopy(params)
        ),
        annotations=copy.deepcopy(annotations),
        attributes=copy.deepcopy(attributes),
        is_run=True,
        is_root=True
    )
    root = Node(name=str(config_root), config=config_root)

    for d in observables_list:
        observables_child = Observables(
            name=copy.deepcopy(attributes.observables.name),
            types=d
        )

        cells_child = Cells(
            name=copy.deepcopy(attributes.cells.name),
            types=copy.deepcopy(attributes.cells.types)
        )

        attributes_child = Attributes(
            target=copy.deepcopy(attributes.target),
            observables=observables_child,
            cells=cells_child,
        )

        config_child = Config(
            data=copy.deepcopy(data),
            experiment=config_root.experiment,
            annotations=copy.deepcopy(annotations),
            attributes=attributes_child,
            is_run=False,
            is_root=True
        )
        Node(name=str(config_child), config=config_child, parent=root)

    build_tree(root)
    calc_tree(root)
