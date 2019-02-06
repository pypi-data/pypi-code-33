'''
Created on Feb 18, 2016

@author: thocu
'''
import math

def prune_GRN(grn, log_dif_effect=0.5, rescue_regulated=True, iterative=True):
    changed = True
    loop_count = 0
    while iterative and changed:
        changed = False
        grn_copy = grn.copy()
        for node, dat in grn.nodes_iter(data=True):
            if dat['type'] != 'tf':
                continue 
            tf = dat['gene_ref']
            if abs( math.log( tf['eff_bound']/tf['eff_apo'] ,2)  ) < log_dif_effect:
                if rescue_regulated and len(grn.predecessors(node)):
                    continue
                grn_copy.remove_node(node)
                changed = True
        grn = grn_copy
        loop_count += 1
    return grn