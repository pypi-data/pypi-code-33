# -*- coding: utf-8 -*-
from __future__ import print_function
import click
from .base import BaseCommand, argument, option, types, register  # noqa


@register("inspect_checkpoint")
class Command(BaseCommand):
    arguments = [
        argument("file_name", type=click.Path()),
        option("-t", "--tensor_name", help="Name of the tensor to inspect"),
        option("-a", "--all_tensors", is_flag=True, help="If True, print the names and values of all the tensors."),
        option("-an", "--all_tensor_names", is_flag=True, help="If True, print the names of all the tensors."),
        option("--printoptions", help="Argument for numpy.set_printoptions(), in the form 'k=v'.")

    ]

    def run(self, file_name, tensor_name, all_tensors, all_tensor_names, printoptions):
        from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file, parse_numpy_printoption
        if printoptions:
            parse_numpy_printoption(printoptions)
        print_tensors_in_checkpoint_file(
            file_name,
            tensor_name,
            all_tensors,
            all_tensor_names
        )
