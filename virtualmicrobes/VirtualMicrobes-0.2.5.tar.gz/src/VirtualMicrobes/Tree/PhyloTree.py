'''
Created on Nov 11, 2014

@author: thocu
'''
from VirtualMicrobes.my_tools.utility import OrderedDefaultdict
from sortedcontainers.sorteddict import SortedDict
from ete3 import TreeNode #TODO: try upgrade to ete3.3 (fork git repo to allow merging in updates to local copy)
import VirtualMicrobes.my_tools.utility as util
import warnings
from collections import OrderedDict, deque
import itertools
#import warnings

def nh_branch(_id, branch_length, features=None):
    nhx_tag = ''
    if features is not None:
        nhx_tag = '[&&NHX:' +   ':'.join( [ '='.join( (n,str(v)) ) for (n,v) in features ]) + ']'
    branch_length_tag = ':' + str(branch_length) if branch_length is not None else ''
    return _id + branch_length_tag + nhx_tag

def newick(_id, time, branch_length):
    branch_length_tag = ":" + str(branch_length) if branch_length else ''
    return  str(_id)+'_' + str(time) + branch_length_tag

def nhx(_id, time, branch_length):
    nhx_tag = '[&&NHX:' + 'ID=' + str(id) + ':TIME=' + str(time) + ']'
    return  newick(_id, time, branch_length) + nhx_tag

class PhyloNode(object):

    """
     
    :version:
    :author:
    """

    """ ATTRIBUTES

    parent  (private)
     this holds the actual object
    children  (private)
    the_object  (private)
    """
    max_node_depth=0
    id = 0
    
    def __init__(self, val, time):
        self.val = val
        if time > PhyloNode.max_node_depth:
            PhyloNode.max_node_depth = time
        self.time = time
        self.offspring_nodes = []
        self.ancestor_nodes = []
        self.internal_child_node = None
        self.internal_parent_node = None
        PhyloNode.id += 1
        self.id = PhyloNode.id
        self.is_root = False
        self.root = None
 
    def add_root(self, root_node):
        self.root = root_node
        root_node.internal_child_node = self
        
    def excise(self):
        '''
        remove references to this node from other tree nodes 
        and reconnect remaining nodes.
        '''
        #print 'excising', self
        if self.internal_parent_node and self.internal_child_node: #crosconnect child with parent
            self.internal_child_node._connect_internal_parent(self.internal_parent_node)
        elif self.internal_parent_node: # internal parent should no longer reference self
            self.internal_parent_node._remove_internal_child()
        elif self.internal_child_node: #child inherits the ancestors of self and ancestors 
            # replace references to self with child
            self.internal_child_node._inherit_ancestors_from(self)
            if self.has_root(): #child inherits reference to root
                self.internal_child_node.inherit_root(self)
            self.internal_child_node._remove_internal_parent()
        else: # remove all references to self at the ancestors
            for anc in self.ancestor_nodes:
                anc.offspring_nodes.remove(self)
        self.internal_parent_node = None
        self.internal_child_node = None

    def push_onto_internal_child(self, child):  # takes PhyloNode objects 
        '''
        makes this node an internal parent node of child
        :param child:
        '''
        if self is child:
            raise Exception('trying to make {} a child of itself'.format(child))
        self._inherit_ancestors_from(child)
        #self.internal_child_node = child #NOTE should be redundant with line below 
        child._connect_internal_parent(self)
        if child.has_root():
            child.push_up_root()
        
    def _connect_internal_parent(self, parent):  # takes PhyloNode objects 
        self.internal_parent_node = parent
        parent.internal_child_node = self
    
    def _disconnect_internal_child(self):
        self.internal_child_node._remove_internal_parent()
        self.internal_child_node = None
        
    def _remove_internal_child(self):
        self.internal_child_node = None
    
    def _remove_internal_parent(self):
        self.internal_parent_node = None
    
    def connect_phylo_offspring(self, offspring):  # takes PhyloNode objects 
        self._add_phylo_offspring(offspring)
        offspring._add_phylo_ancestor(self)
        
    def _add_phylo_offspring(self, offspring):
        self.offspring_nodes.append(offspring)
    
    def _add_phylo_ancestor(self, ancestor):  # takes PhyloNode objects 
        self.ancestor_nodes.append(ancestor)
        
    def _inherit_ancestors_from(self, node):   
        for anc in node.ancestor_nodes[:]:
            anc.offspring_nodes.remove(node)
            anc.connect_phylo_offspring(self)
            node.ancestor_nodes.remove(anc)
    
    @property        
    def children(self):
        internal = [self.internal_child_node] if self.internal_child_node else []
        return internal + self.offspring_nodes
    
    @property
    def parents(self):
        internal = [self.internal_parent_node] if self.internal_parent_node else []
        return internal + self.ancestor_nodes
    
    def push_up_root(self):
        '''
        Iteratively push up the root to the internal_parent_node.
        '''
        if self.internal_parent_node:
            self.internal_parent_node.inherit_root(self)
            self.internal_parent_node.push_up_root()
    
    def inherit_root(self, node):
        self.root = node.root
        node.root = None
        self.root.internal_child_node = self
    
    def has_root(self):
        return True if self.root else False
    
    def _remove_root(self):
        self.root = None
    
    def remove_root_stem(self):
        if not self.is_root:
            raise Exception('Trying to remove root stem of non-root node', str(self))
        if self.internal_child_node != None:
            self.internal_child_node._remove_root()
            self.is_root = False
    
    @property
    def is_leaf(self):
        """
         is this a leaf of the tree
        """
        return False if self.internal_child_node or self.offspring_nodes else True
    
    def dist_to_parent(self, parent):
        dist = None
        if parent in self.parents:
            dist = self.time - parent.time
        elif self.root and parent is None:
            dist = self.time - self.root.time
        return dist
    
    def nh_format_nr(self, _format='newick', formatter=nh_branch):
        '''
        Format a newick string non-recursively.
        :param with_leafs:
        :param _format:
        :param formatter:
        '''
        newick = []
        for postorder, parent, node in self.iter_prepostorder():
            #print newick
            features = node.nhx_features if _format == 'NHX' else None
            if postorder:
                newick.append(")")
                newick.append(formatter(node.newick_id, node.dist_to_parent(parent), features)) 
            else:
                if node is not self and node != parent.children[0]:
                    newick.append(",")
                if node.is_leaf:
                    newick.append(formatter(node.newick_id, node.dist_to_parent(parent), features))
                else:
                    newick.append("(")
        newick.append(";")
        return ''.join(newick)
                
    @property
    def newick_id(self):
        '''
        id tag used in new hampshire (newick) tree format
        '''
        return str(self.val.id) + '_' + str(self.time)
    
    @property
    def nhx_features(self):
        '''
        additional node features used in the 'extended' newick format (nhx)
        '''
        return [('ID', str(self.val.id)), ('TIME', self.time)] 
    
    def iter_prepostorder(self, is_leaf_fn=None):
        """
        Iterate over all nodes in a tree yielding every node in both
        pre and post order. Each iteration returns a postorder flag
        (True if node is being visited in postorder) and a node
        instance.
        """
        to_visit = [(None,self)]

        while to_visit:
            node = to_visit.pop(-1)
            try:
                _ , parent, node = node
            #if isinstance()
            except ValueError:
                # PREORDER ACTIONS
                parent, node = node
                yield (False, parent, node)
                if not node.is_leaf:
                    # ADD CHILDREN
                    to_visit.extend(reversed( [ (node, c ) for c in node.children ] + [[1, parent, node]] ) )
            else:
                #POSTORDER ACTIONS
                yield (True, parent, node)
                
    def _iter_descendants_levelorder(self, is_leaf_fn=None):
        """ 
        Iterate over all desdecendant nodes. 
        """
        tovisit = deque([self])
        while len(tovisit)>0:
            node = tovisit.popleft()
            yield node
            if not is_leaf_fn or not is_leaf_fn(node):
                tovisit.extend(node.children )
    
    def __str__(self):
        internal_child_id = self.internal_child_node.id if self.internal_child_node else ''
        internal_parent_id = self.internal_parent_node.id if self.internal_parent_node else ''
        return ('TN'+str(self.id)+'{int_child_TN:'+str(internal_child_id)+
                ", int_parent_TN:"+str(internal_parent_id)+
                " external_offspring_TN:[" + ",".join([str(c.id) for c in self.offspring_nodes])+
                "], external_ancestor_TN:[" + ",".join([str(c.id) for c in self.ancestor_nodes]) + "]" +
                ", id:"+str(self.val.id)+", t:"+str(self.time)+('root:'+str(self.root.id) if self.root else '')+'}' )

class PhyloTree(object):

    """
    Primary use is a phylogenetic tree, representing reproduction/speciation
    events at particular points in time. Because generations are overlapping, a
    parent may have offspring at various time points. Therefore Nodes are not
    strictly parents, but rather, parent-reproduction-time tuples.
    """
    class_version = '1.0'
    
    class SuperNode(object):
        def __init__(self):
            self.id = 'ROOT'
    
    def __init__(self, supertree=False):
        self.version = self.__class__.class_version
        self.max_depth = 0
        self.nodes_dict = OrderedDefaultdict(SortedDict) #using SortedDict the maintain time ordered TreeNodes
        self.leafs = set()
        self.max_leaf_depth=(0, None)
        self.roots = []
        #self.ete_tree = None
        self.ete_trees = OrderedDict()
        self.lca = None
        self.supertree = supertree
        
    def clear(self):
        self.nodes_dict = OrderedDefaultdict(SortedDict)
        self.leafs = set()
        self.max_leaf_depth=(0, None)
        self.roots = []     
                
    def create_root_stem(self, phylo_root):
        new_root = self.add_node(phylo_root, phylo_root.time_birth) 
        #print 'adding root', new_root
        if new_root is not None:
            self.connect_internal_node(new_root)
            self.roots.append(new_root)
            new_root.is_root = True
        if phylo_root.time_death is not None and not self.nodes_dict[phylo_root].has_key(phylo_root.time_death):
            self.create_leaf(phylo_root)
        
        return new_root
    
    def _connect_root(self, root_node):
        root_child = None
        if len(self.nodes_dict[root_node.val]) > 0: #internal node entries for phylo_unit exist in nodes_dict
            internal_phylo_time = self.nodes_dict[root_node.val].iloc[0]
            root_child = self.nodes_dict[root_node.val][internal_phylo_time]
        else:
            root_child = self.create_leaf(root_node.val)
        root_child.add_root(root_node)
    
    def _remove_root(self, root_node):
        root_node.remove_root_stem()
        #print 'removing root', root_node
        self.roots.remove(root_node)
                    
    def add_leaf(self, leaf):
        self.leafs.add(leaf)
        if leaf.time > self.max_leaf_depth[0]:
            self.max_leaf_depth = leaf.time, leaf
        
    def update(self, new_phylo_units=[], removed_phylo_units=[], new_roots=[]):
        
        for new_root in new_roots:
            new_root = self.create_root_stem(new_root)
        for phylo_unit in new_phylo_units:
            self.add_phylo_history(phylo_unit)
        for phylo_unit in removed_phylo_units:
            self.delete_phylo_hist(phylo_unit)
                
    def add_phylo_history(self, phylo_unit):
        new_leaf = self.create_leaf(phylo_unit)
        phylo_parent_nodes = self.create_stems(phylo_unit)
        for phylo_parent_node in phylo_parent_nodes:
            self.connect_phylo_parent_child(phylo_parent_node, new_leaf)
        return phylo_parent_nodes, new_leaf 
    
    def create_leaf(self, phylo_unit):
        time_death = phylo_unit.time_death
        new_leaf = None
        if not self.nodes_dict[phylo_unit].has_key(time_death):
            new_leaf = self.add_node(phylo_unit, time_death)
            self.add_leaf(new_leaf)
            self.connect_leaf(new_leaf)
        else:
            new_leaf = self.nodes_dict[phylo_unit][time_death]
            print 'WARNING: Node already in tree', new_leaf 
        return new_leaf

    def connect_leaf(self, leaf_node): # a cell death node
        connected = False
        (phylo_unit, time_death) = leaf_node.val, leaf_node.time
        if len(self.nodes_dict[phylo_unit]) > 1: #there are more internal nodes
            leaf_node_index = self.nodes_dict[phylo_unit].index(time_death)
            internal_parent_time = self.nodes_dict[phylo_unit].iloc[leaf_node_index - 1]
            internal_parent_node = self.nodes_dict[phylo_unit][internal_parent_time]
            internal_parent_node.push_onto_internal_child(leaf_node)
            connected = True
        return connected
        
    def create_stems(self, phylo_unit):
        time_birth = phylo_unit.time_birth
        phylo_parent_nodes = []
        new_internal_nodes = []
        for phylo_parent in phylo_unit.parents: # add parent nodes as needed
            if self.nodes_dict[phylo_parent].has_key(time_birth):
                phylo_parent_nodes.append(self.nodes_dict[phylo_parent][time_birth])
            else:
                new_internal_nodes.append(self.add_node(phylo_parent, time_birth))
        for int_node in new_internal_nodes:
            self.connect_internal_node(int_node)
            phylo_parent_nodes.append(int_node)
        return phylo_parent_nodes
    
    def connect_phylo_parent_child(self, phylo_parent_node, phylo_child_node):
        phylo_child_node_pos = self.nodes_dict[phylo_child_node.val].index(phylo_child_node.time)
        if phylo_child_node_pos == 0:
            phylo_parent_node.connect_phylo_offspring(phylo_child_node)
        else:
            first_phylo_time = self.nodes_dict[phylo_child_node.val].iloc[0]
            phylo_parent_node.connect_phylo_offspring(self.nodes_dict[phylo_child_node.val][first_phylo_time])

    def add_node(self, phylo_unit, time):
        if time is not None:
            self.max_depth = max(self.max_depth, time)
        else:
            time = self.max_depth
        new_node = PhyloNode(phylo_unit, time)
        if self.nodes_dict[new_node.val].has_key(new_node.time):
            new_node = self.nodes_dict[new_node.val][new_node.time]
            warnings.warn('reassigning existing node to tree:\n {}\n{}'.format(self.nodes_dict[new_node.val][new_node.time],
                                                                               new_node))
        self.nodes_dict[new_node.val][new_node.time] = new_node
        return new_node
        
    def reconnect_internal_nodes(self, internal_parent, internal_child):
        internal_child_orig = internal_parent.internal_child_node
        if internal_child_orig != None:
            internal_child.push_onto_internal_child(internal_child_orig)
        internal_parent.push_onto_internal_child(internal_child)
        
    def connect_internal_node(self, int_node):
        '''Connect internal node 'int_node' with nodes above and below it on its
        own branch (representing births and/or death in this phylogenetic unit's
        life history branch)
         
        :param int_node: newly made internal node that should get connected up
        and down in the tree.
        
        '''
        connected_up, connected_down = False, False
        (phylo_unit, time) = int_node.val, int_node.time
        new_node_index = self.nodes_dict[phylo_unit].index(time) # get its index in dict
        orig_dict_entries = len(self.nodes_dict[phylo_unit])
        if new_node_index > 0: # this indicates that other (earlier) internal nodes exist, and int_node has to be connected to them
            internal_parent_time = self.nodes_dict[phylo_unit].iloc[new_node_index - 1]
            internal_parent = self.nodes_dict[phylo_unit][internal_parent_time]
            self.reconnect_internal_nodes(internal_parent, int_node)
            connected_up = True
            if orig_dict_entries > (new_node_index+1): #there are also later nodes in the
                connected_down = True 
        elif orig_dict_entries > (new_node_index+1): # this indicates that it is the 'earliest' internal node; reconnect to internal children
            internal_child_time = self.nodes_dict[phylo_unit].iloc[new_node_index + 1]
            internal_child = self.nodes_dict[phylo_unit][internal_child_time]
            self.reconnect_internal_nodes(int_node, internal_child)
            connected_down = True
        return (connected_up, connected_down)
        
    def delete_phylo_hist(self, phylo_unit):
        '''
        Remove the branch representing the phylogenetic unit and disconnect it
        from all sub-branches (children) in the tree.
        
        :param phylo_unit:
        '''
        birth, death = phylo_unit.time_birth, phylo_unit.time_death
        if len(self.nodes_dict[phylo_unit]) == 0: # internal node entries for phylo_unit exist in nodes_dict (phylo_unit reproduced)
            raise Exception('could not find internal node for {}, {}, {}'.format(phylo_unit.id, birth, death))
        for node in  self.nodes_dict[phylo_unit].values():
            self.delete_node(node)
            
    def delete_node(self, tree_node):
        tree_node.excise()
        for phylo_parent in tree_node.ancestor_nodes:
            if len(phylo_parent.offspring_nodes) == 0 and not phylo_parent.has_root():
                phylo_parent.excise()
                del self.nodes_dict[phylo_parent.val][phylo_parent.time]
                if len(self.nodes_dict[phylo_parent.val]) == 0:
                    #pass
                    del self.nodes_dict[phylo_parent.val]
        for phylo_child in tree_node.offspring_nodes:
            phylo_child.ancestor_nodes.remove(tree_node)
        del self.nodes_dict[tree_node.val][tree_node.time]
        if len(self.nodes_dict[tree_node.val]) == 0:
            del self.nodes_dict[tree_node.val]
        try:
            self.leafs.remove(tree_node)
        except KeyError:
            pass
        if tree_node.is_root and tree_node.is_leaf:
            self._remove_root(tree_node)
                
    def delete_empty_phylo_stems(self):
        for phylo_unit, times_dict in self.nodes_dict.items():
            if len(times_dict) == 0:
                del self.nodes_dict[phylo_unit]
              
    def recalc_max_leaf_depth(self, leafs=None):
        if leafs is None:
            leafs = self.leafs
        max_leaf_depth, leaf_node = 0, None
        for leaf in self.leafs:
            if leaf.time > max_leaf_depth:
                max_leaf_depth, leaf_node = leaf.time, leaf
        self.max_leaf_depth = (max_leaf_depth, leaf_node)
    
    def find_lca(self):
        '''
        Find the last common ancestor in the tree.
        
        Start at the single root and go up until a branching point in the tree
        is found.
        
        Returns
        -------
        PhyloNode : LCA if it exists else None
        '''
        if len(self.roots) != 1:
            return None
        node = self.roots[0]
        while True:
            children = node.offspring_nodes
            if len(children) > 1:
                break
            elif len(children) == 1:
                if node.internal_child_node and not node.internal_child_node.is_leaf:
                    break
                else:
                    node = children[0]
            elif len(children) == 0:
                if not node.internal_child_node:
                    break
                else:
                    node = node.internal_child_node
        return node
    
    def coalescent(self):
        '''
        Find coalescent node and depth in the tree.
        
        Returns
        -------
        (class:`Tree.PhyloTree.PhyloNode`, time) : LCA, depth
        '''
        self.lca = self.find_lca()
        lca_depth = self.lca.time if self.lca is not None else 0
        max_depth, _leaf = self.max_leaf_depth
        return (self.lca, max_depth - lca_depth) 
                    
    def nh_formats(self, roots=None, supertree=None, _format='newick'):
        if supertree is None:
            supertree = self.supertree
        nh_trees = []
        if roots is None:
            roots = self.roots
        if supertree:
            supernodeval = self.SuperNode()
            supernode = PhyloNode(supernodeval, 0)
            for root in roots:
                supernode._add_phylo_offspring(root)
            return [supernode.nh_format_nr(_format=_format)]
        for root in roots:
            nh_trees.append(root.nh_format_nr( _format=_format)) 
        return nh_trees 
    
    def nodes_iter(self):
        for d in self.nodes_dict.values():
            for node in d.values():
                yield node
        
    
            
    '''
    Functions pertaining to ete3-tree representation. PhyloTree can be
    (approximately) converted to a representation of trees in the ete3 module.
    This is useful for drawing routines and various tree algorithms and
    functions.
    '''
    
    @property
    def ete_tree(self):
        '''
        Return the first 'ete tree' in the ete trees dict if it exists.
        
        This is an adapter function during the transition to working with the
        multiple ete tree dictionary. 
        '''
        try:
            return self.ete_trees.values()[0].tree
        except IndexError:
            return None

    @property
    def ete_named_node_dict(self):
        '''
        Return the ete_named_node_dict belonging to the first ete tree. 
        
        See Also
        --------
        func:`ete_tree` 
        '''
        try:
            return self.ete_trees.values()[0].named_node_dict
        except IndexError:
            return None
        
    @property
    def ete_node_name_to_phylo_node(self):
        '''
        Return the ete_node_name_to_phylo_node belonging to the first ete tree. 
        
        See Also
        --------
        func:`ete_tree` 
        '''
        try:
            return self.ete_trees.values()[0].node_name_to_phylo_node
        except IndexError:
            return None
    
    def to_ete_trees(self, with_leafs=False, supertree=None):
        '''
        Construct TreeNode representations for all roots in the PhyloTree. 
        
        ete3.TreeNode representations can be used for advanced plotting and tree
        analysis.
        
        Parameters
        ----------
        with_leafs : bool
            construct with or without terminal nodes
        supertree : bool
            use a supernode as an artificial root node (useful when simulation
            starts from independent lineages)
            
        Returns
        -------
        OrderedDict of name -> TreeNode : TreeNodes by name for all phylo roots
        '''
        print 'writing NHX format'
        nhxs = self.nh_formats(supertree=supertree,  _format='NHX')
        #print nhx
        print 'constructing ETE trees for roots:', 
        self.ete_trees = OrderedDict()
        for nhx in nhxs:
            tree = TreeNode(nhx, format=1)
            named_node_dict, node_name_to_phylo_node = self.ete_init_mappings(tree)
            tree_struct = util.ETEtreeStruct(tree=tree,
                                             named_node_dict=named_node_dict,
                                             node_name_to_phylo_node=node_name_to_phylo_node
                                             )
            if not with_leafs:
                self.ete_prune_leafs(tree_struct)
            self.ete_trees[tree.name] = tree_struct
            print tree.name, 
        print 'done'
        return self.ete_trees
            
    def ete_init_mappings(self, ete_tree):
        '''
        Construct helper dictionaries for converting TreeNode names to TreeNodes
        and TreeNode names to PhyloUnits.
        '''
        ete_named_node_dict = OrderedDict( (n.name, n) for n in  ete_tree.traverse())
        ete_node_name_to_phylo_node = OrderedDict([ (n.newick_id, n) for n in self.nodes_iter() ])
        return ete_named_node_dict, ete_node_name_to_phylo_node
        
    def ete_get_lca(self, ete_tree, nodes=None):
        '''
        Return last common ancestor (LCA) for a set of nodes. 
        
        (default: all
        leafs of the current tree)
        
        Parameters
        ----------
        ete_tree : TreeNode
            ete tree root node
        nodes : list of class:`ete3.TreeNode` 
            nodes in tree for which to find LCA
        
        Returns
        -------
        TreeNode : the last common ancestor
        '''
        if nodes is None:
            nodes = ete_tree.get_leaves()
        return ete_tree.get_common_ancestor(nodes) if len(nodes) else None
    
    def ete_calc_lca_depth(self, ete_tree):
        '''
        Calculate the distance from the last common ancestor to the farthest
        leaf in an ete tree.
        
        Parameters
        ----------
        ete_tree : TreeNode
            ete tree root node
            
        Returns
        -------
        int : depth of LCA
        '''
        lca = self.ete_get_lca(ete_tree)
        lca_depth = 0
        if lca is not None:
            _max_node, lca_depth = lca.get_farthest_leaf()
        return lca_depth
            
    def distances(self, ete_tree, nodes):
        """
        Pairwise distances between all nodes.
        
        
        Parameters
        ----------
        ete_tree : class:`ete3.TreeNode` 
            ete tree root node
        nodes : sequence of (phylo_node, ete_node) pairs
        
        Returns
        -------
        sequence of (phylo_node1, phylo_node2, tree_dist, top_dist)
            - tree_dist is phylogenetic distance.
            - top_dist is topological distance
        """
        pairwise_distances = []
        for (pn1, en1), (pn2, en2) in itertools.combinations(nodes, 2):
            t_dist = ete_tree.get_distance(en1, en2)
            top_dist = ete_tree.get_distance(en1, en2, topology_only=True)
            pairwise_distances.append( (pn1,pn2, t_dist, top_dist ))
        return pairwise_distances
              
    def ete_n_most_distant_phylo_units(self, ete_tree_struct, n=2, root=None):
        '''
        Convenience function to return phylo units after finding
        'ete_n_most_distant_leafs' (see below)
        
        
        :param root: phylo unit used as root
        '''
        
        if root is not None:
            root = self.ete_phylo_to_ete_birth_nodes(ete_tree_struct, root)[0]
        else:
            root = ete_tree_struct.tree
        return [ (ete_tree_struct.node_name_to_phylo_node[n.name].val, n) 
                for (n,_) in self.ete_n_most_distant_leafs(root, n) ]
        
    def ete_n_most_distant_leafs(self, ete_root, n):
        '''
        Find n leafs that are most diverged from eachother. 
        
        First, the oldest n subtrees are determined. Then, for all subtrees the
        farthest lying leaf is returned.
        
        :param n: number of leafs
        :param root: starting point for search (default is the ete_tree root)
        '''
        if n == 1:
            return [ (sorted(ete_root.get_leaves(), key=lambda n: n.name )[0],None ) ]
        return [ s.get_farthest_leaf() for s,_ in self.ete_n_oldest_subtrees(ete_root, n) ]
        
    def ete_n_oldest_subtrees(self, ete_root, n):
        '''
        Find n oldest subtrees under root. 
        
        Iteratively expands the oldest subtree root into its children until the
        desired number of subtrees is in the list. Return as a list of tuples of 
        (subtree, distance-from-root).
        
        Parameters
        ----------
        n : int
            number of subtrees 
        root : TreeNode
            start point for subtree search
            
        Returns
        -------
        subtrees : a list of (TreeNode, distance) 
        '''
        subtrees = [ (ete_root, 0) ]
        oldest_subtree = None
        while len(subtrees) < n:
            oldest_subtree, subtree_age = subtrees[0]
            if oldest_subtree.is_leaf(): # oldest subtree is a leaf, nothing left to expand 
                break
            subtrees.pop(0) # oldest is replaced by its children in the subtrees list
            for child in oldest_subtree.get_children():
                subtrees.append( (child, subtree_age + child.dist) ) 
            subtrees = sorted( subtrees, key=lambda x: x[1])
        return subtrees[:n] # because multifurcations exist, there may be more than n subtrees in the list
    
    def _node_ids_to_ete_nodes(self, ete_tree_struct, node_ids):
        '''
        Iterator that maps ete node ids to TreeNode objects using a precompiled map.
        
        Parameters
        ----------
        node_ids : list
            list of ete node ids
        
        Yields
        ------
        TreeNode : the mapped ete node
        '''
        for _id in node_ids:
            try:
                yield ete_tree_struct.named_node_dict[_id]
            except KeyError: # We want to catch this, because the ete_tree may have 
                # had been pruned  
                warnings.warn('Node id {} not found in the ete_named_node_dict. Perhaps the ete_tree was pruned.'.format(_id))
                pass
                
    def ete_phylo_to_ete_birth_nodes(self, ete_tree_struct, phylo_unit):
        '''
        Return iterator over birth nodes in the ete tree for a phylo unit.
        
        Parameters
        ----------
        phylo_unit: class:`virtual_cell.PhyloUnit.PhyloUnit`
            phylounit to map
        
        Returns
        -------
        iterator of class:`ete3.TreeNode`
        '''
        node_ids = []
        if phylo_unit.parents is not None:
            for parent in phylo_unit.parents:
                birth_node = self.nodes_dict[parent][phylo_unit.time_birth]
                node_ids.append(birth_node.newick_id)
        else:
            birth_node = self.nodes_dict[parent][phylo_unit.time_birth]
            node_ids.append(birth_node.newick_id)
        return list(self._node_ids_to_ete_nodes(ete_tree_struct, node_ids))
    
    def ete_phylo_to_ete_stem_nodes(self,ete_tree_struct, phylo_unit):
        '''
        Return iterator over stem nodes in the ete tree for a phylo unit.
        
        The stem nodes represent replication and death of the phylounit.
        
        Parameters
        ----------
        phylo_unit: class:`virtual_cell.PhyloUnit.PhyloUnit`
            phylounit to map
        
        Returns
        ------_
        iterator of class:`ete3.TreeNode`
        '''
        node_ids = []
        for _tp, node in self.nodes_dict[phylo_unit].items():
            node_ids.append(node.newick_id)
        return list(self._node_ids_to_ete_nodes(ete_tree_struct, node_ids))
    
    def ete_phylo_to_ete_death_node(self, ete_tree_struct, phylo_unit):
        '''
        Return TreeNode representing the death of a phylo_unit.
        '''
        phylo_node = self.nodes_dict[phylo_unit][phylo_unit.time_death]
        return ete_tree_struct.named_node_dict[phylo_node.newick_id]
    
    def phylo_to_ete_nodes(self,ete_tree_struct, phylo_unit):
        '''
        Return TreeNode objects in the ete_tree representing the birth and death
        nodes for this phylo_unit (e.g. cell or gene).
         
        Parameters
        ----------
        ete_tree_struct : class:`my_tools.utility.ETEtreeStruct`
            ete tree struct in which to find the phylo_unit
        phylo_unit: class:`virtual_cell.PhyloUnit.PhyloUnit`
            phylounit to map
        
        Returns
        ------
        list of class:`ete3.TreeNode`
        '''
        nodes = []
        nodes += self.ete_phylo_to_ete_birth_nodes(ete_tree_struct, phylo_unit)
        nodes += self.ete_phylo_to_ete_stem_nodes(ete_tree_struct, phylo_unit)
        try:
            death_node = self.ete_phylo_to_ete_death_node(ete_tree_struct, phylo_unit)
            nodes.append(death_node)
        except KeyError:
            pass
        return nodes
            
    def ete_node_to_phylo_unit(self, ete_tree_struct, ete_node):
        '''
        Maps TreeNode to PhyloUnit.
        
        Parameters
        ----------
        ete_node : TreeNode
            node to map
        
        Returns
        -------
        PhyloUnit
        '''
        return ete_tree_struct.node_name_to_phylo_node[ete_node.name].val
    
    def ete_nodes_to_phylo_units(self, ete_tree_struct, nodes=None):
        '''
        Obtain a list of all the phylo units that are represented in the ete
        tree.
        
        The ete_tree is traversed and ete node names are mapped first to
        PhyloTree nodes. The PhyloNodes have a reference to the PhyloUnit in
        their 'val' attribute.
        '''
        return self.ete_get_phylo2ete_dict(ete_tree_struct, nodes).keys()
    
    def ete_get_phylo2ete_dict(self, ete_tree_struct, nodes=None):
        '''
        Return mapping from ete PhyloUnits to lists of ete TreeNode objects.
        
        The mapping is constructed for a set of TreeNodes *nodes*. The default
        action is to map all the TreeNodes in the current ete_tree.
        
        Parameters
        ----------
        nodes : sequence
            sequence of TreeNodes
            
        Returns
        -------
        dictionary from class:`virtual_cell.PhyloUnit.PhyloUnit`s to list of class:`ete3.TreeNode`s
        '''
        
        if nodes is None:
            nodes = list(ete_tree_struct.tree.traverse())
        phylo2ete = OrderedDefaultdict(list)
        for ete_node in nodes:
            phylo_unit = self.ete_node_to_phylo_unit(ete_tree_struct, ete_node)
            phylo2ete[phylo_unit].append(ete_node)
        return phylo2ete
    
    def ete_prune_leafs(self, ete_struct):
        '''
        Prune the external nodes of an 'ete tree'.
        
        Parameters
        ----------
        ete_struct : class:`my_tools.utility.ETEtreeStruct`
            struct holding data for the ete tree
        '''
        to_prune = set()
        for l in ete_struct.tree.get_leaves():
            to_prune.add(l)
        for l in to_prune:
            l.detach()
            del ete_struct.named_node_dict[l.name]
    
    def ete_prune_internal(self, ete_tree_struct):
        '''
        Excise all internal nodes that have a single child, while preserving the
        length of the branch.
        '''
        to_prune = set()
        for n in ete_tree_struct.tree.traverse():
            if not n.is_leaf() and not n.is_root():
                if len(n.children) == 1:
                    to_prune.add(n)
        for n in to_prune:
            n.delete(prevent_nondicotomic=True, preserve_branch_length=True)
            del ete_tree_struct.named_node_dict[n.name]
        
    def ete_prune_external(self,ete_tree_struct, prune_depth):
        print 'pruning tree to max depth', prune_depth,
        to_detach = set()
        for node in ete_tree_struct.tree.iter_leaves(is_leaf_fn = lambda n: 
                                                     self.ete_node_to_phylo_unit(ete_tree_struct,
                                                                                 n).time_birth > prune_depth):
            print '.',
            to_detach.add(node)
        for n in to_detach:
            n.detach()
            del ete_tree_struct.named_node_dict[n.name]
        print 'done'
    
    def ete_annotate_tree(self, ete_tree_struct, features=[], func_features=dict(), ete_root=None):
        '''
        Annotate the phylogenetic tree with cell data for tree plotting.
        
        Assumes that the ete_tree has been constructed/updated. Creates a
        dictionary of feature dictionaries, keyed by the cells in the tree.
        Attaches the feature dictionaries to nodes in the ete_tree
        (annotate_ete_tree). Transforms some data to cummulative data along the
        branches of the tree. Optionally, prunes internal tree nodes (this will
        greatly simplify the tree drawing algorithm). Finally, transforms some
        data to rate of change data, using branch length for rate calculation.
        
        :param prune_internal: if True, nodes with 1 offspring only will be
        removed/collapsed and their branch length added to the preceding node on
        the branch.
        '''
        if ete_root is None:
            ete_root = ete_tree_struct.tree
        for c, ete_nodes in self.ete_get_phylo2ete_dict(ete_tree_struct, ete_root.traverse()).items(): 
            feature_dict = dict()  # NOTE: unordered ok
            for feature in features:
                feature_dict[feature] = getattr(c, feature)
            for feature, func in func_features.items():
                feature_dict[feature] = func(c)
            for ete_node in ete_nodes:
                ete_node.add_features(**feature_dict)
    
    def ete_cummulative_features(self, ete_tree_struct, features=[], 
                                 func_features=dict(), ete_root=None):
        if ete_root is None:
            ete_root = ete_tree_struct.tree
        for feature in features + func_features.keys():
            self.ete_convert_feature_to_cummulative(ete_tree_struct, feature, ete_root)
    
    def ete_rate_features(self, ete_tree_struct, features=[], 
                          func_features=dict(), ete_root=None):
        if ete_root is None:
            ete_root = ete_tree_struct.tree
        max_rate_dict = dict()
        for feature in features + func_features.keys():
            max_rate, rate_feature = self.ete_convert_feature_to_rate(ete_root=ete_root,
                                                                      feature=feature)
            max_rate_dict[rate_feature] = max_rate
        return max_rate_dict
    
    def ete_convert_feature_to_cummulative(self, ete_tree_struct, feature, ete_root):
        '''
        Convert annotated feature values to cummulative values.
        
        By starting at the root, values further down the tree can be computed by
        adding values calculated for the parent node. It is useful when for
        example the aim is to prune away internal nodes and rates of change of a
        feature need to be calculated on the pruned tree.
        '''
        for n in ete_root.traverse('levelorder'):
            if n is ete_root:
                continue
            parent = n.up
            #if parent is not None:
            new_val = getattr(parent, feature)
            if (self.ete_node_to_phylo_unit(ete_tree_struct, n) 
                is not self.ete_node_to_phylo_unit(ete_tree_struct, parent)):
                # don't add the value if we're looking at an identical phylo_unit
                try:
                    new_val += getattr(n, feature)
                except AttributeError:
                    print feature, 'not found for', n.name
                    #raise  
            setattr(n,feature, new_val)
    
    def ete_convert_feature_to_rate(self, ete_root, feature, 
                                    replace_tup=('count','rate')):
        '''
        Convert an annotated feature on the tree nodes to a rate. 
        
        The function assumes cummulative values of the feature. The rate is
        calculated by dividing the difference of the feature value between a
        parent and child by the corresponding branch length.
        '''
        max_rate = 0
        rate_feature = feature.replace(*replace_tup)
        for n in ete_root.traverse('levelorder'):
            rate = 0
            if n is not ete_root: #n.up is not None:
                branch_length = n.get_distance(n.up)
                parent_val = getattr(n.up, feature)
                my_val = getattr(n, feature)
                distance = my_val - parent_val
                
                if branch_length > 0:
                    rate = distance/ branch_length
                if rate > max_rate:
                    max_rate = rate
            setattr(n,rate_feature, rate)
        return max_rate, rate_feature
    
    def annotate_phylo_units_feature(self, ete_tree_struct, phylo_units, feature_name):
        '''
        '''
        phylo_units = set(phylo_units)
        for cell in phylo_units:
            for node in self.phylo_to_ete_nodes(ete_tree_struct, cell):
                has_feat = True
                if not hasattr(node, feature_name): # Check if this wasn't already annotated
                    node.add_feature(feature_name, has_feat)
        
    def annotate_leafs(self,ete_tree_struct, leaf):
        '''
        Annotate leaf labels 
        '''
        for node in self.phylo_to_ete_nodes(ete_tree_struct, leaf):
            if node.is_leaf():
                node.add_feature('leaflabel', str(leaf.id))
    
    def __str__(self):
        out = ''
        for phylo_unit, tp_dict in self.nodes_dict.items():
            out += str(phylo_unit.id) + ':\n'
            for tp, node in tp_dict.items():
                out += "  t="+str(tp) + ":" + str(node) + '\n'
        return 'ROOTS:\n '+ '\n'.join( [str(root) for root in self.roots]) + '\n' + out
    
    def __len__(self):
        return sum([ len(nodes) for nodes in self.nodes_dict.values() ] )
    
    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added. 
        Adapted from recipe at http://code.activestate.com/recipes/521901-upgradable-pickles/
        '''
        version = float(self.version)
        if version < 1.:
            self.ete_trees = OrderedDict()
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class', 
        print self.__class__.__name__, ' from version', version ,'to version', self.version

    def __getstate__(self):
        odict = self.__dict__.copy()
        return odict
        
    def __setstate__(self, d):
        self.__dict__ = d
        # upgrade class if it has an older version
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()
    
