#from virtual_cell.GenomicElement import *
#from virtual_cell.Position import *
#from compiler.ast import List
#from auxiliary import *
from VirtualMicrobes.virtual_cell.PhyloUnit import AddInheritanceType, PhyloUnit
import VirtualMicrobes.simulation.class_settings as cs
import matplotlib as mpl
from VirtualMicrobes.my_tools import utility as util
def _gen_id_func(x):
    return int(x) + 1

class Chromosome:

    """
     A list with all the positions on the chromosome. So far it is not apparent
     why there should be an additional encapsulation of GenomicElements in
     Position wrappers. If they do not provide a sufficient benefit in a real
     usecase, this layere may be taken out.
     
    positions

    :version:
    :author:
    """
    __metaclass__ = AddInheritanceType
    __phylo_type = cs.phylo_types['Chromosome']
    __slots__ = ['positions']
  
    uid = 0
    def __init__(self, gene_list = None, 
                 positions=None, 
                 time_birth=0, circular=False, **kwargs):
        super(Chromosome, self).__init__(time_birth=time_birth,**kwargs)
        if positions is not None:
            self.positions = positions
        else:
            self.init_positions(circular)
        if gene_list is not None:
            for g in gene_list:
                self.append_gene(g)

    def init_positions(self, circular=False):
        if circular:
            self.positions = util.CircularList()
        else:
            self.positions = list()

    def append_gene(self,g):
        self.positions.append(g)
    
    def translocate_stretch(self, start_pos, end_pos, target_pos, target_chrom):
        stretch = self.positions[start_pos:end_pos]
        prev_len = len(target_chrom)
        target_chrom.insert_stretch(stretch, target_pos)
        assert len(target_chrom) == prev_len + len(stretch)
        
    def invert(self,start_pos, end_pos):
        len_prev = len(self.positions)
        stretch = self.positions[start_pos:end_pos]
        stretch.reverse()
        self.positions[start_pos:end_pos] = stretch
        assert len(self.positions) == len_prev
        return stretch
    
    def tandem_duplicate(self, start_pos, end_pos):
        '''
        Duplicates a stretch of genes 'in place', right after end_pos 
        i.e. played on this chromosome.
        :param start_pos:
        :param end_pos:
        '''
        stretch = self.positions[start_pos:end_pos]
        self.insert_stretch(stretch, end_pos)
        return stretch
    
    def insert_stretch(self, stretch, pos, verbose=False):
        '''
        Insert a list of nodes at (=after) pos.
        :param stretch:
        :param pos:
        :param verbose:
        '''
        prev_len = len(self)
        self.positions[pos:pos] = stretch
        assert len(self) == prev_len + len(stretch) 
        
    def delete_stretch(self, start_pos, end_pos):
        '''
        Deletes a stretch of genes 'in place', i.e. played on this chromosome.
        :param start_pos:
        :param end_pos:
        '''
        prev_len = len(self)
        stretch = self.positions[start_pos:end_pos]
        del self.positions[start_pos:end_pos]
        assert len(self.positions) == prev_len - len(stretch) 
        return stretch
        
    @classmethod
    def fuse(cls, chrom1, chrom2, time, end1=True, end2=True):
        positions1 = chrom1.positions[:] 
        if not end2: positions1.reverse()
        positions2 = chrom2.positions[:]
        if end2: positions2.reverse()
        new_chrom = Chromosome(time_birth=time, positions= positions1+positions2)
        assert len(new_chrom) == len(chrom1) + len(chrom2)
        if isinstance(chrom1, PhyloUnit):
            new_chrom.set_ancestor(chrom1)
            new_chrom.set_ancestor(chrom2)
        new_chrom.id.from_parent(chrom1, flat=False)
        assert type(new_chrom.positions) == type(chrom1.positions) == type(chrom2.positions)
        chrom1.die(time)
        chrom2.die(time)
        return new_chrom
                    
    def fiss(self,pos, time, verbose=False): #creating shallow copies of list positions by slicing
        if verbose:
            print "fision of chromosome at position", pos
        subchrom1 = self._mutation_copy(time=time, with_positions=False) 
        subchrom1.positions = self.positions[:pos]
        subchrom2 = self._mutation_copy(time=time, with_positions=False) 
        subchrom2.positions = self.positions[pos:]
        assert len(self) == len(subchrom1) + len(subchrom2) 
        assert type(self.positions) == type(subchrom1.positions) == type(subchrom2.positions)
        self.die(time)
        return subchrom1,subchrom2 

    def duplicate(self, time, verbose=False):
        copy1 = self._mutation_copy(time=time)
        copy2 = self._mutation_copy(time=time)
        self.die(time)
        if verbose:
            print "ids: parent" + str(self.id), "copy1:" +str(copy1.id), "copy2:" +str(copy2.id)
        assert type(self.positions) == type(copy1.positions) == type(copy2.positions)
        return copy1,copy2
        
    def _reproduction_copy(self, orig_copy_genes_map, time):
        '''
        Make a copy of the chromosome when reproducing a cell. This copy should
        be independent of its ancestor so that changes in a child will not
        affect the parent. Copying of the "positions" attribute (containing genes)
        assumes that the genes in the list have
        already been copied ( _reproduction_copy(gene) ) so that the
        "children" attribute of the parental copy holds the newly produced
        "reproduction-copy" of the gene. These are then used to re-instantiate the
        positions of the new "reproduction-copy" of the chromosome.
        '''
        copied = super(Chromosome, self)._copy(time=time, new_id=False)
        copied.init_positions(circular=isinstance(self.positions, util.CircularList))
        for n in self.positions:
            new_copy = orig_copy_genes_map[n]
            copied.positions.append(new_copy)
        return copied
    
    def _mutation_copy(self, time, with_positions=True):
        mutant = super(Chromosome, self)._copy(time=time, flat_id=False)
        if with_positions:
            mutant.positions = self.positions[:]
        else:
            atr_cls = self.positions.__class__
            mutant.positions = atr_cls.__new__(atr_cls)
        return mutant
    
    def toJSON(self, index, *args, **kwargs):
        children = []

        for i,g in enumerate(self.positions):
            children.append(g.toJSON(index=i, *args, **kwargs))
                    
        d = {'name': 'Chr. ' + " #" + str(index+1),
             'description': 'Chromosome ' + str(self.id), 
             'colour': mpl.colors.rgb2hex(mpl.colors.colorConverter.to_rgb('lightgrey')),
             'children': children}
        return d 

    def __str__(self):
        out_str = "chr" + str(self.id) + ": "
        for p in self.positions:
            out_str += str(p) + " "
        return out_str
    
    def __len__(self):
        return len(self.positions)
    
    def __iter__(self):
        return iter(self.positions)

if __name__ == '__main__':
    chrom = Chromosome(range(10) , time_birth=0)
    print type(chrom.positions[:])
    print len(chrom.positions)
    print chrom.positions[10:14]
    print chrom.positions[9:14]
    print chrom.positions[-2:4]
    chrom.positions[-10:-10] = chrom.positions[-10:4]
    print chrom.positions
    print chrom.positions[-3:0]
    