#from virtual_cell.Chromosome import *
from VirtualMicrobes.virtual_cell.PhyloUnit import AddInheritanceType
import VirtualMicrobes.simulation.class_settings as cs

def _gen_id_func(x):
    return int(x) + 1

class GenomicElement:

    """
     

    :version:
    :author:
    """

    """ ATTRIBUTES

     How often and by which type of mutation has this GE been affected.

    mutation_counts  (private)

    """
    __phylo_type = cs.phylo_types['GenomicElement']
    __metaclass__ = AddInheritanceType
    __slots__ = []
    
    uid = 0
    types = ['tf','pump','enz']
    
    def __init__(self, time_birth=0, **kwargs):     
        super(GenomicElement, self).__init__(time_birth=time_birth, **kwargs)

    def _hgt_copy(self, time):
        '''
        Copy method in the case of horizontally transferred gene.
        (For now it is identical to _mutation_copy method
        '''
        copied = super(GenomicElement, self)._copy(time=time, new_id=False)
        return copied
    
    def _reproduction_copy(self, time):
        copied = super(GenomicElement, self)._copy(time=time, new_id=False)
        return copied
    
    def _mutation_copy(self, time):
        '''
        Makes a (partial) deep copy of a genomic element, when a gene is
        mutated. In this way the pre- and post-mutation state of the gene can be
        independently stored, enabling resurrection of the pre-mutation gene.
        Operator and BindingSequence attributes will not be copied, which will
        mutant in different gene variants being able to hold exactly the same
        operator/binding-sequence. Consequently, significant efficiency gains
        can potentially be had when recalculating binding interactions between
        BS and Op in the genome, if there is a lot of sharing of BS and Op
        sequences.
        '''
        mutant = super(GenomicElement, self)._copy(time=time,flat_id=False)
        return mutant

    def __str__(self):
        out_str = "g" + str(self.id) + " "
        return out_str

