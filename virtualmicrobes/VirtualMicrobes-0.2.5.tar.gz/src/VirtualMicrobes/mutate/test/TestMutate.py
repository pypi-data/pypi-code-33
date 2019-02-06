'''
Created on Nov 15, 2013

@author: thocu
'''
#from nose.tools import *
#import unittest
import VirtualMicrobes.simulation.Simulation as simu
import VirtualMicrobes.my_tools.utility as util
from VirtualMicrobes.virtual_cell.Cell import Cell
from VirtualMicrobes.environment.Environment import Environment
import random

class Test():
    
    @classmethod
    def setup_class(self):
        self.rand_gen = random.Random(24)
        param_updates = dict()
        param_updates['grid_cols'] = 1
        param_updates['grid_rows'] = 1
        param_updates['nr_cat_reactions'] = 10
        param_updates['nr_ana_reactions'] = 10
        param_updates['chromosome_compositions'] = [ util.GeneTypeNumbers(tf=10, enz=10, pump=10) for _ in range(2) ]
        self.params = simu.update_default_params(**param_updates)
        self.environment = Environment(self.params)
        self.environment.print_values()
        self.cell = Cell(params=self.params, 
                         environment=self.environment,
                         rand_gen=self.rand_gen)

    def test_chrom_dup(self):
        '''
        Tests: 
        * duplicating chromosome increases chromosome count.
        * rewinding mutation yields the original set of chromosomes
        * after rewinding nr of chromosomes equals pre mutation count
        '''
        predup_chroms = self.cell.genome.chromosomes[:]
        predup_len = len(predup_chroms)
        chosen = self.rand_gen.choice(self.cell.genome.chromosomes)
        dup = self.cell.duplicate_chromosome(chrom=chosen, time=0 )
        assert len(self.cell.genome.chromosomes) == predup_len + 1
        dup.rewind()
        predup_set = set(predup_chroms)
        post_rewind_set = set(self.cell.genome.chromosomes)    
        assert predup_set == post_rewind_set
        assert len(post_rewind_set) == predup_len

    def test_chrom_del(self):
        '''
        Tests: 
        * deleting chromosome decreases chromosome count.
        * rewinding mutation yields the original set of chromosomes
        * after rewinding nr of chromosomes equals pre mutation count
        '''
        predel_chroms = self.cell.genome.chromosomes[:]
        chosen = self.rand_gen.choice(self.cell.genome.chromosomes)
        del_ = self.cell.delete_chromosome(chrom=chosen, time=0)
        assert len(self.cell.genome.chromosomes) == len(predel_chroms) - 1
        del_.rewind()
        assert set(predel_chroms) == set(self.cell.genome.chromosomes)
        assert len(self.cell.genome.chromosomes) == len(predel_chroms)

    def test_chrom_fiss(self):
        '''
        Tests: 
        * fission of chromosome decreases chromosome count.
        * number of genes remains constant
        * rewinding mutation yields the original set of chromosomes
        * after rewinding, the number of chromosomes equals pre mutation count
        '''
        prefiss_chroms = self.cell.genome.chromosomes[:]
        chosen = self.rand_gen.choice(self.cell.genome.chromosomes)
        pos = len(chosen)/2
        fission = self.cell.fiss_chromosome(chrom=chosen, pos=pos, time=0)
        assert len(self.cell.genome.chromosomes) == len(prefiss_chroms) + 1
        assert sum(map(len, prefiss_chroms)) == len(self.cell.genome) 
        fission.rewind()
        assert set(prefiss_chroms) == set(self.cell.genome.chromosomes)
        assert len(self.cell.genome.chromosomes) == len(prefiss_chroms)
        
    def test_chrom_fuse(self):
        '''
        Tests: 
        * fusing chromosomes increases chromosome count.
        * number of genes remains constant
        * rewinding mutation yields the original set of chromosomes
        * after rewinding, the number of chromosomes equals pre mutation count
        '''
        prefus_chroms = self.cell.genome.chromosomes[:]
        chosen1, chosen2 = self.rand_gen.sample(self.cell.genome.chromosomes,2)
        end1, end2 = [ self.rand_gen.choice([True, False]) for _ in range(2) ]
        fusion = self.cell.fuse_chromosomes(chrom1=chosen1, chrom2=chosen2, 
                                   end1=end1, end2=end2, time=0)
        
        assert len(self.cell.genome.chromosomes) == len(prefus_chroms) - 1 
        assert sum(map(len, prefus_chroms)) == len(self.cell.genome) 
        fusion.rewind()
        
        assert set(self.cell.genome.chromosomes) == set(prefus_chroms)
        assert len(self.cell.genome.chromosomes) == len(prefus_chroms)
        
    def test_point_mutations(self): # TODO: test that the mutated parameter is different for pre and post mutation gene
        '''
        Tests:
        * A new, mutated gene is created and stored
        * After mutating all genes in genome, no gene is the same
        * after rewinding all point mutations, all genes are equal to those in the pre mutation genome
        '''
        pre_point_chroms = [ chrom.positions[:] for chrom in self.cell.genome.chromosomes ]
        point_muts = []
        for chrom in self.cell.genome.chromosomes:
            for pos in range(len(chrom)):
                point_mut = self.cell.point_mutate_gene(chrom=chrom, pos=pos, 
                                                        mut_dict=self.params.point_mutation_dict, 
                                                        point_mut_ratios=self.params.point_mutation_ratios, 
                                                        environment=self.environment, 
                                                        time=0, rand_gen=self.rand_gen)
                assert point_mut.genomic_target != point_mut.post_mutation
                point_muts.append(point_mut)
        for pre, post in zip(pre_point_chroms, self.cell.genome.chromosomes):
            for g_pre, g_post in zip(pre,post):
                assert g_pre != g_post
        for pm in reversed(point_muts):
            pm.rewind()
        for pre, post in zip(pre_point_chroms, self.cell.genome.chromosomes):
            for g_pre, g_post in zip(pre,post):
                assert g_pre == g_post
                
    def test_parameter_mutations(self):
        '''
        Tests:
        * For every gene in the genome all parameters are mutated.
        * Mutated gene parameters are different from original values.
        * No mutations are no-op.
        '''
        for chrom in self.cell.genome.chromosomes:
            for pos,gene in enumerate(chrom):
                type_ = gene['type']
                mut_dict = self.params.point_mutation_dict[type_]
                for par, mut_modifier in mut_dict.items():
                    cur_val = None
                    if par == 'bind':
                        cur_val = gene.binding_sequence.sequence
                    elif par == 'operator':
                        cur_val = gene.operator.sequence
                    elif par == 'promoter':
                        cur_val = gene.promoter.strength
                    elif par == 'ligand_class':
                        cur_val = gene.ligand_class
                    else:
                        cur_val = gene[par] 
                    point_mut = self.cell.point_mutate_gene_param(chrom, pos, par, mut_modifier, 
                                                      self.environment, time=0, rand_gen=self.rand_gen)
                    mutated_gene = chrom.positions[pos]
                    new_val = None
                    if par == 'bind':
                        new_val = mutated_gene.binding_sequence.sequence
                    elif par == 'operator':
                        new_val = mutated_gene.operator.sequence
                    elif par == 'promoter':
                        new_val = mutated_gene.promoter.strength
                    elif par == 'ligand_class':
                        new_val = mutated_gene.ligand_class
                    else:
                        new_val = mutated_gene[par] 
                    assert cur_val != new_val
