from copy import copy, deepcopy
import itertools
import matplotlib as mpl
from orderedset import OrderedSet 
from VirtualMicrobes.my_tools.utility import OrderedDefaultdict
import collections
class Genome(object):

    """
    """
    
    class_version = '1.0'
        
    def __init__(self, chromosomes, min_bind_score):
        
        self.version = self.__class__.class_version
        
        self.init_chromosomes(chromosomes)
        self.init_regulatory_network(min_bind_score)
        self.genes_removed = set()
        self.chromosomes_removed = set()
        
    @property        
    def size(self):
        return self.__len__()

    @property
    def tfs(self):
        return ( g for g in self if g['type'] == 'tf' ) 
    
    @property
    def enzymes(self):
        return ( g for g in self if g['type'] == 'enz' ) 
    
    @property
    def pumps(self):
        return ( g for g in self if g['type'] == 'pump' )  
    
    @property
    def eff_pumps(self):
        return [ p for p in self.pumps if p['exporting'] ]
    
    @property
    def inf_pumps(self):
        return [ p for p in self.pumps if not p['exporting'] ]
    
    @property
    def copy_number_dist(self):
        return collections.Counter(  self.copy_numbers.values() )
    
    @property
    def copy_numbers(self):
        return collections.Counter( [ ge['type']+str(ge.id.major_id) for ge in self ])

    @property
    def copy_numbers_tfs(self):
        return collections.Counter( [ str(ge.id.major_id)+str(ge.ligand_class) for ge in self.tfs ])
    
    @property
    def copy_numbers_enzymes(self):
        return collections.Counter( [ str(ge.id.major_id) for ge in self.enzymes ])
    
    @property
    def copy_numbers_inf_pumps(self):
        return collections.Counter( [ str(ge.id.major_id) for ge in self.inf_pumps ])
    @property
    def copy_numbers_eff_pumps(self):
        return collections.Counter( [ str(ge.id.major_id) for ge in self.eff_pumps ])
        
    @property
    def operators(self):
        return OrderedSet(g.operator for g in self)
    
    @property
    def binding_sequences(self):
        return OrderedSet(g.binding_sequence for g in self.tfs)
    
    def init_chromosomes(self, chromosomes):
        '''
        Initialize chromosomes.
        
        Add preinitialized chromosomes to the genome.
        
        Parameters
        ----------
        chromosomes : iterable of class:`virtual_cell.Chromosome.Chromosome`
            chromosomes to add
        '''
        self.chromosomes = []
        for chrom in chromosomes:
            self.add_chromosome(chrom)
            
    def add_chromosome(self,chrom, verbose=False):
        '''
        Add a chromosome to the list of chromosomes.
        '''
        if verbose:
            print "adding chromosome", chrom
        self.chromosomes.append(chrom)
    
    def del_chromosome(self,chrom, remove_genes=True, verbose=False): 
        '''
        Delete a chromosome.
        
        Remove a chromosome from the list of chromosomes. If `remove_genes` is
        True the genome will be further updated to reflect deletion of genes.
        E.g. the sequence bindings should be updated when genes are removed from
        the genome. It may be useful to defer updating if it is already known
        that the genes will be readded immediately. This may be the case when a
        chromosome is split (fission) or fused and no genes will be actually
        lost from the genome.
        
        Parameters
        ----------
        chrom : class:`virtual_cell.Chromosome.Chromosome`
            chromosome to be removed
        remove_genes : bool
            if True update the genome
        verbose : bool
            be verbose
        '''
        if verbose:
            print "deleting chromosome", chrom   
        self.chromosomes.remove(chrom)
        if remove_genes:
            self.chromosomes_removed.add(chrom)
            self.update_genome_removed_genes(chrom.positions)
        
    def bs_to_tfs_dict(self):
        '''
        Create mapping from binding sequences to tfs. 
        
        For each binding sequence in the genome map to the set of tfs that 
        contain this binding sequence
        
        Returns
        -------
        mapping from class:`virtual_cell.Sequence.BindingSequence` to set 
        of class:`virtual_cell.Gene.TranscriptionFactor
        '''
        d = collections.OrderedDict()
        for bs in self.binding_sequences:
            d[bs] = OrderedSet(tf for tf in self.tfs if tf.binding_sequence == bs)
        return d 
    
    def op_to_tfs_scores_dict(self):
        '''
        Create mapping from operators to the tfs that bind them, with their scores.
        
        For each operator in the genome map the set of tfs, together with their
        binding scores.
        
        Returns
        -------
        mapping from class:`virtual_cell.Sequence.Operator` to set 
        of class:`virtual_cell.Gene.TranscriptionFactor, binding-score (float) tuples.
        '''
        op_to_tfs_scores = OrderedDefaultdict(list)
        bs_to_tf_dict = self.bs_to_tfs_dict()
        for op in self.operators:
            for bs, score in op.binding_sequences.items():
                for tf in bs_to_tf_dict[bs]:
                    op_to_tfs_scores[op].append((tf,score))
        return op_to_tfs_scores
        
    def binding_tfs_scores(self, op):
        '''
        Return tfs that bind this operator and their scores.
         
        Parameters
        ----------
        op : class:`virtual_cell.Sequence.Operator`
            operator sequence 
            
        Returns
        -------
        list of class:`virtual_cell.Gene.TranscriptionFactor`, float tuples
        '''
        tfs_scores = list()
        bs_to_tf_dict = self.bs_to_tfs_dict()
        for bs, score in op.binding_sequences.items():
            for tf in bs_to_tf_dict[bs]:
                tfs_scores.append((tf,score))
        return tfs_scores
    
    def update_regulatory_network(self, min_bind_score):
        '''
        Update the binding state of the regulatory network.
        
        Iterate over all Sequences in the genome and if their check_binding flag
        is set, match the sequence against all potential binders in the genome.
        
        Parameters
        ----------
        min_bind_score : float
            minimum binding score for sequence matching
        '''
        for op in self.operators:
            if op.check_binding:
                op.update_binding_sequences(self.binding_sequences, min_bind_score)
            for bs in op.binding_sequences:
                assert op in bs.bound_operators
        for bs in self.binding_sequences:
            if bs.check_binding:
                bs.match_operators(self.operators, min_bind_score)
            for op in bs.bound_operators:
                assert bs in op.binding_sequences
    
    def reset_regulatory_network(self, min_bind_score):
        '''
        Reset the binding state of the regulatory network.
        
        Iterate over all Sequences in the genome and clear all bindings. 
        Then re-initialize the regulatory network.
        
        Parameters
        ----------
        min_bind_score : float
            minimum binding score for sequence matching
        '''
        for bs in self.binding_sequences:
            bs.clear_bound_operators()
        for op in self.operators:
            op.clear_binding_sequences()
        self.init_regulatory_network(min_bind_score)
    
    def init_regulatory_network(self, min_bind_score): 
        '''
        Initialize the binding state of the regulatory network.
        
        Iterate over all class:`virtual_cell.Sequence.Operator`s in the genome
        and match them against all
        class:`virtual_cell.Sequence.BindingSequence`s.
        
        Parameters
        ----------
        min_bind_score : float
            minimum binding score for sequence matching
        '''
        for op in self.operators:
            op.update_binding_sequences(self.binding_sequences, min_bind_score)
        for bs in self.binding_sequences:
            bs.check_binding = False #because all TFs have been updated simultaneously 
            
    def tf_connections_dict(self):
        """
        A dictionry of TFs to sets of downstream bound genes.
        """
        d = collections.defaultdict(set) # NOTE: unordered ok, use for output only
        op_to_tfs_scores_dict = self.op_to_tfs_scores_dict()
        for g in self:
            for tf,_score in op_to_tfs_scores_dict[g.operator]:
                d[tf].add(g)
        return d
        
    def _inform_lost_bs(self, binding_sequence):
        '''When a binding sequence is lost (due to deletion) it informs operators it was bound to.
        
        A single binding sequence that was removed may or not be present in
        another gene (copy) in the genome. Only if it was the last of its type,
        should the operators that it was binding to be informed about its
        removal. These operators remove the binding_sequence from their internal
        bound binding_sequence dictionaries.
        
        Parameters
        ----------
        binding_sequence : class:`virtual_cell.Sequence.BindingSequence`
            binding_sequence to check
        
        See Also
        --------
        func:`_inform_lost_operator`
        '''
        if binding_sequence not in self.binding_sequences:
            binding_sequence.inform_operators()
            
    def _inform_lost_operator(self, operator):
        '''
        If an operator is lost from the genome inform its binding sequences.
        
        Tells class:`virtual_cell.Sequence.BindingSequence`s of the `operator` to 
        remove `operator`.
        
        Parameters
        ----------
        operator : class:`virtual_cell.Sequence.Operator`
            operator to check
        
        See Also
        --------
        func:`_inform_lost_bs`
        '''
        if operator not in self.operators:
            operator.inform_bss()
            
    def update_genome_removed_gene(self, gene): 
        '''
        Remove a gene from the genome if no more copies exist in the genome. 
        
        Updates the genome 
        
        Parameters
        ----------
        gene : class:`virtual_cell.GenomicElement.GenomicElement`
            gene to be removed
        '''

        if gene['type'] == 'tf':
            self._inform_lost_bs(gene.binding_sequence)
        if gene not in set(self):
            self.genes_removed.add(gene)
        self._inform_lost_operator(gene.operator)
        
    def update_genome_removed_genes(self,genes):
        '''
        Update the genome to reflect gene deletions. 
       
        After the deletion of (part of) a chromosome, the genome has to be
        updated to reflect the change. Because exact copies of deleted genes may
        still be present in another part of the genome a check has to be
        performed before definitive removal.
        
        Parameters
        ----------
        genes : iterable of class:`virtual_cell.GenomicElement.GenomicElement`
            genes that were targeted by a deletion operation.
        '''
        for g in set(genes): # NOTE: unordered ok
            self.update_genome_removed_gene(g)
    
    def die(self, time):
        '''
        Record death of phylogenetic units in the genome.
        
        Typically called from the cell when it dies. All phylogenetic units in
        the genome are instructed to record their death. When phylogenetic units
        are no longer alive, they may be pruned from their respective
        phylogenetic trees if there are no more living descendants of the
        phylogenetic unit.
        
        Parameters
        ----------
        time : float
            simulation time
        '''
        for g in self:
            g.die(time)
        for chrom in self.chromosomes:
            chrom.die(time)
        for g in self.genes_removed:
            g.die(time)
        for c in self.chromosomes_removed:
            c.die(time)
        #clear the sequences bindings to decrease references to (dead) sequences
        #=======================================================================
        # for op in self.operators:
        #     op.clear_binding_sequences()
        # for bs in self.binding_sequences:
        #     bs.clear_bound_operators()
        #=======================================================================
            
    def prune_genomic_ancestries(self):
        '''
        Prune the phylogenetic trees of phylogenetic units in the genome.
        
        Returns
        -------
        tuple (set of class:`virtual_cell.Chromosome.Chromosome` , 
        set of class:`virtual_cell.GenomicElement.GenomicElement`)
        '''
        pruned_genes = self._prune_gene_ancestries()
        pruned_chromosomes = self._prune_chromosome_ancestries()
        return pruned_chromosomes, pruned_genes
    
    def _prune_gene_ancestries(self):
        pruned_genes = set()
        for g in set(self) | self.genes_removed:
            pruned_genes.update(g.prune_dead_branch())
        return pruned_genes
    
    def _prune_chromosome_ancestries(self):
        pruned_chromosomes = set()
        for chrom in set(self.chromosomes) | self.chromosomes_removed :
            pruned_chromosomes.update(chrom.prune_dead_branch())
        return pruned_chromosomes
    
    def _reproduction_copy_operators(self, operators, time):
        '''
        Make copy of operators present in the genome during reproduction.
        
        Copies each operator and stores the originals and copies in a map. This
        map is used as a reference when genes are copied and the new gene copy's 
        reference to its operator is updated to the newly created operator copy.
        
        Parameters
        ----------
        operators : iterable of class:`virtual_cell.Sequence.Operators` 
            parent operators
        time : float
            simulation time point
        
        Returns
        -------
        mapping of parent to child operators     
        '''
        self.orig_copy_operator_map = dict() # NOTE: unordered ok
        for op in operators:
            copy = op._reproduction_copy(time)
            self.orig_copy_operator_map[op] = copy
        return self.orig_copy_operator_map
    
    def _reproduction_copy_binding_sequences(self, binding_sequences, time):
        '''
        Make copy of binding sequences present in the genome during reproduction.
        
        Copies each operator and stores the originals and copies in a map. This
        map is used as a reference when genes are copied and the new gene copy's 
        reference to its binding sequence is updated to the newly created operator copy.
        
        Parameters
        ----------
        binding_sequences : iterable of class:`virtual_cell.Sequence.BindingSequence`
            parent binding sequences
        time : float
             simulation time point
        
        Returns
        -------
        mapping of parent to child binding sequences
        '''
        self.orig_copy_binding_sequence_map = dict() # NOTE: unordered ok
        for bs in binding_sequences:
            copy = bs._reproduction_copy(time)
            self.orig_copy_binding_sequence_map[bs] = copy
        return self.orig_copy_binding_sequence_map
    
    def _update_bind_mapping(self):
        '''
        Update bindings from parent to child sequences.
        '''
        for bs in self.binding_sequences:
            bs._update_bound_operators(self.orig_copy_operator_map)
        for op in self.operators:
            op._update_binding_sequences(self.orig_copy_binding_sequence_map)
       
    def _reproduction_copy_genes(self, parent_genome, time):
        '''
        Make copy of the parent_genome.
        
        Copies each gene and stores the originals and copies in a map. This map
        is used as a reference when chromosomes are copied and the new
        chromosome copy's references to genes in the parent_genome is updated
        to the newly created gene copies.
        
        Parameters
        ----------
        parent_genome : class:`Genome` 
            genome of parent
        time : float 
            simulation time point
        
        Returns
        -------
        mapping from parent genes to gene copies belonging to this offspring 
        '''
        self.orig_copy_genes_map = dict()  # NOTE: unordered ok
        
        for g in parent_genome:
            copy = g._reproduction_copy(time)
            copy.operator = self.orig_copy_operator_map[g.operator]
            if copy['type'] == 'tf':
                copy.binding_sequence = self.orig_copy_binding_sequence_map[g.binding_sequence]
            self.orig_copy_genes_map[g] = copy
        return self.orig_copy_genes_map

    def _reproduction_copy_chromosomes(self,chromosomes, time):
        for chrom in chromosomes:
            self.chromosomes.append(chrom._reproduction_copy(self.orig_copy_genes_map, time))
       
    def _reproduction_copy(self, time):
        '''
        '''
        cls = self.__class__
        result = cls.__new__(cls)
        for k, v in self.__dict__.items():
            if k in [ "enzymes", "pumps", "tfs", "binding_sequences", "operators", 'orig_copy_genes_map',
                     'orig_copy_operator_map', 'orig_copy_binding_sequence_map'] :
                pass
            elif k in  ["genes_per_type", "chromosomes", 
                         'genes_removed', 'chromosomes_removed',
                         'removed_bss', 'removed_operators']:
                atr_cls = v.__class__
                setattr(result, k, atr_cls.__new__(atr_cls))
            elif k in ['version']:
                setattr(result, k , v)
            else:    
                print "deepcopying", k , "of genome"
                setattr(result, k, deepcopy(v))
        result._reproduction_copy_operators(self.operators, time)
        result._reproduction_copy_binding_sequences(self.binding_sequences, time)
        result._reproduction_copy_genes(self, time)
        result._reproduction_copy_chromosomes(self.chromosomes, time)
        result._update_bind_mapping()
        return result

    def toJSON(self, *args, **kwargs):
        children = []
        
        for i,c in enumerate(self.chromosomes):
            children.append(c.toJSON(i, *args, **kwargs))
        
        d = {'name': 'genome',
             'description':'genome',
             'colour': mpl.colors.rgb2hex(mpl.colors.colorConverter.to_rgb('grey')),
             'children': children}
        return d
    
    def __str__(self):
        return '\n'.join([ str(chrom) for chrom in self.chromosomes])
    
    def __len__(self):
        return sum(map(len, self.chromosomes))
    
    def __iter__(self):
        """
        Iterate over all positions in all chromosomes.
        
        Yields
        ------
        :class:`virtual_cell.GenomicElement.GenomicElement`
            Genomic elements in the order of the chromosomes in the genome and positions in chromosomes.  
        """
        return itertools.chain(*self.chromosomes)
    
    def update(self, state):
        version = float(state.get('version', '0.0'))
        if version < 1.0:
            for attr in ['genes_per_type', 'operators', 'binding_sequences', 'removed_bss', 'removed_operators']:
                del state[attr]
            
    def upgrade(self):        
        version = float(self.version)
        self.version = self.class_version
        print 'upgrade class', self.__class__.__name__,
        print 'from version', version, 'to version', self.version
        if version < 1.0:
            self.genes_removed = set()
            self.chromosomes_removed = set()
            
    
    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = state
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()
        

