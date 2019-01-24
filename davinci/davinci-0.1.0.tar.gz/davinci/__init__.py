#!/usr/bin/env python

from .mnist_problem import get_mnist
from .wikitext2_problem import get_wikitext2
from .imagenet_problem import get_imagenet
from .tiny_imagenet_problem import get_tiny_imagenet
from .pascal_alpha_problem import get_pascal_alpha
from .kdd_protein_problem import get_kdd_protein
from .cifar_small_problem import get_cifar_small

MNIST = get_mnist
WIKITEXT2 = get_wikitext2
IMAGENET = get_imagenet
TINY_IMAGENET = get_tiny_imagenet
PASCAL_ALPHA = get_pascal_alpha
KDD_PROTEIN = get_kdd_protein
CIFAR_SMALL = get_cifar_small

experiments = {
    'mnist': MNIST,
    'wikitext2': WIKITEXT2,
    'imagenet': IMAGENET,
    'tiny_imagenet': TINY_IMAGENET,
    'pascal_alpha': PASCAL_ALPHA,
    'kdd_protein': KDD_PROTEIN,
    'cifar_small': CIFAR_SMALL,
}


def get_experiment(name):
    return experiments[name]
