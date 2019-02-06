'''
Created on Feb 9, 2016

@author: thocu
'''
from VirtualMicrobes.virtual_cell import PhyloUnit
from collections import OrderedDict
import numpy as np

class PhyloGeneticAnalysis(object):
    '''
    Analyze biological networks
    '''

    
    def __init__(self):
        '''
        
        '''
        pass
        

def find_homologs(gene, genome):
    """
    For a gene, find all its homologs in a given genome.
    
    This is a naive approach that uses a combination of the gene's type and its
    :class:`virtual_cell.Identifier.Identifier` attribute to detect common
    descent.
    
    Parameters
    ----------
    gene : :class:`virtual_cell.GenomicElement.GenomicElement`
        Reference gene for homology search.
    genome : :class:`virtual_cell.Genome.Genome`
        Genome in which to search for homologs.
        
    Returns
    -------
    set
        The set of homologs of `gene` in the `genome`.
    """
    homologous = set()
    for g in genome:
        if (type(g) == type(gene) and gene.id.is_copy(g.id)):
            homologous.add(g)
    return homologous
        
def find_homolog_distances(gene, genome, closest_homolog=False):
    """
    Find homologs and their distance for a gene in a target genome.
    
    Parameters
    ----------
    gene : :class:`virtual_cell.GenomicElement.GenomicElement`
        Reference gene for homology search.
    genome : :class:`virtual_cell.Genome.Genome`
        Genome in which to search for homologs.
    closest_homolog : bool
        Flag to filter found homologs to those that have the shortest
        phylogenetic distance to the `gene`.
    """
    age = gene.time_birth
    #print 'gene age', age
    homolog_distance_dict = dict()
    for h in find_homologs(gene, genome):
        dist = 0
        h_age = h.time_birth
        if h is gene:
            dist = 0
            homolog_distance_dict[h] = dist
        elif gene.parent_of(h):
            dist = age - h_age
            homolog_distance_dict[h] = dist
            #print 'found parent', h, 'at distance', dist
        elif gene.child_of(h):
            dist = h_age - age
            homolog_distance_dict[h] = dist
            #print 'found child', h, 'at distance', dist
        else: 
            common_ancestors = gene.common_ancestors(h)
            ca_dists = []
            for ca in common_ancestors:
                ca_dists.append(age + h_age - 2 * ca.time_birth)
            if len(ca_dists):
                homolog_distance_dict[h] = min(ca_dists)
    if closest_homolog and len(homolog_distance_dict):
        min_dist = min(homolog_distance_dict.values())
        homolog_distance_dict = { k:v for k,v in homolog_distance_dict.items() 
                                 if v == min_dist }
    return homolog_distance_dict
     
def calculate_overlap(tf_connections, connections_of_homologous_tfs, 
                      closest_bound_homologs_dict):   
    """
    Calculate the overlap in bound genes between tf homologs.
    
    Parameters
    ----------
    tf_connections : list of :class:`virtual_cell.Gene.Gene`
        Downstream connections of the reference TF
    connections_of_homologous_tfs : list of sets of :class:`virtual_cell.Gene.Gene`s
        List of sets of downstream genes for each homolog of the reference TF  
    closest_bound_homologs_dict : dict of sets of :class:`virtual_cell.Gene.Gene`s
        Mapping of each original downstream gene of the reference TF to sets of
        homologs of these downstream genes.
        
    Returns
    -------
    float,float
        Tuple of fractions: 
        [0]: Fraction of downstream genes who's homologs are bound by a homolog of
        the reference TF.
        [1]: Fraction of new connections (averaged over tf homologs) per original 
        connection of the reference TF.  
    """
    connections_still_bound = 0
    nr_homologous_tfs = len(connections_of_homologous_tfs)
    all_closest_homolog_of_bound_genes = set()
    all_connections_of_homologous_tfs = set()
    for bound_gene in tf_connections:
        closest_homologs_of_bound_gene = set(closest_bound_homologs_dict[bound_gene])
        all_closest_homolog_of_bound_genes |= closest_homologs_of_bound_gene
        still_bound = False
        for connections in connections_of_homologous_tfs:
            overlap = connections & closest_homologs_of_bound_gene
            all_connections_of_homologous_tfs |= connections
            if len(overlap) > 0: # the homolog of the tf binds a homolog of the bound gene
                still_bound = True
        if still_bound:
            connections_still_bound += 1
    all_new = all_connections_of_homologous_tfs - all_closest_homolog_of_bound_genes
    fraction_conserved = np.NaN 
    if len(tf_connections):
        fraction_conserved = connections_still_bound / float(len(tf_connections))
    
    fraction_new = np.NaN 
    if len(tf_connections) and nr_homologous_tfs:
        avrg_new_connections = len(all_new) / float(nr_homologous_tfs)
        fraction_new = avrg_new_connections / float(len(tf_connections))
    return fraction_conserved , fraction_new
     
def tf_binding_overlap(cell1, cell2, closest_homolog=False, no_phylogeny=False, verbose=False):
    """
    Measure the overlap in target genes for tf homologs in phylogenetically
    related individuals.
    
    cell1 : :class:`virtual_cell.Cell.Cell`
        Reference individual for which to find homologs
    cell2 : :class:`virtual_cell.Cell.Cell`
        Homologs of TFs and downstream targets will be detected in this individual. 
    closest_homolog : bool
        Flag to filter found homologs to those that have the shortest
        phylogenetic distance to the `gene`.
    verbose : bool
        Print messages about homologs found.
        
    Returns
    -------
    dict
        Mapping from :class:`virtual_cell.Gene.TranscriptionFactor` to (maximum)
        binding overlap score.
    """
    overlap_dict, new_dict = OrderedDict(), OrderedDict()
    cell1_tf_connections = cell1.genome.tf_connections_dict()
    cell2_tf_connections = cell2.genome.tf_connections_dict()
    if verbose:
        print 'cell1', cell1.time_birth, '-> cell2', cell2.time_birth
    for tf in set(cell1.genome.tfs):
        bound_genes = cell1_tf_connections[tf]
        if isinstance(tf,PhyloUnit.PhyloUnit) and not no_phylogeny:
            #print 'using detailed phylogenetic distance information'
            closest_tf_homologs = find_homolog_distances(tf, cell2.genome, closest_homolog)
            closest_bound_homolog_dict = dict()
            for bg in bound_genes:
                closest_bound_homolog_dict[bg] = find_homolog_distances(bg, cell2.genome, closest_homolog)
        else:
            #print 'No phylogeny stored for object. Using simple homology by identifier information.'
            closest_tf_homologs = find_homologs(tf, cell2.genome) 
            closest_bound_homolog_dict = dict()
            for bg in bound_genes:
                closest_bound_homolog_dict[bg] = find_homologs(bg, cell2.genome)
        
        if verbose:
            print '\tfound', sum( [len(homologs) for homologs in closest_bound_homolog_dict.values() ]),
            print 'homologs for', len(bound_genes), 'downstream genes bound now'
        
        overlap_dict[tf], new_dict[tf] = calculate_overlap(bound_genes, 
                                             [ cell2_tf_connections[h_tf] 
                                              for h_tf in closest_tf_homologs ], 
                                             closest_bound_homolog_dict)
        if verbose:
            print
    return overlap_dict, new_dict