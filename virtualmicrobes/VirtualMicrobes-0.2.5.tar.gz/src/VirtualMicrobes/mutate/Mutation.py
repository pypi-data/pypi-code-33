#from virtual_cell.Cell import Cell
from abc import abstractmethod

class MutationError(Exception):
    pass

class MutationAlreadyAppliedError(MutationError):
    def __init__(self, value="Cannot 'reapply' if already applied"):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class MutationNotAppliedError(Exception):
    def __init__(self, value="Cannot 'rewind' if not already applied"):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Mutation(object):

    """
     

    :version:
    :author:
    """

    uid = 0
    __slots__ = ['applied', 'genomic_target', 'post_mutation', 
                 'genomic_unit', 'time']
    
    def __init__(self, target, genomic_unit):
        self.applied = False
        self.genomic_target = target
        self.genomic_unit = genomic_unit 
                        
    @abstractmethod
    def mutate(self, time):
        self.applied = True
        self.time = time
    
    @abstractmethod
    def reapply(self):
        if self.applied:
            raise MutationAlreadyAppliedError
        self.applied = True

    @abstractmethod
    def rewind(self):
        """
         Go back to the ancestral state by patching the mutated cell with the unmutated
         genomic state.
         It should make a check that the genomic element is a part of this cell.

        :param virtual_cell.Cell mutant : On which cell do we play the reversal?
        :return  :
        :author
        """
        if not self.applied:
            raise MutationNotAppliedError
        self.applied = False

class ChromosomalMutation (Mutation):

    """
    """
    __slots__ = ()
    def __init__(self, chromosomes,genome):
        super(ChromosomalMutation,self).__init__(chromosomes,genome)

class ChromosomeDuplication (ChromosomalMutation):
    
    __slots__ = ()
    
    def __init__(self,chromosome, genome):
        super(ChromosomeDuplication,self).__init__(chromosome,genome)
    
    def mutate(self, time):
        copy1,copy2 = self.genomic_target.duplicate(time)
        self.post_mutation = [copy1,copy2]
        self.genomic_unit.del_chromosome(self.genomic_target, remove_genes=False)
        self.genomic_unit.add_chromosome(copy1) #.chromosomes += [copy1,copy2]
        self.genomic_unit.add_chromosome(copy2)
        super(ChromosomeDuplication,self).mutate(time)
        return self.genomic_unit
    
    def reapply(self):
        super(ChromosomeDuplication,self).reapply()
        self.genomic_unit.del_chromosome(self.genomic_target, remove_genes=False)
        for chrom in self.post_mutation:
            self.genomic_unit.add_chromosome(chrom)    
        return self.genomic_unit
    
    def rewind(self):
        super(ChromosomeDuplication,self).rewind()
        for chrom in self.post_mutation:
            self.genomic_unit.del_chromosome(chrom, remove_genes=False)
        self.genomic_unit.add_chromosome(self.genomic_target)    
        return self.genomic_unit

class StretchMutation(Mutation):
    
    __slots__ = ['start_pos', 'end_pos', 'stretch']
    
    def __init__(self, chromosome, genome, start_pos=None, end_pos=None, stretch=None):
        super(StretchMutation, self).__init__(chromosome, genome)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.stretch = stretch
        self.positive_positions()
        
    def positive_positions(self):
        if self.start_pos is not None and self.start_pos < 0: # ensure that we are working with purely positive indexes 
            shift = len(self.genomic_target)
            # this allows wrapping around to work properly in the case of circular genomes
            self.start_pos += shift
            if self.end_pos is not None:
                self.end_pos += shift
            #print 'start-end shifted to', self.start_pos, self.end_pos

class StretchDeletion(StretchMutation):
    
    __slots__ = ()
    
    def __init__(self, chromosome, genome, start_pos, end_pos):
        '''
        Tandem Duplication affects a single chromosome. It has a start and end position
        of the duplication stretch.
        '''
        super(StretchDeletion, self).__init__(chromosome,genome, start_pos, end_pos)
        
    def mutate(self, time):
        self.stretch = self.genomic_target.delete_stretch(self.start_pos, self.end_pos)
        assert len(self.stretch)
        self.genomic_unit.update_genome_removed_genes(self.stretch)
        super(StretchDeletion,self).mutate(time)
        return self.genomic_unit
        
    def rewind(self):
        super(StretchDeletion, self).rewind()
        self.genomic_target.insert_stretch(self.stretch, self.start_pos)
        return self.genomic_unit
    
    def reapply(self):
        super(StretchDeletion, self).reapply()
        self.genomic_target.delete_stretch(self.start_pos, self.end_pos)
        self.genomic_unit.update_genome_removed_genes(self.stretch)
        return self.genomic_unit
        
class TandemDuplication (StretchMutation):
    
    __slots__ = ()
    
    def __init__(self, chromosome, genome, start_pos, end_pos):
        '''
        Tandem Duplication affects a single chromosome. It has a start and end position
        of the duplication stretch.
        '''
        super(TandemDuplication, self).__init__(chromosome,genome, start_pos, end_pos)
        
    def mutate(self, time):
        self.stretch = self.genomic_target.tandem_duplicate(self.start_pos, self.end_pos)
        assert len(self.stretch)
        super(TandemDuplication,self).mutate(time)
        return self.genomic_unit
    
    def reapply(self):
        super(TandemDuplication, self).reapply()
        self.genomic_target.insert_stretch(self.stretch, self.end_pos)
        return self.genomic_unit
    
    def rewind(self):
        super(TandemDuplication, self).rewind()
        self.genomic_target.delete_stretch(self.start_pos, self.end_pos)
        return self.genomic_unit
        
class Inversion (StretchMutation):
    
    __slots__ = ()
    
    def __init__(self,chromosome, genome, start_pos, end_pos):
        super(Inversion,self).__init__(chromosome, genome, start_pos, end_pos) 
    
    def mutate(self, time):
        '''The invert is in place, hence pre- and post- mutation will appear the same'''
        self.stretch = self.genomic_target.invert(self.start_pos, self.end_pos)
        assert len(self.stretch) != 0
        super(Inversion, self).mutate(time)
        return self.genomic_unit
    
    def reapply(self):
        super(Inversion, self).reapply()
        self.genomic_target.invert(self.start_pos, self.end_pos)
        self.applied = False
        return self.genomic_unit
    
    def rewind(self):
        super(Inversion, self).rewind()
        self.genomic_target.invert(self.start_pos, self.end_pos)
        self.applied = False
        return self.genomic_unit

class Insertion (StretchMutation):
    '''
    Insertion of a stretch of exogenous genomic material
    '''
    
    __slots__ = ['insert_pos', 'is_external']
    
    def __init__(self, chromosome, genome, stretch, insert_pos, is_external):
        super(Insertion, self).__init__(chromosome, genome, stretch=stretch)
        self.insert_pos = insert_pos
        self.is_external = is_external
        
    def mutate(self, time):
        assert len(self.stretch)
        self.genomic_target.insert_stretch(self.stretch, self.insert_pos)
        super(Insertion, self).mutate(time)
        
    def rewind(self):
        super(Insertion, self).rewind()
        start_del_pos = self.insert_pos - len(self.stretch)
        self.genomic_target.delete_stretch(start_del_pos, self.insert_pos)
        self.genomic_unit.update_genome_removed_genes(self.stretch)
    
    def reapply(self):
        super(Insertion, self).reapply()
        self.genomic_target.insert_stretch(self.stretch, self.insert_pos)
    
class Translocation (StretchMutation):
    
    __slots__ = ['insert_pos','invert']
    
    def __init__(self, chromosome, genome, start_pos, end_pos, target_chrom, insert_pos, invert):
        super(Translocation, self).__init__((chromosome, target_chrom), genome, start_pos, end_pos)
        self.insert_pos = insert_pos
        self.invert = invert
        
    def positive_positions(self):
        if self.start_pos is not None and self.start_pos < 0: 
            shift = len(self.genomic_target[0])
            self.start_pos += shift
            if self.end_pos is not None:
                self.end_pos += shift
            #print 'start-end shifted to', self.start_pos, self.end_pos
        
    def mutate(self, time):
        orig, orig_target = self.genomic_target
        self.stretch = orig.delete_stretch(self.start_pos, self.end_pos)
        assert len(self.stretch)
        if self.invert:
            self.stretch.reverse()
        orig_target.insert_stretch(self.stretch, self.insert_pos)
        super(Translocation, self).mutate(time)
        
    def rewind(self):
        super(Translocation, self).rewind()
        orig, orig_target = self.genomic_target
        if self.invert:
            self.stretch.reverse()
        orig.insert_stretch(self.stretch, self.start_pos)
        start_del_pos = self.insert_pos - len(self.stretch)
        orig_target.delete_stretch(start_del_pos, self.insert_pos)
    
    def reapply(self):
        super(Translocation, self).reapply()
        orig, orig_target = self.genomic_target
        orig.delete_stretch(self.start_pos, self.end_pos)
        if self.invert:
            self.stretch.reverse()
        orig_target.insert_stretch(self.stretch, self.insert_pos)
        
class ChromosomeDeletion (ChromosomalMutation):
    
    __slots__ = ()
    
    def __init__(self,chromosome, genome):
        super(ChromosomeDeletion,self).__init__(chromosome,genome)
    
    def mutate(self, time):
        self.post_mutation = []
        self.genomic_unit.del_chromosome(self.genomic_target)
        super(ChromosomeDeletion,self).mutate(time)
        return self.genomic_unit
    
    def reapply(self):
        super(ChromosomeDeletion, self).reapply()
        self.genomic_unit.del_chromosome(self.genomic_target)
        return self.genomic_unit
    
    def rewind(self):
        super(ChromosomeDeletion, self).rewind()
        self.genomic_unit.add_chromosome(self.genomic_target)
        return self.genomic_unit
        
class Fusion (ChromosomalMutation):
    
    __slots__ = ['end1', 'end2']
    
    def __init__(self,chrom1, chrom2, genome, end1, end2):
        super(Fusion,self).__init__((chrom1,chrom2), genome)
        self.end1 = end1
        self.end2 = end2
    
    def mutate(self, time):
        target_cls = self.genomic_target[0].__class__
        fusion = target_cls.fuse(self.genomic_target[0], self.genomic_target[1], time, 
                               self.end1, self.end2)
        self.post_mutation = fusion
        for chrom in self.genomic_target:
            self.genomic_unit.del_chromosome(chrom, remove_genes=False)
        self.genomic_unit.add_chromosome(fusion)
        super(Fusion,self).mutate(time)
        return self.genomic_unit
    
    def reapply(self):
        super(Fusion, self).reapply()
        for chrom in self.genomic_target:
            self.genomic_unit.del_chromosome(chrom, remove_genes=False)
        self.genomic_unit.add_chromosome(self.post_mutation)
        return self.genomic_unit
    
    def rewind(self):
        super(Fusion, self).rewind()
        self.genomic_unit.del_chromosome(self.post_mutation, remove_genes=False)
        for chrom in self.genomic_target:
            self.genomic_unit.add_chromosome(chrom)
        return self.genomic_unit

    
class Fission (ChromosomalMutation):
    
    __slots__ = ['pos']
    
    def __init__(self,chromosome, genome, pos):
        super(Fission,self).__init__(chromosome, genome)
        self.pos = pos
        
    def mutate(self, time):
        subchrom1, subchrom2 = self.genomic_target.fiss(self.pos, time)
        self.post_mutation = [subchrom1, subchrom2]
        self.genomic_unit.del_chromosome(self.genomic_target, remove_genes=False)
        self.genomic_unit.add_chromosome(subchrom1) 
        self.genomic_unit.add_chromosome(subchrom2)
        super(Fission, self).mutate(time)
        return self.genomic_unit
    
    def reapply(self):
        super(Fission, self).reapply()
        self.genomic_unit.del_chromosome(self.genomic_target, remove_genes=False)
        for _chrom in self.post_mutation:
            self.genomic_unit.add_chromosome(self.post_mutation)   
    
    def rewind(self):
        super(Fission, self).rewind()
        for chrom in self.post_mutation:
            self.genomic_unit.del_chromosome(chrom, remove_genes=False)
        self.genomic_unit.add_chromosome(self.genomic_target)    
        return self.genomic_unit
    

class SingleGeneMutation (Mutation):
    
    __slots__ = ['pos']
    
    def __init__(self, gene , chromosome, pos):
        super(SingleGeneMutation,self).__init__(gene, chromosome)
        self.pos = pos

    def mutate(self, time):
        return super(SingleGeneMutation, self).mutate(time)

    def reapply(self):
        super(SingleGeneMutation, self).reapply()

    def rewind(self):
        super(SingleGeneMutation, self).rewind()
    
class SGDeletion (SingleGeneMutation):    
    pass

    
class SGDuplication (SingleGeneMutation):
    pass
        
class PointMutation (SingleGeneMutation):
    
    __slots__ = ['par', 'new_val']
    
    def __init__(self,gene, chromosome, par, new_val, pos):
        super(PointMutation,self).__init__(gene, chromosome, pos)
        self.par = par
        self.new_val = new_val
        
    def mutate(self, time):
        self.post_mutation = self.genomic_target.mutated(self.par, self.new_val, time)
        self.genomic_unit.positions[self.pos] = self.post_mutation
        super(PointMutation, self).mutate(time)        
        return self.genomic_unit

    def reapply(self):
        super(PointMutation, self).reapply()
        self.genomic_unit.positions[self.pos] = self.post_mutation
        return self.genomic_unit

    def rewind(self):
        super(PointMutation, self).rewind()
        self.genomic_unit.positions[self.pos] = self.genomic_target
        return self.genomic_unit

class OperatorInsertion (SingleGeneMutation):
    
    __slots__ = ['par', 'new_val']
    
    def __init__(self,gene, chromosome, new_val, pos):
        super(OperatorInsertion,self).__init__(gene, chromosome, pos)
        self.par = 'operator'
        self.new_val = new_val
        
    def mutate(self, time):
        self.post_mutation = self.genomic_target.mutated(self.par, self.new_val, time)
        self.genomic_unit.positions[self.pos] = self.post_mutation
        super(OperatorInsertion, self).mutate(time)        
        return self.genomic_unit

    def reapply(self):
        super(OperatorInsertion, self).reapply()
        self.genomic_unit.positions[self.pos] = self.post_mutation
        return self.genomic_unit

    def rewind(self):
        super(OperatorInsertion, self).rewind()
        self.genomic_unit.positions[self.pos] = self.genomic_target
        return self.genomic_unit  
