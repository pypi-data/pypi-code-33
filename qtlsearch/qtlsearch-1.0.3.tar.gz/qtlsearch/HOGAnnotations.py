#!/usr/bin/env python
'''
    QTLSearch — to search for candidate causal genes in QTL studies
     by combining Gene Ontology annotations across many species, leveraging
    hierarchical orthologous groups.

    (C) 2015-2018 Alex Warwick Vesztrocy <alex@warwickvesztrocy.co.uk>

    This file is part of QTLSearch. It contains a class definition for a
    structure to hold the annotations for every node in a Hierarchical
    Orthologous Group (HOG).

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
from .Annotations import AnnotationTerm
from .HOGParser import is_evolutionary_node, is_geneRef_node, tag_name, \
                       NS
from .OBOParser import ONTOLOGIES
from .strategies.utils import STRATEGY
from collections import defaultdict
from copy import copy
from lxml import etree
from numbers import Number


class HOGAnnotations(object):
    '''
        This class defines a structure to hold annotations for every node in a
        Hierarchical Orthologous Group (HOG).
    '''

    def __init__(self, hog, *args, **kwargs):
        '''
            Initialisation. Loads up annotations from a dictionary passed as an
            argument.
        '''
        # Initialise the strategy for this set of annotations.
        self.strategy = (STRATEGY.get_strategy().Strategy(hog, *args, **kwargs)
                         if STRATEGY.is_set else None)

        # Backup reference
        self.hog = hog
        # self.hog_state = [None, None, None]

        if 'annots' in kwargs:
            # Load up the annotations passed
            self.annotations = []
            self._load_annots(kwargs['annots'])
        else:
            # Load from XML
            self.annotations = self._load_annots_xml()

        self._backup_annotations = copy(self.annotations)

    def remove_other_annotations(self, id, annots=None, take_copy=None):
        '''
            Remove all other annotations except for id.
        '''
        annots = self.annotations if annots is None else annots
        self.annotations = list(map(lambda t:
                                    set(map(lambda t: (copy(t) if take_copy else
                                                       t),
                                            filter(lambda a: (a.id == id),
                                                   t))),
                                    annots))

    def reset(self, id=None):
        '''
            Reset annotations.
        '''
        if id is not None:
            annots = (self._backup_annotations +
                      [set()] * (len(self.annotations) -
                                 len(self._backup_annotations)))
            self.remove_other_annotations(id,
                                          annots=annots,
                                          take_copy=True)
        else:
            self.annotations = (copy(self._backup_annotations) +
                                [set()] * (len(self.annotations) -
                                           len(self._backup_annotations)))

    def _load_annots(self, global_annots):
        '''
            Loads up the annotations into the structure.
        '''
        # For every gene in the HOG, if annotations exist save them!
        for gene in self.hog.geneRefs():
            gene_id = int(gene.get('id'))

            annots = global_annots.annotations.get(gene_id)
            if annots is not None:
                for annot in annots:
                    annot.set_relevant_genes((gene_id, annot.get_source()))
                self.save(set(annots), gene)

    def _load_annots_xml(self):
        '''
            Loads up the annotations from the XML.
        '''
        def annot_xml_to_term(node):
            '''
                Turns an XML annotation node into an AnnotationTerm required for
                HOGPROP.
            '''
            # Get the ontology of the annotation
            ont = node.attrib['ont']

            # Get annotation ID - turn into int if ontology declared
            id = node.attrib['id']
            id = (ONTOLOGIES[ont]._id_to_int(id) if ont in ONTOLOGIES else id)
            # Get alpha score, etc.
            alpha = float(node.attrib['alpha'])
            is_not = (node.attrib['is_not'] == '1')
            source = node.attrib['source']
            t = AnnotationTerm(id, ont, alpha, is_not=is_not, source=source)

            z = defaultdict(set)
            for y in map(lambda y: y.split(';'),
                         node.attrib['relevant_genes'].split('@')):
                z[y[0]].update(set(map(int, y[1:])))

            t.update_relevant_genes(z)
            return t

        # Load genes
        genes = sorted(filter(lambda g: ('annots' in g.attrib),
                              self.hog.geneRefs()),
                       key=lambda g: int(g.attrib['annots']))

        # Now load the actual annotations.
        annots = [{annot_xml_to_term(a)
                   for a in gene.findall('.//OrthoXML:annotation', NS)}
                  for gene in genes]

        # Delete the <notes> tags containing only annotations
        for n in self.hog.struct.findall('.//OrthoXML:notes', NS):
            if all(a.tag == tag_name('annotation') for a in n.findall('.//*')):
                n.getparent().remove(n)

        return annots

    def is_empty(self):
        '''
            Returns boolean dependent on if there are *no* annotations loaded in
            the HOG.
        '''
        return self.annotations == []

    def save(self, annots, node):
        '''
            Saves a set of annotations in this object, then saves a reference
            to this in the XML node.
        '''
        # Check there are annotations to save.
        if annots:
            # Save the annotations in the array
            self.annotations.append(annots)

            # Get the index of the annotations
            i = len(self.annotations) - 1

            # Save the location in the XML
            self._save_loc_in_node(i, node)

    def _save_loc_in_node(self, i, node):
        '''
            Saves the location in the HOG annotations array of a particular
            node's annotations.
        '''
        # Save in the attribute of the node.
        node.attrib['annots'] = str(i)

    def _get_loc_from_node(self, node):
        '''
            Get the location in the HOG annotations array of a particular node's
            annotations.
        '''
        if 'annots' in node.attrib:
            # Node has attribute that holds the location.
            return int(node.attrib['annots'])
        else:
            # Node doesn't have any annotations.
            return None

    def update(self, annots, node):
        '''
            Update the annotations at a particular node.
        '''
        # Get the location in the array of HOG annotations.
        i = self._get_loc_from_node(node)

        # Ensure no zero-belief values in annots
        annots = set(filter(lambda a: a.get_belief() > 0, annots))

        if i is not None:
            # Already has annotations. Replace them with this list
            self.annotations[i] = annots

        else:
            # Node doesn't have any annotations yet. Save them with no
            # complaints...
            self.save(annots, node)

    def get(self, node):
        '''
            Get the annotations associated with a particular node.
        '''
        # Get the location in array of HOG annotations
        i = self._get_loc_from_node((node if not isinstance(node, Number) else
                                     self.hog.get_gene(node)))

        if i is not None:
            # Return annotations at node
            return self.annotations[i]

        else:
            # No annotations at node
            return set()

    def propagate_up(self):
        '''
            Outer method for propagating annotations up the hierarchy.
        '''
        assert (self.strategy is not None), 'Strategy must be set to propagate.'
        # self.hog_state[0] = self.hog.tostring(gz=True)
        self._propagate_up_inner(self.hog.struct)
        # self.hog_state[1] = self.hog.tostring(gz=True)

    def _propagate_up_inner(self, node):
        '''
            Inner method for propagating annotations up the hierarchy,
            recursively.
        '''
        if is_evolutionary_node(node):
            # Recursively compute functions of children nodes
            child_terms = []
            for child in filter(lambda x: (is_evolutionary_node(x) or
                                           is_geneRef_node(x)),
                                node):
                child_terms.append((child, self._propagate_up_inner(child)))

            # Combine all functions by passing *list of sets*
            combined_terms = self.strategy.combine_up(node, child_terms)

            # Store here.
            self.update(combined_terms, node)

            # Return
            return combined_terms

        elif is_geneRef_node(node):
            combined_terms = self.strategy.combine_up(node,
                                                      [self.get(node)])
            # Update stored terms
            self.update(combined_terms, node)
            return combined_terms
        else:
            return []

    def push_down(self):
        '''
            Outer method for pushing annotations down the hierarchy.
        '''
        assert (self.strategy is not None), 'Strategy must be set to propagate.'
        self._push_down_inner(None, self.hog.struct)
        # self.hog_state[2] = self.hog.tostring(gz=True)

    def _push_down_inner(self, parent_node, node, parent_terms=[]):
        '''
            Inner method for pushing annotations down the hierarchy,
            recursively.
        '''
        def filter_for_targets(child):
            if self.hog.targets is None:
                return True
            else:
                # Get list of genes below this node.
                if is_geneRef_node(child):
                    return (int(child.attrib['id']) in self.hog.targets)
                elif is_evolutionary_node(node):
                    return len(self.hog._gene_ids(child) & self.hog.targets) > 0

        if is_evolutionary_node(node) or is_geneRef_node(node):
            terms = self.strategy.combine_down(parent_node,
                                               parent_terms,
                                               node,
                                               self.get(node))

            self.update(terms, node)

            # Recurse on node's children
            for child in filter(filter_for_targets, list(node)):
                self._push_down_inner(node, child, terms)

    def include_in_xml(self, delete=True):
        '''
            Outer method for including the annotations held in this object in
            the OrthoXML structure.
        '''
        if delete:
            # Delete the <notes> tags containing only annotations
            for n in self.hog.struct.findall('.//OrthoXML:notes', NS):
                if all(a.tag == tag_name('annotation')
                       for a in n.findall('.//*')):
                    n.getparent().remove(n)

        self._include_in_xml_inner(self.hog.struct)

    def _include_in_xml_inner(self, node):
        '''
            Inner method for including the annotations held in this object in
            the OrthoXML sturcture. This is done so as to preserve OrthoXML
            compliancy. So, at each level annotations are added as "annotation"
            elements, within "notes" elements.

            TODO: change this to loop over the nodes with "annots" attribs.
        '''
        # Get node's annotation index
        i = self._get_loc_from_node(node)

        if i is not None:
            # Add annotation under notes, as this is still valid OrthoXML.
            annotations = etree.Element(tag_name('notes'))

            # For every annotation, add it as a seperate element under notes.
            for annot in self.annotations[i]:
                relevant_genes = ''
                for (source, gs) in annot.relevant_genes.items():
                    relevant_genes += '@' if len(relevant_genes) > 0 else ''
                    relevant_genes += (source + ';' + ';'.join(map(str, gs)))

                attribs = {
                    'id': (ONTOLOGIES[annot.ont]._id_to_str(annot.id)
                           if annot.ont in ONTOLOGIES else annot.id),
                    'ont': annot.ont,
                    'relevant_genes': relevant_genes,
                    'alpha': str(annot.get_belief()),
                    'source': str(annot.get_source()),
                    'is_not': str(1 if annot.is_not else 0)}

                annotations.append(etree.Element(tag_name('annotation'),
                                                 attrib=attribs))
            node.append(annotations)

        # Recurse on node's children
        for child in node:
            self._include_in_xml_inner(child)

    def results(self):
        '''
            Returns a list of the resulting predictions.
        '''
        for gene in self.hog.geneRefs():
            i = self._get_loc_from_node(gene)

            if i is not None:
                entry_num = int(gene.attrib['id'])

                for annot in self.annotations[i]:
                    yield ResultTerm(entry_num,
                                     annot,
                                     ONTOLOGIES.get(annot.ont))

    def save_state(self, args):
        '''
            Saves the state of the HOG propagation for each step to the DB.
        '''
        hog_db = getattr(args, 'hog_db', None)
        # hog_db = hog_db if hog_db is not None else hogprop.Worker.hog_db

        hog_db.add(self.hog.id, *self.hog_state)


class ResultTerm(object):
    def __init__(self, entry_id, annot, ontology):
        self.entry_id = entry_id
        self.annot = annot
        self.ontology = ontology

    def as_array(self):
        return [self.entry_id,
                (self.ontology._id_to_str(self.annot.id)
                 if self.ontology is not None else self.annot.id),
                str(1 if self.annot.is_not else 0),
                '{:.3e}'.format(self.annot.get_belief()),
                str(self.annot.get_source())]

    def set_protId(self, args):
        # Sets protId as the entry_id.
        self.entry_id = args.species.get_xref(self.entry_id)

    @property
    def pred_id(self):
        return self.annot.id

    @property
    def is_not(self):
        return self.annot.is_not

    @property
    def belief(self):
        return self.annot.get_belief()

    @property
    def source(self):
        return self.annot.get_source()
