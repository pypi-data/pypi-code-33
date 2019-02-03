#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 10:41:07 2019

@author: Maria Climent-Pommeret
"""

from dataclasses import dataclass, field
from typing import List
from prettytable import PrettyTable
import csv

TYPES = ["std", "W/W", "H/H", "S/S", "W/H", "W/S", "H/S","stacked"]


def create_interactions(basepairs, interactions):
    """
    Factory to generate child classes.
    
    Parameters:
        - basepairs: a deck of BasePair
        - interactions: list of strings of interactions types.
    """
    return [basepair
            for basepair in basepairs.deck
            if basepair.interaction_type in interactions
            ]

@dataclass
class BasePair:
    """
    Base class for representing BasePairs.
    """
    orientation: str
    position_1: int
    position_2: int
    base_1: str
    base_2: str
    interaction_type: str

    def __init__(self, interaction_type, orientation, positions, basepair):
        """
        Parameters:
            - interaction_type: one of TYPES
            - orientation: either "cis", "tran" or empty string
            - positions: list of two ints representing the base position
            - basepair: list of two strings reprenting the basepair
        """
        self.interaction_type = interaction_type
        self.orientation = orientation
        self.position_1 = positions[0]
        self.position_2 = positions[1]
        self.base_1 = basepair[0]
        self.base_2 = basepair[1]

    def __eq__(self, other):
        """
        Equality test between two base pairs
        """
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.interaction_type, self.orientation, self.position_1, self.position_2, self.base_1, self.base_2) == (other.interaction_type, other.orientation, other.position_1, other.position_2, other.base_1, other.base_2)

    def __str__(self):
        """
        Returns a fornatted string of the object.
        """
        return f'{self.position_1}{self.positon_2}{self.interaction_type}'


@dataclass
class BasePairs:
    """
    Deck of BasePair
    """
    deck: List[BasePair] = field(default_factory=list)
    interaction_type = TYPES

    def add(self, other):
        """
        Adds another BasePair to the deck.
        
        Parameters:
            - other: another BasePair
        """
        if type(other) is not BasePair:
            return NotImplementedError
        else:
            self.deck.append(other)

    def find_interaction_by_position(self, position):
        """
        Finds every occurance of interactions involving a given position in
        the sequence.
        
        Returns a tuple:
            - number of interactions
            - list of BasePair involved
        Parameters:
            - position: an int
        """
        data = []
        for child in self.deck:
            if position == child.position_1 or position == child.position_2:
                data.append(child)
        return len(data), data
    
    def find_interaction_by_list(self, positions):
        """
        Finds every occurance of interaction in a list of positions that
        represents a basepair.
        
        Returns a tuple:
            - number of interactions
            - list of BasePairs involved
        
        Parameters:
            - positions: list of two ints
        """
        data = []
        for child in self.deck:
            if child.position_1 in positions and child.position_2 in positions:
                data.append(child)
        return len(data), data

    def find_interaction_by_type(self, types):
        """
        Finds all BasePairs involved in a given type of interaction.
        
        Returns a tuple:
            - number of interactions found
            - list of BasePair involved
        
        Parameters:
            - types: a string representing the type
        """
        data = []
        for child in self.deck:
            if types == "std":
                if child.interaction_type in ["+/+", "-/-"]:
                    data.append(child)
            if child.interaction_type == types:
                data.append(child)
        return len(data), data

    def generate_interactions(self):
        """
        Generates all sub-classes of interactions, by interaction type.
        
        Returns a dict:
            - key: interaction type
            - value: instance of a class containing a deck
        """
        data = {}
        for (types, classes) in zip(TYPES, CLASSES):
            data[types] = classes(self)
        return data

    def pretty(self):
        """
        Pretty prints the deck
        """
        table = PrettyTable()
        table.field_names = ["Interaction type", "Orientation", "Total", ]
        for j in range(0, len(self.interaction_type) - 1):
            table.add_row([TYPES[j],
                           "cis",
                           len([i for i in self.deck
                                if i.interaction_type == TYPES[j]
                                and i.orientation == "cis"
                               ]),
                           ])
            table.add_row([TYPES[j],
                           "trans",
                           len([i for i in self.deck
                                if i.interaction_type == TYPES[j]
                                and i.orientation == "tran"
                                ])
                    ])
        if "stacked" in self.interaction_type:
            table.add_row(["stacked",
                           "",
                           len([i for i in self.deck
                                if i.interaction_type == "stacked"
                                ]),
                    ])
        print(table)


    def csv(self, filepath):
        """
        Creates a CSV of the deck.
        
        Parameters:
            - filepath: path to CSV to be written.
        """
        with open(filepath, "w", newline="\n") as csvfile:
            writer = csv.writer(csvfile,
                                delimiter=",",
                                quotechar="'",
                                quoting=csv.QUOTE_MINIMAL,
                                )
            writer.writerow([
                    "Interaction type",
                    "Orientation",
                    "Position 1",
                    "Position 2",
                    "Base 1",
                    "Base 2",
                    ])
            for base in self.deck:
                writer.writerow([
                        base.interaction_type,
                        base.orientation,
                        base.position_1,
                        base.position_2,
                        base.base_1,
                        base.base_2,
                        ])
        
@dataclass
class Stacked(BasePairs):
    interaction_type: str = "stacked"
    
    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["stacked",])


@dataclass
class Std(BasePairs):
    interaction_type: str = "std"
    
    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["+/+", "-/-"])


@dataclass
class WW(BasePairs):
    interaction_type: str = "WW"

    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["W/W"])

@dataclass
class HH(BasePairs):
    interaction_type: str= "HH"

    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["H/H"])

@dataclass
class SS(BasePairs):
    interaction_type: str = "SS"

    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["S/S"])

@dataclass
class WH(BasePairs):
    interaction_type: str = "WH"

    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["W/H"])

@dataclass
class WS(BasePairs):
    interaction_type: str = "WS"

    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["W/S"])


@dataclass
class HS(BasePairs):
    interaction_type: str = "HS"

    def __init__(self, basepairs):
        self.deck = create_interactions(basepairs, ["H/S"])


CLASSES = [Std, WW, HH, SS, WH, WS, HS, Stacked]
