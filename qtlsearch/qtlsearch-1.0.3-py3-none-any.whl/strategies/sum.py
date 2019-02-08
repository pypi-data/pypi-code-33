#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains a very basic propagation
    strategy, combining through summation.

    QTLSearch is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    QTLSearch is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with QTLSearch.  If not, see <http://www.gnu.org/licenses/>.
'''
from ..OBOParser import ONTOLOGIES
from ..HOGParser import is_orthologGroup_node, is_paralogGroup_node, \
                        is_geneRef_node
from .utils import STRATEGY
from collections import defaultdict
from copy import copy
from itertools import groupby


def add_arguments(parser):
    '''
        Adds arguments to overall program's parser.
    '''
    parser.add_argument('--bound', default=None, type=float,
                        help='[Default is None] Decision boundary for belief.')
    parser.add_argument('--orthotrustfactor', default=0.85, type=float,
                        help='[Default is 0.85] Trust factor (decay) in '
                             'belief for orthologue nodes.')
    parser.add_argument('--paratrustfactor', default=0.7225, type=float,
                        help='[Default is 0.7225] Trust factor (decay) in '
                             'belief for paralogue nodes.')


def save_arguments(args):
    STRATEGY.save_args(['bound', 'orthotrustfactor', 'paratrustfactor'], args)


class Strategy(object):
    '''
        Basic1 is a strategy which when travelling up sums the alpha scores and
        decays constantly. When propagating down, alpha scores also decay
        constantly.
    '''
    sourcestr = 'HOG-Sum'

    def __init__(self, hog, *args, **kwargs):
        '''
            Initialise the strategy with arguments.
        '''
        self.bound = STRATEGY.args['bound']
        self.orthotrustfactor = STRATEGY.args['orthotrustfactor']
        self.paratrustfactor = STRATEGY.args['paratrustfactor']

    def get_trustfactor(self, node):
        '''
            Get the trustfactor dependent on the node type.
        '''
        if node is not None:
            if is_orthologGroup_node(node):
                return self.orthotrustfactor
            elif is_paralogGroup_node(node):
                return self.paratrustfactor
            else:
                # geneRef
                return 1.0
        else:
            # Root node.
            return 1.0

    def combine_up(self, node, child_terms):
        '''
            This method merges the function of direct children into the node.
        '''
        if not is_geneRef_node(node):
            # Get the trustfactor dependent on type of node.
            tf = self.get_trustfactor(node)

            # Annotations at node are the sum of those below.
            annots = defaultdict(dict)
            for (_, a) in child_terms:
                for t in a:
                    if t.id not in annots[t.ont]:
                        # New annotation. Make a copy
                        term = copy(t)
                        term.set_source(self.sourcestr)
                        term.decay_belief(tf)

                        annots[term.ont][term.id] = term
                    # elif t.annots[t.id].is_not != t.is_not:
                    #     raise ValueError('Trying to propagate annotation to '
                    #                      'a node with a NOT annotation or '
                    #                      'vice-versa.')
                    else:
                        # Sum belief
                        annots[term.ont][t.id].add_belief(t.get_belief() * tf)
                        annots[term.ont][t.id].update_relevant_genes(
                            t.relevant_genes)

                        # # Probably don't need to set belief.
                        # annots[t.id].set_source(self.sourcestr)
            return self.consolidate(annots)

        else:
            # geneRef node.
            return list(child_terms[0])

    def combine_down(self, parent_node, parent_terms, node, node_terms):
        '''
            This method merges the terms when pushing down the tree.
        '''
        # Get the trustfactor dependent on type of parent node
        tf = self.get_trustfactor(parent_node)

        # Convert annotations to dictionary
        annots = defaultdict(dict)
        for t in node_terms:
            annots[t.ont][t.id] = t

        # For each parent term, work out whether we have a new term or one which
        # we're more confident in.
        for term in parent_terms:
            if term.id not in annots[term.ont]:
                # New term
                t = copy(term)
                t.set_source(self.sourcestr)
                t.decay_belief(tf)
                annots[t.ont][t.id] = t
            else:
                # Check for +ve / -ve. If +ve check parents for -ve / if -ve
                # check children for +ve.
                if term.ont in ONTOLOGIES:
                    func = (ONTOLOGIES[term.ont].parents if not term.is_not
                            else ONTOLOGIES[term.ont].children)
                    s = ({t for t in annots[term.ont].keys()} &
                         func(term.id, include_self=True))
                else:
                    # No ontology
                    s = {term.id}

                # Check all the same sign for this...
                # 1. find intersection of annots with term parents / children.
                # 2. check sign of all of these that exist in the db
                if len({annots[term.ont][t].is_not for t in s}) > 1:
                    # print('Blocked NOT annotation propagation...')
                    # raise ValueError('Trying to propagate annotation to a '
                    #                  'node with a NOT annotation or '
                    #                  'vice-versa.')
                    pass
                elif (annots[term.ont][term.id].get_belief() <
                      (term.get_belief() * tf)):
                    # Match - max alpha is in parent so copy it and decay.
                    t = copy(term)
                    t.set_source(self.sourcestr)
                    t.decay_belief(tf)
                    annots[t.ont][t.id] = t

        return self.consolidate(annots, bound=(is_geneRef_node(node)))

    def consolidate(self, annots, bound=False):
        # Consolidate the annotations. i.e., ensure only most specific for
        # those with > some predefined alpha. If bound is not set, all
        # annotations will be returned and this can be done separately.
        def filter_terms(t):
            return ((not bound) or
                    (self.bound is None) or
                    t.get_belief() >= self.bound or
                    (not t.get_source().lower().startswith('hog')))

        # Final annots needs to be double-flattened. First layer is ont, second
        # term id.
        ret = []
        for (ont, ont_ts) in annots.items():
            ont_ts = groupby(sorted(filter(filter_terms, ont_ts.values()),
                                    key=lambda t: t.is_not),
                             key=lambda t: t.is_not)

            # Sort annotations by belief - the terms with lower belief are then
            # overwritten by those with greater, later.
            # Note: AnnotationTerms have a unique hash.
            for (is_not, ont_ts_set) in map(lambda x: (x[0], list(x[1])),
                                            ont_ts):
                if ont not in ONTOLOGIES:
                    z = {t.id: t
                         for t in sorted(ont_ts_set,
                                         key=lambda t: t.get_belief())}
                    ret += list(set(z.values()))
                else:
                    func = (ONTOLOGIES[ont].parents if not is_not else
                            ONTOLOGIES[ont].children)

                    z = {t1: t
                         for t in sorted(ont_ts_set,
                                         key=lambda t: t.get_belief())
                         for t1 in (func(t.id, include_self=True) &
                                    set(map(lambda t: t.id, ont_ts_set)))}
                    ret += list(set(z.values()))
        return ret
