#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 09:46:54 2019

@author: Maria Climent-Pommeret
"""

import rnaviewparser.rnaview_data as rnaview_data

class Node:
    """
    Basic Node Class

    Takes into parameter either:
        - a list of children
        - a single child
    """
    count = 0

    def __init__(self, children=None):
        self.number = str(Node.count)
        self.pretty = "Basic Node"
        Node.count += 1
        if not children:
            self.children = []
        elif hasattr(children, "__len__"):
            self.children = children[:]
        else:
            self.children = [children]

    def __str__(self):
        return "Node %s" % self.number

    def __repr__(self):
        return self.pretty

class RelevantDataNode(Node):
    """
    Node that contains all the data
    """
    pretty = "Relevant Data"

    def rewrite(self):
        """
        Returns the BasePairs objets
        """
        data = rnaview_data.BasePairs()

        for child in self.children:
            data.add(child.rewrite())

        return data


class StackedLine(Node):
    """
    Stacked interactions
    """
    pretty = "Stacked"

    def rewrite(self):
        """
        Retuns a BasePair obect
        """
        data = rnaview_data.BasePair(
            self.children[0].rewrite(),
            "",
            self.children[1].rewrite(),
            self.children[2].rewrite(),
            )

        return data

class StackedNode(Node):
    """
    Staked Node
    """
    pretty = "Staked"

    def rewrite(self):
        """
        Returns a string
        """
        return "stacked"


class DataLineNode(Node):
    """
    Node that represents a relevant data line
    """
    pretty = "Data"

    def rewrite(self):
        """
        Returns a BasePair
        """
        data = rnaview_data.BasePair(self.children[0].rewrite(),
                                     self.children[1].rewrite(),
                                     self.children[2].rewrite(),
                                     self.children[3].rewrite(),
                                    )
        return data


class BPPositionNode(Node):
    """
    Node that represents basepair positions
    """
    pretty = "Basepair positions"

    def rewrite(self):
        """
        Retuns a list of ints
        """
        return [int(i) for i in self.children.strip(",").split("_")]


class BasePairNode(Node):
    """
    Node that represents the base pairs
    """
    pretty = "Basepairs"

    def rewrite(self):
        """
        Retuns a list of strings
        """
        return [i for i in self.children.split("-")]


class TypeNode(Node):
    """
    Interaction type node
    """
    pretty = "Interaction type"

    def rewrite(self):
        """
        Retuns a string
        """
        return self.children

class OrientationNode(Node):
    """
    Orientation node
    """
    pretty = "Orientation"

    def rewrite(self):
        """
        Returns a string
        """
        return self.children
