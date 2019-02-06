'''
Created on Sep 13, 2014
@author: thocu
'''

import matplotlib as mpl
from matplotlib import cm
from matplotlib.figure import Figure
import matplotlib.backends.backend_agg as backend
from matplotlib.markers import MarkerStyle
from matplotlib.gridspec import GridSpec
import numpy as np
import itertools as it
import networkx as nx
from networkx import nx_pydot
from ete3 import TreeStyle, PieChartFace, TextFace
import os.path

from abc import abstractmethod
import math
import VirtualMicrobes.my_tools.utility as util
from VirtualMicrobes.my_tools.utility import GridPos
import shutil
import warnings
from VirtualMicrobes.event.Reaction import ClassConvert
from ete3.treeview.main import NodeStyle, add_face_to_node

#===============================================================================
# def flatten_list_dict(dict_of_lists):
#     print dict_of_lists
#     return reduce(lambda x,y: x+y, dict_of_lists.values(), [])
#===============================================================================

class GraphingError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class GraphNotFoundError(GraphingError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PositionOutsideGridError(GraphingError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    
    
class AttributeMap(object):
    def __init__(self, mol_class_dict, reactions_dict, species_markers):
        self.init_color_maps(species_markers)
        self.shape_map = {'tf': 'D', 'pump':'s', 'enz':'o', 'conversion':'o', 'import':'s', 'metabolite':'p'}
        self.prot_line_style_dict = {'tfs': '--', 'pumps':'-.', 'enzymes': '-'}
        self.activation_map = mpl.cm.get_cmap('RdBu_r')
        self.init_mol_class_color_dict(mol_class_dict)
        self.small_mols_color_dict.update([ (mol.paired, c) for (mol,c) in self.small_mols_color_dict.items() ])      

        self.reactions_color_dict = dict() # NOTE: unordered ok
        self.reactions_color_dict.update( [ (i,c) for (i,c) in zip(reactions_dict['import'], 
                                                         self.color_maps['pumps']
                                                         (np.linspace(0.,.9, len(reactions_dict['import'])) ))])
        self.reactions_color_dict.update( [ (i,c) for (i,c) in zip(reactions_dict['conversion'], 
                                                         self.color_maps['enzymes']
                                                         (np.linspace(0.1,0.9, len(reactions_dict['conversion']))))])
        self.reactions_color_dict.update( [ (m,c) for (m,c) in zip(mol_class_dict.keys(), 
                                                         self.color_maps['tfs']
                                                         (np.linspace(0.5,1., len(mol_class_dict))))])
        
    def init_mol_class_color_dict(self, mol_class_dict):
        color_map = self.color_maps['internal_res']
        mol_color_dict = dict() # NOTE: unordered ok
        starts, step = np.linspace(0, 1, len(mol_class_dict), endpoint=False, retstep=True)
        stops = [ s+step/2 for s in starts ]
        intervals =  zip(starts,stops)
        for (_mol_class, mols), (start,stop) in zip(mol_class_dict.items(), intervals):
            mol_color_dict.update([ (mol, color_map(v)) for (mol,v) in  zip(mols, np.linspace(start,stop, len(mols)) ) ] )
        self.small_mols_color_dict = mol_color_dict
            
    def init_color_maps(self, species_markers):
        self.color_maps = dict() # NOTE: unordered ok
        cm = mpl.cm.get_cmap('Set1', len(species_markers))
        cm.set_under('k')
        cm.set_over('w')
        self.color_maps['lineage'] = cm
        cm = mpl.cm.get_cmap('Set1', len(species_markers))
        cm.set_under('k')
        cm.set_over('w')
        self.color_maps['metabolic_type'] = cm
        cm = mpl.cm.get_cmap('inferno')
        cm.set_under('r')
        self.color_maps['resource_conc'] = cm 
        cm = mpl.cm.get_cmap('hot')
        cm.set_bad('grey')
        cm.set_over('magenta')
        cm.set_under('g')
        self.color_maps['cell_vals'] = cm 
        self.color_maps['mutation_rates'] = mpl.cm.get_cmap('hot')
        self.color_maps['internal_res'] = mpl.cm.get_cmap('jet')
        self.color_maps['external_res'] = mpl.cm.get_cmap('jet')
        self.color_maps['enzymes'] = mpl.cm.get_cmap('jet') #summer
        self.color_maps['tfs'] = mpl.cm.get_cmap('copper') #'autumn'
        self.color_maps['pumps'] = mpl.cm.get_cmap('winter')
        
    def color_reaction(self,r):
        return tuple(self.reactions_color_dict[r])
    
    def color_mol_class(self, mc):
        return self.reactions_color_dict[mc]
        
    def color_mol(self, mol):
        return self.small_mols_color_dict[mol]
    
    def color_protein(self, g):
        color = None
        if g['type'] in ['enz', 'pump']:
            color = self.color_reaction(g.reaction)
        elif g['type'] == 'tf':
            color = self.color_mol_class(g.ligand_class)
        return color
    
    def activation_color(self, effect, domain=(-1,1)):
        color_domain = (0,1.)
        val = color_domain[1] * (effect + (color_domain[0] - domain[0]) ) / (domain[1] - domain[0])
        return self.activation_map(val)
    
    def protein_type_line_style(self,type_):
        line_style='-'
        if self.prot_line_style_dict.has_key(type_):
            line_style= self.prot_line_style_dict[type_]
        return line_style
    #===========================================================================
    # def __getstate__(self):
    #     odict = self.__dict__.copy()
    #     del odict['color_maps']
    #     return odict
    # 
    # def __setstate__(self, odict):
    #     self.__dict__ = odict
    #     self.init_color_maps()
    #===========================================================================
    
class Grapher(object):
    
    class_version = '1.0'
    
    def __init__(self, base_save_dir, name, show=True, attribute_dict=None, clean=True, create=True):
        self.version = self.__class__.class_version
        
        self.name = name
        self.base_save_dir = base_save_dir
        self.show = show
        self.init_save_dir(clean=clean, create=create)
        self.attribute_mapper = attribute_dict  
        
    def init_save_dir(self, clean=False, create=True):
        if create:
            remove_globs = ['*.png', '*.svg', '*.graphml', '*.gml', '*.nw', '*.dot', '*.nhx', '*.mp4', '*.txt'] if clean else []
            util.ensure_dir(self.save_dir, remove_globs=remove_globs)
    
    def change_save_location(self, base_dir=None, name=None, clean=False, create=True):
        if base_dir is not None:
            self.base_save_dir = base_dir
        if name is not None:
            self.name = name        
        self.init_save_dir(clean=clean, create=create)
        
    def init_attribute_mapper(self, mol_class_dict, reactions_dict, species_markers):
        self.attribute_mapper = AttributeMap(mol_class_dict, reactions_dict, species_markers)
        
    @property
    def save_dir(self):
        return os.path.join(self.base_save_dir, self.name)
    
    def update_figure(self, show=None):
        if show is None:
            show = self.show
        #We need to draw *and* flush
        self.figure.canvas.draw()
        if show:
            self.figure.canvas.flush_events()
            self.figure.show()
            
    def backup_plots(self):
        for fn in os.listdir(self.save_dir):
            splits = fn.split('.')
            fn, ext = '.'.join(splits[:-1]), splits[-1]
            if not fn.endswith('bak'):
                shutil.copy2(os.path.join(self.save_dir,'.'.join([fn,ext])), os.path.join(self.save_dir,'.'.join([fn,'bak',ext])))
    
    def save_fig(self, name=None, labels=[], title=None, suffix=".svg", copy_labels=None, **kwargs):
        '''
        Render and save a figure. 
        
        Parameters
        ----------
        name : str
            base name of the figure
        labels : iterable
            additional labels in file name
        title : str
            printable title of figure
        suffix : str
            file extension suffix
        copy_labels : iterable
            additional labels for the filename of a copy of the figure
            
        Returns
        -------
        list of filenames of the saved figure(s)
        '''
        if name is None:
            name = self.name
        save_file = os.path.join(self.save_dir, "_".join(name.split() + map(str,labels)) + suffix)
        saved = []
        if title is not None:
            self.figure.suptitle(title, fontsize=30, fontweight='bold')
        self.figure.savefig(save_file, **kwargs)
        saved.append(save_file)
        if copy_labels is not None:
            copy_save = os.path.join(self.save_dir, '_'.join(name.split() + map(str,copy_labels))  + suffix)
            shutil.copy2(save_file, copy_save)
            saved.append(copy_save)
        return saved
    
    def save_fig2(self, ext, name=None, title=None, **kwargs):
        '''
        Render and save a figure. 
        
        Parameters
        ----------
        name : str
            base name of the figure
        title : str
            printable title of figure
        suffix : str
            file extension suffix
            
        Returns
        -------
        filename of the saved figure
        '''
        if name is None:
            name = self.name
        save_file = os.path.join(self.save_dir, "_".join(name.split() ))
        if title is not None:
            self.figure.suptitle(title, fontsize=50, fontweight='bold')
        self.figure.savefig(save_file, format=ext, **kwargs)
        return save_file
        
    def save_video(self, video=None, frame=None):
        if frame is not None and video is not None:            
            cmd = str(video+" -y -i '"+frame+"' -s 1500x1500 -vb 80000k -r 5 -pix_fmt yuv420p '"+frame+"_lastframe.mp4' 2> /dev/null")
            os.system(cmd)
            if os.path.isfile(frame+".mp4"):
                cmd = str(video+" -y -f concat -i '"+frame+".txt' -c:a copy '"+frame+"~.mp4' 2> /dev/null; mv '"+frame+"~.mp4' '"+frame+".mp4' 2> /dev/null")
                os.system(cmd)
            else:
                cmd = str("printf \"file '"+frame+".mp4'\nfile '"+frame+"_lastframe.mp4'\n\" > '"+frame+".txt' 2> /dev/null; cp '"+frame+"_lastframe.mp4' '"+frame+".mp4' 2> /dev/null")
                os.system(cmd)
    
    def upgrade(self, odict):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added. (see also __setstate__) 
        
        Adapted from recipe at http://code.activestate.com/recipes/521901-upgradable-pickles/
        '''
        version = float(self.version)
        if version < 1.:
            self.base_save_dir = os.path.split(odict['save_dir'])[0]
            del self.__dict__['save_dir']
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class', 
        print self.__class__.__name__, ' from version', version ,'to version', self.version

    def __setstate__(self, d):
        self.__dict__ = d
        self.subprocesses = []
        # upgrade class if it has an older version
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade(d)
        
            
class Network(Grapher):    
    
    def __init__(self, base_save_dir, name, attribute_dict, size=(10,10), show=True, **kwargs):
        self.name = name
        self.figure = Figure(size)
        canvas = backend.FigureCanvas(self.figure)
        self.figure.set_canvas(canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')
        self.G = None
        super(Network, self).__init__(base_save_dir, name, attribute_dict=attribute_dict,
                                      show=show, **kwargs)
        
    @abstractmethod
    def init_network(self):
        pass
    
    def gene_node_id(self, gene):
        return "_"+str(gene.id)
    
    def gene_node_label(self, gene_node_id, depth=1):
        return '.'.join(gene_node_id.strip("_").split('.')[0:depth])

    def n_attr_list(self, attr, selectors=[]):
        return [  d[attr] for _,d in self.G.nodes_iter(data=True) 
                if reduce(lambda a,b: a and b, 
                          [ d.get(selector[0]) == selector[1] for selector in selectors], True) ]
    
    def nodes_with_attr_list(self, selectors=[]):
        return [  n for n,d in self.G.nodes_iter(data=True) 
                if reduce(lambda a,b: a and b, 
                          [ d.get(selector[0]) == selector[1] for selector in selectors], True) ]
    
    def e_attr_list(self, attr, selectors=[]):
        return [  d[attr] for (_,_,d) in self.G.edges_iter(data=True) 
                if reduce(lambda a,b: a and b, 
                          [ d.get(selector[0]) == selector[1] for selector in selectors], True) ]
    
    def edges_with_attr_list(self, selectors=[]):
        return [  (s,e) for (s,e,d) in self.G.edges_iter(data=True) 
                if reduce(lambda a,b: a and b, 
                          [ d.get(selector[0]) == selector[1] for selector in selectors], True) ]
        
    def type_shape(self, reac_type):
        shape = None
        if self.attribute_mapper.shape_map.has_key(reac_type):
            shape = self.attribute_mapper.shape_map[reac_type]
        return shape
    
    def add_self(self, marker):
        self.G.add_node('self', marker=marker)
        
    def clear_graph(self):
        self.G.clear()
        
    def metabolite_edge_width(self, bb, cell_bb=False):
        edgewidth = 1
        if cell_bb:
            edgewidth = 4
        elif bb:
            edgewidth = 2
        return edgewidth
        
    def color_edge_direction(self, i):
        color = 'grey'
        if i == -1:
            color = mpl.colors.colorConverter.to_rgba('b')
        elif i == 1:
            color = mpl.colors.colorConverter.to_rgba('r')
        elif i == 0:
            color = mpl.colors.colorConverter.to_rgba('black')
        return color
    
    def redraw_network(self, **kwargs): 
        self.ax.clear()
        self.ax.axis('off')
        # Note: don't try to use self.ax.relim() as it does not work with the 
        self.ax.set_xlim((0,1e-4), auto=True)
        self.ax.set_ylim((0,1e-4), auto=True)
        self.draw_network(**kwargs)    
          
        
    def write_to_file(self, name=None, labels=[], suffix=".gml", **kwargs):
        if name is None:
            name = self.name
        filename = "_".join(name.split()+ map(str,labels)) + suffix
        path = os.path.join(self.save_dir, filename)
        if suffix == '.gml':
            nx.write_gml(self.G, path, str)
        elif suffix == '.dot':
            print 'writing dot'
            try:
                nx_pydot.write_dot(self.G, path)
            except KeyError as e:
                print e
            
    
    def __str__(self):
        return str(self.G)

class Genome(Grapher):   
    
    def __init__(self, base_save_dir, name, attribute_dict, size=(10,10), show=True, **kwargs):
        self.name = name
        self.figure = Figure(size)
        self.ax = self.figure.add_subplot(111)
        canvas = backend.FigureCanvas(self.figure)
        self.figure.set_canvas(canvas)
        self.ax.axis('equal')
        self.G = None
        super(Genome, self).__init__(base_save_dir, name, attribute_dict=attribute_dict,  
                                      show=show, **kwargs)
    
    def plot_genome_structure(self, cell, labels, video=None, max_size=None):
        '''
        Render the genome structure as a circular (plasmid-like) representation.        
        :param cell: which genome is plotted 
        '''
        if max_size is None:
            max_size = cell.genome.size
                 
        #timebirth = str(cell.time_birth).zfill(10) # Label for this cell
        
        # Makes list of all gene labels, colors, sizes etc
        for i, chrom in enumerate(cell.genome.chromosomes): #TODO: plot all chromosomes in 1 figure 
            #NOTE: now, figure is cleared for every new chromosome and only last chromosome will be drawn when
            # calling save_fig()
            gene_labels = []     # Labels to be plotted alongside donutgraph
            colors = []     # Colors for genes
            sizes = []      # Enzymes and pumps are 1, TFs are scaled with out-degree to easily note hubs)
            explode = []    # Distance from center increases for highly expressed genes
            self.ax.clear()
            for g in chrom:
                if g['type'] == 'pump':
                    gene_labels.append(str('pmp '+ str(g.reaction.substrate_class))) 
                    sizes.append(1)
                elif g['type'] == 'enz':
                    gene_labels.append(str('enz '+ ''.join( '['+str(cl)+']' for cl in g.reaction.reactants ) + 
                                      '>'+ ''.join( '['+str(cl)+']' for cl in g.reaction.products )))
                    sizes.append(1)
                elif g['type'] == 'tf':
                    gene_labels.append(str('tf '+ str( g.ligand_class)))
                    sizes.append((len(g.binding_sequence.bound_operators)+0.5))
                colors.append(str(mpl.colors.rgb2hex(self.attribute_mapper.color_protein(g))))
                explode.append(g.promoter.strength*0.025)
            
            #plt.rcParams['patch.linewidth'] = 1.5
            #plt.rcParams['patch.edgecolor'] = 'black'
            #plt.rcParams['text.color'] = 'black'
            #plt.rcParams['font.size'] = 7
            
            #scaling = 0.4*cell.genome.size/max_size
            self.ax.clear()
            #plt.clf()
            #self.ax = self.figure.add_axes([(1-0.5-scaling)/2, (1-0.5-scaling)/2, 0.5+scaling, 0.5+scaling]) 
            self.ax.pie(sizes, labels=gene_labels, colors=colors, 
                             explode=explode, labeldistance=1.05, radius=1)
            
            centre_circle = mpl.patches.Circle((0,0),0.97,
                                       color='black', fc='white',linewidth=1.5)
            self.ax.add_artist(centre_circle)
            self.ax.text(0,0,'Time: '+str(labels[0])+'\n#Genes: '+str(cell.genome.size), 
                     horizontalalignment='center', 
                     verticalalignment='center',
                     fontsize=15)
            self.ax.set_axis_off()
            name = 'GenomeStruct'
            if i > 0:
                name += '-c'+str(i)
            self.figure.savefig(os.path.join(self.save_dir,name))
            name += '_'.join(map(str, labels)) 
            self.figure.savefig(os.path.join(self.save_dir,name))
             
        if video is not None:
            self.save_video(video, frame="GenomeStruct.png")
        else:
            print 'skip ffmpeg video step (no suitable ffmpeg found)'
        
class MetabolicNetwork(Network):
    
    def __init__(self, base_save_dir, name, mol_class_dict, conversions, imports, size=(30,30), attribute_dict=None, **kwargs):
        
        super(MetabolicNetwork, self).__init__(base_save_dir, name, attribute_dict, size=size, **kwargs)
        self.init_network(mol_class_dict, conversions, imports)
        self.layout_network_positions()
        
    def init_network(self, mol_class_dict, conversions, imports):
        self.G = nx.DiGraph()
        metabolites = reduce(lambda x,y: x+y, [ mols for mols in mol_class_dict.values()  ])
        self.G.add_node('self', marker=None, present=False, color=mpl.colors.colorConverter.to_rgba('grey'))
        for c in conversions:
            self.G.add_node(c, type='conversion')
            if isinstance(c, ClassConvert):
                self.G.node[c]['classC'] = True
            else:
                self.G.node[c]['classC'] = False
            sub_reaction_dicts = c.sub_reaction_dicts
            for sub_reaction_dict in sub_reaction_dicts:
                for r in sub_reaction_dict['reactants']:
                    self.G.add_node(r['mol'], stoi=r['stoi'])
                    self.G.add_edge(r['mol'], c)
                for p in sub_reaction_dict['products']:
                    self.G.add_node(p['mol'], stoi=p['stoi'])
                    self.G.add_edge(c, p['mol'])
        for i in imports:
            self.G.add_node(i, type='import')
            sub_reaction_dicts = i.sub_reaction_dicts
            for sub_reaction_dict in sub_reaction_dicts:
                e_dict = sub_reaction_dict['reactants']['energy']
                p_dict = sub_reaction_dict['products']['substrate']
                self.G.add_node(p_dict['mol'], stoi=p_dict['stoi'])
                self.G.add_edge(i, p_dict['mol'], eneStoi=e_dict['stoi'] )
                self.G.add_edge(p_dict['mol'],i, eneStoi=e_dict['stoi'] )
        nx.set_node_attributes(self.G, 'color', mpl.colors.colorConverter.to_rgba('grey'))
        nx.set_edge_attributes(self.G, 'color', mpl.colors.colorConverter.to_rgba('grey'))
        for m in metabolites:
            self.G.add_node(m, type='metabolite', buildingBlock=m.is_building_block, color=self.attribute_mapper.color_mol(m))    
    
    def color_reactions(self, conversions, imports, building_blocks=[],
                        self_marker=None, reac_color_func=None, 
                        mol_color_func=None, edge_color_func=None):
        if self_marker is not None:
            self.G.node['self']['marker'] = self_marker
            self.G.node['self']['color'] = self.attribute_mapper.color_maps['lineage'](self_marker)
            self.G.node['self']['present'] = True
        if reac_color_func is None:
            reac_color_func=self.attribute_mapper.color_reaction 
        if mol_color_func is None:
            mol_color_func = self.attribute_mapper.color_mol
        if edge_color_func is None:
            edge_color_func = self.color_edge_direction
        if building_blocks is not None:
            for bb in building_blocks:
                self.G.node[bb]['cellBB'] = True
        for conv, _ in conversions:
            class_convert = self.G.node[conv]['classC']
            self.G.node[conv]['color'] = reac_color_func(conv)
            self.G.node[conv]['present'] = True
            sub_reaction_dicts = conv.sub_reaction_dicts
            for sub_reaction_dict in sub_reaction_dicts:
                for r in sub_reaction_dict['reactants']:
                    consume=1
                    self.G.edge[r['mol']][conv]['color'] = edge_color_func(consume)
                    self.G.node[r['mol']]['color'] = mol_color_func(r['mol'])
                    if not class_convert:
                        self.G.edge[r['mol']][conv]['present'] = True
                for p in sub_reaction_dict['products']:
                    consume=-1
                    self.G.edge[conv][p['mol']]['color'] = edge_color_func(consume)
                    self.G.node[p['mol']]['color'] = mol_color_func(p['mol'])
                    if not class_convert:
                        self.G.node[p['mol']]['present'] = True
                        self.G.edge[conv][p['mol']]['present'] = True                        
        for i, exporting in imports:
            self.G.node[i]['color'] = reac_color_func(i)
            self.G.node[i]['present'] = True
            if exporting:
                self.G.node[i]['exporting'] = True
            sub_reaction_dicts = i.sub_reaction_dicts
            for sub_reaction_dict in sub_reaction_dicts:
                _e_dict = sub_reaction_dict['reactants']['energy']
                p_dict = sub_reaction_dict['products']['substrate']
                self.G.node[p_dict['mol']]['color'] = mol_color_func(p_dict['mol'])
                if not exporting:
                    #self.G.node[p_dict['mol']]['present'] = True
                    #self.G.edge[i][p_dict['mol']]['present'] = True
                    self.G.edge[i][p_dict['mol']]['color'] = edge_color_func(-1)
                else:
                    self.G.edge[p_dict['mol']][i]['color'] = edge_color_func(1)
               
    def layout_network_positions(self):
        sorted_imports = sorted(self.nodes_with_attr_list([ ('type','import') ]), key=lambda i: str(i.substrate_class))
        sorted_metabolites = sorted(self.nodes_with_attr_list([ ('type','metabolite') ] ), key=lambda m: str(m.mol_class) )
        sorted_conversions = sorted(self.nodes_with_attr_list([ ('type','conversion'),('classC',False) ]), 
                                    key=lambda c: (map(str, c.products), map(str, c.reactants))) #  str(c.products[0]), str(c.reactants[0])))
        sorted_class_conversions = sorted(self.nodes_with_attr_list([ ('type','conversion'),('classC',True) ]), key=lambda c: str(c.products[0]))
        if len(sorted_class_conversions) == 0:
            sorted_class_conversions = range(len(sorted_conversions))
        self.pos = nx.shell_layout(self.G, nlist=[['self'],
                                                  range(len(sorted_conversions)),
                                                  range(len(sorted_conversions)),
                                                  sorted_conversions,
                                                  range(len(sorted_metabolites)),
                                                  sorted_metabolites,
                                                  range(len(sorted_class_conversions)),
                                                  sorted_class_conversions,
                                                  range(len(sorted_imports)),
                                                  sorted_imports ])
        #nodes, positions = zip(*self.pos.items())
        #self.pos.update( dict(zip(nodes,  nx.layout._rescale_layout(np.array(positions), scale=4))))
        
    def draw_network(self, reactions_dict=None, self_marker=None, building_blocks=None):
            
        if reactions_dict is not None:
            nx.set_node_attributes(self.G, 'color', mpl.colors.colorConverter.to_rgba('0.95'))
            nx.set_node_attributes(self.G, 'present', False)
            nx.set_node_attributes(self.G, 'cellBB', False)
            nx.set_node_attributes(self.G, 'exporting', False)
            nx.set_edge_attributes(self.G, 'color', mpl.colors.colorConverter.to_rgba('0.95'))
            nx.set_edge_attributes(self.G, 'present', False)
            self.color_reactions(reactions_dict['conversion'],reactions_dict['import'],
                                 building_blocks=building_blocks,
                                 self_marker=self_marker)

        labels = dict() # NOTE: unordered ok
        for type_ in ['metabolite','conversion','import']:
            linewidths=1
            node_selectors = [ ('present', True), ('type',type_) ]
            nodes = self.nodes_with_attr_list(node_selectors)
            labels.update(dict([ (n, '\n-->\n'.join(str(n).split('-->'))) for n in nodes ]))
            if type_ == 'metabolite':
                building_block_attr = self.n_attr_list('buildingBlock',node_selectors)
                cell_bb_attr = self.n_attr_list('cellBB',node_selectors)
                linewidths = list(it.starmap(self.metabolite_edge_width, zip(building_block_attr, cell_bb_attr)))
            if type_ == 'import':
                exporting_attr = self.n_attr_list('exporting',node_selectors)
                linewidths = [ 0.3 if ex else 3 for ex in exporting_attr ]
                
            nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax, 
                             nodelist=nodes , 
                             node_color=self.n_attr_list('color', node_selectors),
                             node_shape=self.type_shape(type_), #hold=False,
                             node_size=1000,
                             linewidths=linewidths,
                             alpha=0.8)
            
            linewidths=1
            node_selectors = [ ('present', False), ('type',type_) ]
            nodes = self.nodes_with_attr_list(node_selectors)
            if type_ == 'metabolite':
                building_block_attr = self.n_attr_list('buildingBlock',node_selectors)
                cell_bb_attr = self.n_attr_list('cellBB',node_selectors)
                linewidths = list(it.starmap(self.metabolite_edge_width, zip(building_block_attr, cell_bb_attr)))
                #add labels on absent metabolites (but not other types
                labels.update(dict([ (n, '\n-->\n'.join(str(n).split('-->'))) for n in nodes ]))
            if type_ == 'import':
                exporting_attr = self.n_attr_list('exporting',node_selectors)
                linewidths = [ 0.3 if ex else 3 for ex in exporting_attr ]
                
            nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax, 
                             nodelist=nodes , 
                             node_color=self.n_attr_list('color',node_selectors),
                             node_shape=self.type_shape(type_), #hold=False,
                             node_size=1000,
                             linewidths=linewidths,
                             alpha=0.2)

        nx.draw_networkx_labels(self.G, self.pos, labels, font_size=7, font_color="black", 
                                font_family="sans-serif", font_weight='heavy', alpha=1, ax=self.ax)
        #draw self node
        if self_marker is not None:
            nx.draw_networkx_nodes(self.G, self.pos, nodelist=['self'], node_size=800, node_shape='8',
                                   node_color = self.G.node['self']['color'],
                                   ax=self.ax)
            nx.draw_networkx_labels(self.G, self.pos, labels={'self': str(self.G.node['self']['marker'])}, 
                                    font_size=8, font_color="black", 
                                    font_family="sans-serif", font_weight='heavy', alpha=1, ax=self.ax)
        #draw edges
        nx.draw_networkx_edges(self.G, self.pos, edgelist=self.edges_with_attr_list([ ('present',False) ]), 
                                   edge_color=self.e_attr_list('color', [('present',False) ]),
                                   alpha=0.1
                                   , style='-', ax=self.ax, label="")
        nx.draw_networkx_edges(self.G, self.pos, edgelist=self.edges_with_attr_list([ ('present',True) ]), 
                                   edge_color=self.e_attr_list('color', [ ('present',True) ]),
                                   alpha=0.75
                                   ,style='-', ax=self.ax, label="") 
        
class BindingNetwork(Network):
    
    def __init__(self, base_save_dir, name, attribute_dict=None, size=(35,35), **kwargs):
        self.name = name
        super(BindingNetwork, self).__init__(base_save_dir, name, attribute_dict, size=size, **kwargs)
        
    def init_network(self, cell, with_self_marker=True):
        self.G = cell.GRN(prot_color_func=self.attribute_mapper.color_protein,
                          with_self_marker=with_self_marker)
        return self.G
    
    def layout_network_positions(self, prog):
        '''
        Compute and store node positions using a layout algorithm.
        
        Parameters
        ----------
        prog : str
            layout algorithm
        '''
        if prog in ['dot', 'neato', 'circo']:
            print 'attempting graphviz layout...'
            warnings.filterwarnings('ignore', '.* is not a known color.',)
            with warnings.catch_warnings():
                try:
                    G_copy = self.G.copy() # Make a copy without color attritube to circumvent anoying pydot warning
                    for nname in G_copy:
                        try:
                            del G_copy.node[nname]['color']
                        except KeyError:
                            pass
                    
                    self.pos = nx_pydot.graphviz_layout(G_copy, prog=prog)
                except (KeyError, OSError) as e:
                    print repr(e)
                    pass
        elif prog == 'nwx':
            self.pos = nx.spring_layout(self.G, scale=1.)
    
    def draw_network(self, self_marker=None, edge_effect='effect'):
        
        self_regulators = self.G.nodes_with_selfloops()
        labels = dict([ (n, "\n".join([str(data['typeLabel']), 
                                       data['label'], 
                                       str(data['copynr']) ])) for (n,data) in self.G.nodes_iter(data=True) 
                                       if data.has_key('typeLabel')
                       ]
                      )
        for type_ in ['tf', 'enz', 'pump']:
            node_selectors = [ ('type',type_) ]
            nodes = self.nodes_with_attr_list(node_selectors) 
            linewidths=1
            if type_ == 'tf':
                linewidths = [ 5 if n in self_regulators else 2 for n in nodes ]
            if type_ == 'pump':
                exporting_attr = self.n_attr_list('exporting', node_selectors)
                linewidths = [ 1 if ex else 5. for ex in exporting_attr ]
            nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax, 
                             nodelist=nodes, 
                             node_color=self.n_attr_list('color', node_selectors),
                             node_shape=self.type_shape(type_), 
                             labels=self.n_attr_list('copynr', node_selectors),
                             hold=False,
                             node_size=2500,
                             linewidths=linewidths,
                             alpha=0.8)
        nx.draw_networkx_labels(self.G, self.pos, labels, font_size=10, 
                                font_color='black', font_family='sans-serif', 
                                font_weight='heavy', alpha=1., ax=self.ax)
        
        for u,v,d in self.G.edges(data=True):
            nx.draw_networkx_edges(self.G, self.pos, [(u,v)], 
                                   width=d['strength']+0.5, 
                                   edge_color=[self.attribute_mapper.activation_color(d[edge_effect])]
                                   , style='-', ax=self.ax, label="") 
        #add self_marker
        if self_marker:
            positions = np.array(self.pos.values())
            min_node_pos = np.min(positions, axis=0) if len(positions) else np.array([0.,0])
            max_node_pos = np.max(positions, axis=0) if len(positions) else np.array([0.,0])
            
            self_pos = tuple(min_node_pos - 0.05 * (max_node_pos - min_node_pos))
            nx.draw_networkx_nodes(self.G, {'self':self_pos}, nodelist=['self'], node_size=2500, node_shape='8',
                                   node_color = self.attribute_mapper.color_maps['lineage'](self.G.node['self']['marker']),
                                   ax=self.ax)
            nx.draw_networkx_labels(self.G, {'self':self_pos}, labels={'self':str(self.G.node['self']['marker'])}, 
                                    font_size=10, font_color="black", 
                                    font_family="sans-serif", font_weight='heavy', alpha=1, ax=self.ax)

class MultiGraph(Grapher):
    line_markers = MarkerStyle.filled_markers
    line_styles = ["-",":","--", "-."]
    colors = cm.get_cmap('jet')(np.linspace(0,1,50))
    marker_sizes = [2.]
    marker_edge_widths=[.1]
    
    def __init__(self, base_save_dir, name, rows,cols,row_heigth=2, col_width=4, attribute_dict=None,
                 show=True, **kwargs):
        self.figure = Figure((cols * col_width, rows * row_heigth))
        canvas = backend.FigureCanvas(self.figure)
        self.figure.set_canvas(canvas)
        self.grid = GridSpec(rows, cols)
        self.grid_filled = [ [ False for _ in range(cols) ] for _ in range(rows) ]
        self.axes = dict() # NOTE: unordered ok
        super(MultiGraph,self).__init__(base_save_dir, name, attribute_dict=attribute_dict, show=show, **kwargs)

    @property
    def rows(self):
        return self.grid.get_geometry()[0]
    
    @property
    def cols(self):
        return self.grid.get_geometry()[1]
        
    def within_grid(self, pos, rows, cols):
        not_in_grid = False
        if pos.row < 0 or pos.col < 0:
            print "Negative position index"
            not_in_grid |= True
        if pos.row + rows > self.rows or pos.col + cols > self.cols:
            print "Some positions are outside the grid."
            not_in_grid |= True
        if not_in_grid:
            raise PositionOutsideGridError("coord:{0} rows:{1}, cols:{2} Falls outside grid with {3} rows and {4} cols ".format(pos, rows, cols, self.rows, self.cols))
        
    def append_data(self,axes_name, xdata, ydata):
        if self.axes[axes_name]['dat'] is None:
            self.axes[axes_name]['dat'] = (xdata,ydata)
        else:
            self.axes[axes_name]['dat'] = ( np.vstack((self.axes[axes_name]['dat'][0],xdata)),
                                        np.vstack((self.axes[axes_name]['dat'][1],ydata)))
        
    def append_to_axes(self, axes_name, xdata, ydata, line_in=[], autoscale=True):
        self.append_data(axes_name,xdata,ydata)
        ax = self.axes[axes_name]['ax']
        (xdatas,ydatas) = self.axes[axes_name]['dat']
        lines = ax.get_lines()
        if line_in:
            lines = [ lines[i] for i in line_in ]
        for ydata, line in zip(ydatas.T, lines):
            line.set_xdata(xdatas)
            line.set_ydata(ydata)
        ax.relim()
        if autoscale:
            try:
                ax.autoscale_view()
            except ValueError:
                pass
        
    def append_to_lines(self, axes_name, xdat, ydata_dict, autoscale=True):
        ax = self.axes[axes_name]['ax']
        lines_updated = []
        for key, y in ydata_dict.items():
            line = self.axes[axes_name]['lines_data'][key]
            xdata, ydata = line.get_data()
            if len(xdata) == 0:
                line.set_xdata(xdat)
            else:
                line.set_xdata(np.hstack( (xdata, xdat )))
            if len(ydata) == 0:
                line.set_ydata(np.array((y,)))
            else:
                line.set_ydata(np.hstack( (ydata, np.array((y,)))) )
            lines_updated.append(line)
        ax.relim()
        if autoscale:
            try:
                ax.autoscale_view()
            except ValueError:
                pass
        return lines_updated
        
    def add_lines(self, ax_name, nr_lines, **line_customization):
        ax = self.axes[ax_name]['ax']
        if isinstance(nr_lines, int):
            nr_lines = range(nr_lines)
        new_lines = []
        for item in nr_lines:
            line = mpl.lines.Line2D([], []) #, linewidth, linestyle, color, marker, markersize, markeredgewidth, markeredgecolor, markerfacecolor, markerfacecoloralt, fillstyle, antialiased, dash_capstyle, solid_capstyle, dash_joinstyle, solid_joinstyle, pickradius, drawstyle, markevery
            ax.add_line(line)
            self.axes[ax_name]['lines_data'][item] = line
            new_lines.append(line)
        self.customize_lines(new_lines, **line_customization)
        return new_lines
        
    def add_axis(self, name, pos, rows=1, cols=1, min_max_y=None, 
                 nr_lines=0, auto_scale=True, **plot_params): #, markers=None,line_styles=None, colors=None, 

        ax = self.figure.add_subplot(self.grid[pos.row:pos.row + rows, pos.col:pos.col+cols])
        ax.set_title(name)

        self.axes[name] = {'ax':ax, 'dat':None, 'lines_data':dict(), 
                           'range':None} # NOTE: unordered ok
        self.add_lines(name, nr_lines, **plot_params)
        if auto_scale:
            ax.set_autoscalex_on(True)
        if min_max_y != None:
            min_y, max_y = min_max_y
            self.ax.set_ylim(min_y, max_y)
        
        self.fill_grid(pos,rows,cols)
        return ax
    
    def customize_lines(self, lines ,markers=None,
                     line_styles=None, marker_sizes=None, 
                     marker_edge_widths=None,
                     colors=None):
        if markers is None:
            markers = self.line_markers
        if line_styles is None:
            line_styles = self.line_styles
        if colors is None:
            colors = self.colors
        if marker_sizes is None:
            marker_sizes = self.marker_sizes
        if marker_edge_widths is None:
            marker_edge_widths = self.marker_edge_widths
        marker_cycler = it.cycle(markers)
        line_style_cycler = it.cycle(line_styles)
        color_cycler = it.cycle(colors)
        ms_cycler = it.cycle(marker_sizes)
        mew_cycler = it.cycle(marker_edge_widths)
        for line in lines:
            if len(markers): # enables leaving markers unchanged by setting [], 0 or False
                line.set_marker(next(marker_cycler))
            if len(line_styles):
                line.set_linestyle(next(line_style_cycler))
            if len(colors):
                line.set_color(next(color_cycler))
            if len(marker_edge_widths):
                line.set_markeredgewidth(next(mew_cycler))
            if len(marker_sizes):
                line.set_markersize(next(ms_cycler))
        
    def fill_grid(self,pos, rows, cols):
        self.within_grid(pos, rows, cols)
        self.grid_free(pos, rows, cols)
        for r in range(pos.row, pos.row + rows):
            for c in range(pos.col, pos.col + cols):
                self.grid_filled[r][c] = True
                
    def grid_free(self, pos, rows, cols):
        occupied = []
        for r in range(pos.row, pos.row + rows):
            for c in range(pos.col,  pos.col + cols):
                if self.grid_filled[r][c]:
                    occupied.append((r,c))
        return not bool(len(occupied)), occupied
        
    def tight_layout(self, **kwargs):
        renderer = self.figure.canvas.get_renderer()
        self.grid.tight_layout(self.figure, renderer=renderer, **kwargs)
        
    def __getitem__(self, key):
        return self.axes[key]['ax']

class MultiGridGraph(MultiGraph):
    '''
    classdocs
    '''


    def __init__(self, base_save_dir, name, rows , cols, row_heigth=4, col_width=4, 
                 attribute_dict=None, show=True, **kwargs):
        super(MultiGridGraph, self).__init__(base_save_dir, name, rows, cols, row_heigth=row_heigth, 
                                         col_width=col_width, attribute_dict=attribute_dict, show=show, **kwargs)
        
        '''
        Constructor
        '''
        
    def add_axis(self, name, pos, rows=1, cols=1):
        return MultiGraph.add_axis(self, name, pos, rows=rows, cols=cols)
    
    def set_data_range(self, axes_name, _range):
        self.axes[axes_name]['range'] = _range
    
    def append_data(self, axes_name, time_point, data):
        self.axes[axes_name]['dat'] = (time_point, data)
    
    def append_to_axes(self, axes_name, time_point, data):
        self.append_data(axes_name,time_point, data)
        
    def plot_in_axes(self, axes_name, cm_name, matrix_data=None,  
                     data_range=None, color_bar=True):
        ax = self.axes[axes_name]['ax']
        if matrix_data is None:
            _, matrix_data = self.axes[axes_name]['dat']
            del self.axes[axes_name]['dat']
        title = ax.get_title()
        ax.clear()
        ax.set_title(title)
        color_map = self.attribute_mapper.color_maps[cm_name]
        if data_range is not None:
            min_val, max_val = data_range
        elif self.axes[axes_name]['range']:
            min_val, max_val = self.axes[axes_name]['range']
        else:
            max_val = np.max(matrix_data) # TODO: make this min and max fixed
            min_val = np.min(matrix_data)
        cb_tick_bounds = np.linspace(min_val, max_val, 5)
        img = ax.matshow(matrix_data, interpolation='nearest', cmap=color_map,
                 vmin=min_val, vmax=max_val, origin='lower')
        _format='%.3f'
        if max_val < 1e-2:
            _format='%.3e'
        cbargs = dict(format=_format, ticks=cb_tick_bounds, shrink=0.79)
        
        if self.axes[axes_name].has_key('cax'):
            cax = self.axes[axes_name]['cax']
            cax.clear()
            _cbar = mpl.colorbar.colorbar_factory(cax, img)
            #self.figure.colorbar(img, cax=cbar.ax)
        else:
            #cax, kw = mpl.colorbar.make_axes_gridspec(parent=ax, **cbargs)
            #cbar = self.figure.colorbar(img, cax=cax, **kw) #plt.colorbar(img, ax=ax, **cbargs)
            cax, kw = mpl.colorbar.make_axes_gridspec(ax, orientation='vertical', **cbargs)
            if color_bar:
                cbar = mpl.colorbar.colorbar_factory(cax, img, **kw)
                cax.tick_params(labelsize=15) 
            else:
                cax.set_axis_off()
            #cbar = self.figure.colorbar(img, ax=ax, use_gridspec=True, 
            #                    orientation='vertical', **cbargs)
            self.axes[axes_name]['cax'] = cax
        ax.set_axis_off()
        return ax
    

    
class PhyloTreeGraph(Grapher):
    '''
    Plot phylogenetic trees and represent the data in nodes with different layout styles. 
    '''
    
    rate_features = ['point_mut_rate', 'chromosomal_mut_rate', 'stretch_mut_rate', 
                    'sequence_mut_rate', 'chromosome_dup_rate',
                    'chromosome_del_rate', 'tandem_dup_rate', 'stretch_del_rate', 
                    'external_hgt_rate', 'internal_hgt_rate']
    
    node_layouts = [ 'metabolism', 'trophic_type', 'metabolic_with_lod' ] 
    
    def __init__(self, base_save_dir, name, attribute_dict, show=True, **kwargs):
        self.name = name
        self.range_dict = dict()
        self.figure = Figure((10,10))
        canvas = backend.FigureCanvas(self.figure)
        self.figure.set_canvas(canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')
        self.tree = None
        self.init_tree_style_dict() # NOTE: unordered ok
        super(PhyloTreeGraph, self).__init__(base_save_dir, name, attribute_dict=attribute_dict,
                                      show=show, **kwargs)
    
    def trophic_type_layout(self, node, trophic_type):
        
        colormap = {'autotroph':'green', 
                    'heterotroph':'red', 
                    'obl-mixotroph':'black', 
                    'fac-mixotroph':'blue'}
        ndst = NodeStyle()
        #check if the background of node should be recolored
        if node.up is not None:
            parent = node.up
            tr_type_parent = parent.trophic_type
            if node.trophic_type != tr_type_parent:
                ndst['bgcolor'] = colormap[node.trophic_type]
        else: #root node
            ndst['bgcolor'] = colormap[node.trophic_type]
        ndst['size'] = 0
        node.set_style(ndst)
        
    def mutation_rates_layout(self, node, mut_type):
        ndst = NodeStyle()
        color_map = self.attribute_mapper.color_maps['mutation_rates']
        try:
            mut_rate = getattr(node, mut_type)
        except AttributeError:
            print 'no attribute', mut_type, 'for node', node
        min_val, max_val = self.range_dict[mut_type]
        feature_range = max_val - min_val
        branch_color = mpl.colors.rgb2hex(color_map(mut_rate / (max_val-min_val))) if feature_range > 0 else 0
        ndst['hz_line_color'] = branch_color
        ndst['vt_line_color'] = branch_color
        ndst["vt_line_width"] = 2
        ndst["vt_line_width"] = 1
        ndst['size'] = 0
        node.set_style(ndst)

    def metabolic_with_lod_layout(self, node):
        self.metabolic_type_layout(node)
        ndst = node.img_style
        
        ndst["hz_line_width"] = 2
        ndst["vt_line_width"] = 2
        ndst["hz_line_type"] = 2
        ndst["vt_line_type"] = 2
        ndst['size'] = 0

        if hasattr(node, 'in_lod'):
            if node.in_lod:
                ndst["hz_line_type"] = 0
                ndst["vt_line_type"] = 0
        
        if hasattr(node, 'leaflabel'):
            label = TextFace(node.leaflabel)
            label.margin_top = 10
            label.margin_right = 10
            label.margin_left = 10
            label.margin_bottom = 10
            label.opacity = 1.0 # from 0 to 1
            label.background.color = "White"
            #label.inner_border.width = 0 # 1 pixel border
            #label.inner_border.type = 1  # dashed line
            label.border.width = 1
            label.fsize = 20
            add_face_to_node(label, node, column=0, position = "aligned")
            #ndst['']
        node.set_style(ndst)
                
    
    def metabolic_type_layout(self, node):    
        ndst = NodeStyle()
        #check if the background of node should be recolored
        color_map = self.attribute_mapper.color_maps['metabolic_type']
        if node.up is not None:
            parent = node.up
            mt_type_parent = parent.metabolic_type
            if node.metabolic_type != mt_type_parent:
                ndst['bgcolor'] = mpl.colors.rgb2hex(color_map(node.metabolic_type))
        else: #root node
            ndst['bgcolor'] = mpl.colors.rgb2hex(color_map(node.metabolic_type))
        ndst['size'] = 0
        node.set_style(ndst)
        
        #=======================================================================
        # gtp = node.gene_type_counts
        # total = float(gtp['genome']) if gtp['genome'] > 0 else 1.
        # prcts= ( 100 * gtp['tfs']/total, 
        #            100 * gtp['enzymes']/total,
        #            100 * gtp['eff-pumps']/total,
        #            100 * gtp['inf-pumps']/total )
        # colors = ('DarkOrchid','Crimson','SteelBlue','Chartreuse')
        # height = width = 2 * ( math.log(total,2) if total  else 0)
        # gene_type_pie_chart = PieChartFace(prcts, width, height, colors)
        # gene_type_pie_chart.opacity = 1.
        # gene_type_pie_chart.orientation = 0.
        # add_face_to_node(gene_type_pie_chart, node, column=0, position='branch-right')
        #=======================================================================
        
    def select_layout_fn(self, data_type):
        if data_type=='metabolism':
            return self.metabolic_type_layout
        elif data_type=='trophic_type':
            return lambda n: self.trophic_type_layout(n, data_type)
        elif data_type=='metabolic_with_lod':
            return self.metabolic_with_lod_layout
        elif data_type in self.rate_features:
            return lambda n: self.mutation_rates_layout(n, data_type)
        
    def make_tree_style(self, layout=None, mode='c', leaf_names=False, face_overlap=True, 
                        arc_span=360, scale=None, branch_lengths=False,
                        branch_vertical_margin=0):
        ts = TreeStyle()
        ts.mode = mode
        ts.show_leaf_name = leaf_names
        ts.allow_face_overlap = face_overlap
        ts.arc_span = arc_span
        ts.scale = scale
        ts.show_branch_length = branch_lengths
        ts.root_opening_factor = 1  # added by Bram ( default = 0.25 ; supposed to help scaling issues) 
        ts.branch_vertical_margin = branch_vertical_margin
        if layout is not None:
            ts.layout_fn = self.select_layout_fn(layout)
        return ts
        
    def init_tree_style_dict(self, layouts=None):
        if layouts is None:
            layouts = self.node_layouts + self.rate_features
        self.tree_style_dict = dict() # NOTE: unordered ok
        for layout in layouts:
            mode = 'r'
            scale = 0.1
            branch_vertical_margin = 1
            if layout in ['trophic_type', 'metabolism', 'metabolic_with_lod']:
                mode = 'c'
                scale = 0.05 # was None , changed by Bram
                branch_vertical_margin = 0
            self.tree_style_dict[layout] = self.make_tree_style(layout=layout, mode=mode,
                                                                scale=scale,
                                                                branch_vertical_margin=branch_vertical_margin)
        
    def update(self, tree):
        '''
        Set new ete_tree.
        '''
        self.tree = tree
        
    def compress_root_branch(self, root_branch_dist=20):
        if len(self.tree.children) == 1:
            child = self.tree.children[0]
            child.dist = root_branch_dist
       
    def update_figure(self, show=None, feature='metabolism', **kwargs):
        if show is None:
            show = self.show
        if show:
            mystyle = self.tree_style_dict[feature]
            mystyle.scale = 10
            self.tree.show(tree_style=mystyle, **kwargs)
        
    def save_fig(self, feature='metabolism', name=None, labels=[], suffix=".svg", rescale=None, dpi=10, **kwargs):
        '''
        Render tree with layout function depending on the selected feature for tree representation. 
        
        :param feature: feature selects for a specific layout function, determining node style 
        :param name: name for saving
        :param labels: labels to appear in save file name
        :param suffix: suffix of save file name
        '''
        
        my_tree_style=self.tree_style_dict[feature]        
        if name is None:
            name = self.name
        if rescale is not None:
            my_tree_style.scale = min(my_tree_style.scale * rescale, 0.3) # Maximum to prevent overscaling really low coalescent times.           
            print 'scale of tree set to ' + str(my_tree_style.scale)
            
        name = "_".join(name.split() + [feature] + map(str,labels) ) + suffix
        save_file = os.path.join(self.save_dir, name)
        self.tree.render(save_file, tree_style=my_tree_style, dpi=dpi, **kwargs)
        return save_file
        
    def write_to_file(self, name=None, labels=[], suffix='.nw', **kwargs):
        if name is None:
            name = self.name
        filename = "_".join(name.split()+ map(str,labels))
        self.tree.write(format=1, outfile=os.path.join(self.save_dir, filename+suffix), **kwargs)
        self.tree.write(format=1, features=[], 
                        outfile=os.path.join(self.save_dir, filename+'.nhx'), **kwargs)
    
    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['tree_style_dict']
        return odict
        
    def __setstate__(self, d):
        super(PhyloTreeGraph, self).__setstate__(d)
        self.init_tree_style_dict() 
    
class Graphs(Grapher):
    '''
    Produces static and online graphs of simulated data.
    '''
    
    def __init__(self, base_save_dir, name, utility_path, mol_class_dict, 
                 reactions_dict, population_markers, species_markers, show, clean=True, **kwargs):
        
        
        self.graphs = dict() # NOTE: unordered ok
        super(Graphs, self).__init__(base_save_dir, name, show=show, clean=clean, **kwargs)
        self.utility_path = utility_path
        self.init_attribute_mapper(mol_class_dict, reactions_dict, species_markers)
        self.init_time_course_graph(clean=clean)
        self.init_pop_stats(species_markers, reactions_dict, mol_class_dict, clean=clean)
        self.init_binding_network(clean=clean)
        self.init_metabolic_network(mol_class_dict, reactions_dict['conversion'], reactions_dict['import'], clean=clean)
        self.init_phylo_tree(clean=clean)
        self.init_grid_graphs(mol_class_dict, population_markers, clean=clean)
        self.init_genome_structure(clean=clean)
        self.init_scaling_dict()
        
    def change_save_location(self, base_save_dir=None , name=None, clean=False, create=True):
        if base_save_dir is not None:
            self.base_save_dir = base_save_dir
        if name is not None:
            self.name = name
        self.init_save_dir(clean=clean, create=create)
        for g in self.graphs.values():
            g.change_save_location(base_dir=self.save_dir, clean=clean, create=create)
        
    def init_scaling_dict(self):
        self.scaling_dict = {'production_max':0.,
                             'production_min':0.,
                             'production_rate_max':0.,
                             'production_rate_min':0.,
                             'death_rate_max': 0.,
                             'death_rate_min': 0.,
                             'cell_size_max':0.,
                             'cell_size_min':0.,
                             'crossfeed_max':0.,
                             'crossfeed_min':0.}
        
    def init_phylo_tree(self, show=None, **kwargs):
        if show is None:
            show = self.show
        pt = PhyloTreeGraph(self.save_dir, 'PhyloTree',
                       show=show, attribute_dict=self.attribute_mapper, **kwargs)
        self.add_multigraph(pt)
        
    def init_binding_network(self, show=None, **kwargs):              
        if show is None:
            show = self.show
        g = BindingNetwork(self.save_dir, 'GRN', 
                           show=show, attribute_dict=self.attribute_mapper, **kwargs)
        self.add_multigraph(g)
    
    def init_genome_structure(self, show=None, **kwargs):
        if show is None:
            show = self.show
        g = Genome(self.save_dir, 'Genome', attribute_dict=self.attribute_mapper, show=show, **kwargs)
        self.add_multigraph(g)
    
    def init_metabolic_network(self, metabolites, conversions, imports, show=None, **kwargs):    
        if show is None:
            show = self.show
        g = MetabolicNetwork(self.save_dir, 'Metabolome', metabolites, conversions, imports,
                             show=show, attribute_dict=self.attribute_mapper, **kwargs)
        self.add_multigraph(g)
    
    def line_colors(self, name, nr):
        colors = self.color_maps[name](np.linspace(0.5,1,nr))
        return colors
    
    def init_grid_graphs(self,  mol_class_dict, markers=[], 
                         nr_cols_markers=3, show=None, mol_classes_per_row=4, **kwargs):
        if show is None:
            show = self.show
        
        nr_cols_mols = max([len(mols) for mols in mol_class_dict.values()]) * mol_classes_per_row
        nr_rows_prod_death_size_cross = int(math.ceil(9./float(nr_cols_markers)))
        nr_rows_markers = int(math.ceil(len(markers)/float(nr_cols_markers)))
        nr_rows_mols = int(math.ceil(len(mol_class_dict) / float(mol_classes_per_row)))
        
        g = MultiGridGraph(self.save_dir, name='grid views', rows=max(nr_rows_markers+nr_rows_prod_death_size_cross, nr_rows_mols), 
                           cols=nr_cols_mols+nr_cols_markers, 
                           attribute_dict=self.attribute_mapper, show=show, **kwargs)
        
        index_iter = it.product(xrange(nr_rows_mols), xrange(nr_cols_mols))

        for mols in mol_class_dict.values():
            for _, m in it.izip_longest(range(nr_cols_mols /mol_classes_per_row ), mols):
                r,c = index_iter.next()
                if m is not None:
                    ax = g.add_axis(str(m), pos=GridPos(row=r, col=c), rows=1, cols=1)
                    ax.set_title(str(m))
      
        index_iter = it.product(xrange(nr_rows_markers+nr_rows_prod_death_size_cross), xrange(nr_cols_markers))
        for m in markers:
            r,c = index_iter.next()
            ax = g.add_axis(m, pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
            ax.set_title(m)
            print 'added axis', m, 'to graph', g.name
        while True:
            r,c = index_iter.next()
            if c == 0:
                break    
        ax = g.add_axis('production', pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
        ax.set_title('production')
        r,c = index_iter.next()
        ax = g.add_axis('production rate', pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
        ax.set_title('production rate')
        r,c = index_iter.next()
        ax = g.add_axis('death', pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
        ax.set_title('death rate')
        r,c = index_iter.next()
        ax = g.add_axis('crossfeeding', pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
        ax.set_title('crossfeeding')
        r,c = index_iter.next()
        ax = g.add_axis('exploitive crossfeeding', pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
        ax.set_title('exploitive crossfeeding')
        r,c = index_iter.next()
        ax = g.add_axis('strict crossfeeding', pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
        ax.set_title('strict crossfeeding')
        
        r,c = index_iter.next()
        ax = g.add_axis('cell size', pos=GridPos(row=r, col=c+nr_cols_mols), rows=1, cols=1)
        ax.set_title('cell size')
        
        self.add_multigraph(g)
        g.tight_layout(rect=(0, 0, 1.0, 0.95))
        return g
            
    def init_pop_stats(self, species_markers, reactions_dict, mol_class_dict, show=None, **kwargs):
        if show is None:
            show = self.show
        g = MultiGraph(self.save_dir, 'population stats', 4,4, row_heigth=4, col_width=6, 
                       show=show, attribute_dict=self.attribute_mapper, **kwargs)
        ax = g.add_axis('genome size', GridPos(row=0, col=0), 1, 1, nr_lines=11, line_styles=[''], 
                   markers=['*'], colors=['black'], marker_edge_widths=[0], marker_sizes=[.5])
        g.customize_lines(ax.get_lines()[-1:], line_styles=['-'], colors=['red'], markers=[''])
        ax = g.add_axis('chromosome counts', GridPos(row=1, col=0), 1, 1, nr_lines=11, line_styles=[''], 
                   markers=['*'], colors=['black'], marker_edge_widths=[0], marker_sizes=[.5])
        g.customize_lines(ax.get_lines()[-1:],line_styles=['-'], colors=['red'], markers=[''])
        ax = g.add_axis('population size', GridPos(row=2, col=0), 1, 1, nr_lines=1, line_styles=['-'], markers=[''], auto_scale=False)
        ax.set_ylim((0,len(species_markers)))
        ax = g.add_axis('production rate', GridPos(row=0, col=1), 1, 1, nr_lines=3, colors=['blue','blue','red'])
        g.customize_lines(ax.get_lines()[1:], line_styles=[''], colors=[])
        ax = g.add_axis('production value', GridPos(row=1, col=1), 1, 1, nr_lines=3)
        g.customize_lines(ax.get_lines()[1:2], line_styles=[''])
        g.add_axis('offspring', GridPos(row=2, col=1), 1, 1, nr_lines=3)
        g.add_axis('death rate', GridPos(row=3, col=1), 1, 1, nr_lines=3)
        g.add_axis('generation age', GridPos(row=0, col=3), 1, 1, nr_lines=3)
        g.add_axis('coalescent time', GridPos(row=1, col=3), 1, 1, nr_lines=1, line_styles=['-'], markers=[''])
        g.add_axis('crossfeeding', GridPos(row=2, col=3), 1, 1, nr_lines=4, colors=['blue', 'blue', 'red','green'])
        ax = g.add_axis('metabolic types', GridPos(row=0, col=2), 1, 1, nr_lines=6, auto_scale=False)
        ax.set_ylim((0,1.))
        g.customize_lines(ax.get_lines()[:3], colors=['blue'])
        g.customize_lines(ax.get_lines()[-3:], colors=['red'])
        ax = g.add_axis('transport types', GridPos(row=1, col=2), 1, 1, nr_lines=6, auto_scale=False)
        ax.set_ylim((0,1.))
        g.customize_lines(ax.get_lines()[:3], colors=['blue'])
        g.customize_lines(ax.get_lines()[-3:], colors=['red'])
        ax = g.add_axis('metabolic capacities', GridPos(row=2, col=2), 1, 1, nr_lines=4,
                        colors=['blue','red','blue','red'], 
                        line_styles=['-', '-', '-.', '-.'])
        cm = self.attribute_mapper.color_maps['lineage']
        g.add_axis('species', GridPos(row=3, col=0), 1, 1, nr_lines=species_markers, 
                   colors=cm(species_markers), line_styles=['-'])
        cm = self.attribute_mapper.color_maps['metabolic_type']
        g.add_axis('metabolic type counts', GridPos(row=3, col=1), 1, 1, nr_lines=species_markers, 
                   colors=cm(species_markers), line_styles=['-'])
        
        conversions = zip(list(reactions_dict['conversion']), it.repeat(False)) 
        imports = zip( list( reactions_dict['import']), it.repeat(False))
        exports = zip( list( reactions_dict['import']), it.repeat(True))
        reactions = conversions + imports + exports
        ax = g.add_axis('reactions', GridPos(row=3, col=2), 1, 1, nr_lines=reactions,
                        colors=[self.attribute_mapper.color_reaction(r[0]) for r in reactions], line_styles=['-'], markers=[''])
        g.customize_lines(ax.get_lines()[-len(exports):], line_styles=['--'], colors=[],
                          marker_sizes=[], marker_edge_widths=[], markers=[])
        g.customize_lines(ax.get_lines()[:len(conversions)], line_styles=[':'], colors=[],
                          marker_sizes=[], marker_edge_widths=[], markers=[])
        ordered_mols = sorted(util.flatten(mol_class_dict.values()), key=lambda x:x.name)
        nr_lines = len(ordered_mols)
        ax = g.add_axis('external resource evo', 
                                                 GridPos(row=3, col=3), 1, 1, nr_lines=nr_lines)
        g.customize_lines(ax.get_lines(), colors=[ self.attribute_mapper.color_mol(mol) for mol in ordered_mols],
                          line_styles = [ '--' if mol.is_building_block else '-' for mol in ordered_mols ],
                          markers=['' for _ in ordered_mols]
                          )
        ax.set_yscale('log')
        self.add_multigraph(g)
        g.tight_layout()
        return g
        
    def add_multigraph(self, graph):
        self.graphs[graph.name] = graph
        
    def init_time_course_graph(self, show=None, **kwargs):
        if show is None:
            show = self.show
        g = MultiGraph(self.save_dir, 'time course', 3, 2, row_heigth=3, col_width=6,
                       show=show, attribute_dict=self.attribute_mapper, **kwargs)
        _ax = g.add_axis('internal resource', GridPos(row=0, col=0), 1, 1)
        #g.add_axis('external resource', (0,0), 1, 1, sharey=ax)
        ax = g.add_axis('protein', GridPos(row=1, col=0), 1, 1)
        ax.set_ylim( (0.01,20) )
        
        ax = g.add_axis('cell size', GridPos(row=0, col=1), 1, 1)
        ax = g.add_axis('toxicity', GridPos(row=1, col=1), 1, 1)
        ax = g.add_axis('production', GridPos(row=2, col=1), 1, 1)
        g.tight_layout()
        self.add_multigraph(g)
        return g
        
    def add_pop_stats_data(self, time, most_fecundant_death_rate, most_fecundant_production, 
                           data_store, high_freq_cutoff=10):
        
        time_point = np.array((time,))
        graph = self.graphs['population stats']
        data_dict = data_store['population size'].get_data_point(time)
        pop_size = data_dict['value']
        graph.append_to_axes('population size', time_point, np.array((pop_size,)))
        data_dict = data_store['genome sizes'].get_data_point(time)
        genome_avrg_size = data_dict['avrg']
        genome_sizes_freq_sorted = np.array([ data_dict['most_freq'+str(i)] for i in range(high_freq_cutoff)])
        genome_sizes_freq_sorted[np.isnan(genome_sizes_freq_sorted)] = -1.
        graph.append_to_axes('genome size', time_point,
                             np.hstack((genome_sizes_freq_sorted,
                                        genome_avrg_size )))
        data_dict = data_store['chromosome counts'].get_data_point(time)
        chromosome_avrg_count = data_dict['avrg']
        chromosome_counts_freq_sorted = np.array([ data_dict['most_freq'+str(i)] for i in range(high_freq_cutoff)])
        chromosome_counts_freq_sorted[np.isnan(chromosome_counts_freq_sorted)] = -1
        graph.append_to_axes('chromosome counts', time_point, 
                             np.hstack((chromosome_counts_freq_sorted,
                                        chromosome_avrg_count)))
        data_dict = data_store['pos production'].get_data_point(time) 
        production_rate_avrg = data_dict['avrg']
        production_rate_max = data_dict['max']
        if production_rate_max > self.scaling_dict['production_rate_max']:
            self.scaling_dict['production_rate_max'] = production_rate_max
            
        production_rate_min = data_dict['min']
        if production_rate_min < self.scaling_dict['production_rate_min']:
            self.scaling_dict['production_rate_min'] = production_rate_min
        graph.append_to_axes('production rate', time_point, np.hstack((production_rate_avrg,
                                                                  production_rate_max,
                                                                  most_fecundant_production)))
 
        data_dict = data_store['production values'].get_data_point(time)
        production_avrg = data_dict['avrg']        
        production_max = data_dict['max']
        if production_max > self.scaling_dict['production_max']:
            self.scaling_dict['production_max'] = production_max
        production_min = data_dict['min']
        if production_min < self.scaling_dict['production_min']:
            self.scaling_dict['production_min'] = production_min

        graph.append_to_axes('production value', time_point, np.hstack((production_avrg,
                                                                  production_max,
                                                                  most_fecundant_production)))
        
        data_dict = data_store['death rates'].get_data_point(time)
        death_rate_avrg = data_dict['avrg']
        death_rate_max = data_dict['max']
        if death_rate_max > self.scaling_dict['death_rate_max']:
            self.scaling_dict['death_rate_max'] = death_rate_max
        death_rate_min = data_dict['min']
        if death_rate_min < self.scaling_dict['death_rate_min']:
            self.scaling_dict['death_rate_min'] = death_rate_min
        graph.append_to_axes('death rate', time_point, np.hstack((death_rate_avrg, 
                                                                  death_rate_max,
                                                                  most_fecundant_death_rate)) )
        data_dict = data_store['offspring counts'].get_data_point(time)
        offspring_avrg = data_dict['avrg']
        offspring_max = data_dict['max']
        graph.append_to_axes('offspring', time_point, np.hstack((offspring_avrg, 
                                                                 offspring_max)) )
        data_dict = data_store['iterages'].get_data_point(time)
        generation_age_avrg = data_dict['avrg']
        generation_age_max = data_dict['max']
        graph.append_to_axes('generation age', time_point, np.hstack((generation_age_avrg,
                                                                      generation_age_max)))
        data_dict = data_store['metabolic types'].get_data_point(time)
        graph.append_to_axes('metabolic types', time_point, np.hstack((data_dict['producer_avrg_diff'], data_dict['producer_max_diff'],
                                                                       data_dict['producer_min_diff'],
                                                                       data_dict['consumer_avrg_diff'], data_dict['consumer_max_diff'],
                                                                       data_dict['consumer_min_diff'])))
        
        graph.append_to_axes('transport types', time_point, np.hstack((data_dict['import_avrg_diff'], data_dict['import_max_diff'],
                                                                       data_dict['import_min_diff'],
                                                                       data_dict['export_avrg_diff'], data_dict['export_max_diff'],
                                                                       data_dict['export_min_diff'])))
        graph.append_to_axes('metabolic capacities', time_point, np.hstack((data_dict['producer_sum'], 
                                                                            data_dict['consumer_sum'],
                                                                            data_dict['import_sum'],
                                                                            data_dict['export_sum'] )))
        data_dict = data_store['species counts'].get_data_point(time)
        #for k in data_dict:
        #    data_dict[k] /= float(pop_size)
        graph.append_to_lines('species', time_point, data_dict)
        data_dict = data_store['reaction counts'].get_data_point(time)
        #for k in data_dict:
        #    data_dict[k] /= float(pop_size)
        graph.append_to_lines('reactions', time_point, data_dict)
        
        data_dict = data_store['coalescent time'].get_data_point(time)
        graph.append_to_axes('coalescent time', time_point, np.array((data_dict['value'], )))
        
        data_dict = data_store['crossfeeding'].get_data_point(time)
        crossfeeding_avrg = data_dict['avrg']
        crossfeeding_max = data_dict['max']
        if crossfeeding_max > self.scaling_dict['crossfeed_max']:
            self.scaling_dict['crossfeed_max'] = crossfeeding_max
        crossfeeding_min = data_dict['min']
        if crossfeeding_min < self.scaling_dict['crossfeed_min']:
            self.scaling_dict['crossfeed_min'] = crossfeeding_min
        data_dict = data_store['strict crossfeeding'].get_data_point(time)
        strict_crossfeeding_avrg = data_dict['avrg']
        data_dict = data_store['exploitive crossfeeding'].get_data_point(time)
        exploitive_crossfeeding_avrg = data_dict['avrg']
        graph.append_to_axes('crossfeeding', time_point, np.hstack((crossfeeding_avrg,
                                                                    crossfeeding_max, 
                                                                    strict_crossfeeding_avrg,
                                                                    exploitive_crossfeeding_avrg)))
        
        data_dict = data_store['cell sizes'].get_data_point(time)
        cell_size_min = data_dict['min']
        cell_size_max = data_dict['max']
        if cell_size_max > self.scaling_dict['cell_size_max']:
            self.scaling_dict['cell_size_max'] = cell_size_max
        if cell_size_min < self.scaling_dict['cell_size_min']:
            self.scaling_dict['cell_size_min'] = cell_size_min
        
        
    def add_grid_graphs_data(self, time_point, pop_grid_data_dict, small_mol_names, data_store,
                            scaling_dict_updates, markers_range_dict):
        self.scaling_dict.update(scaling_dict_updates)
            
        graph = self.graphs['grid views']
        for small_mol_name in small_mol_names:
            graph.append_to_axes(small_mol_name, time_point, data_store['grid concentration '+small_mol_name].get_data_point(time_point))
        for marker, data in pop_grid_data_dict.items():
            graph.append_to_axes(marker, time_point, data)
            graph.set_data_range(marker, markers_range_dict[marker])
        graph.append_to_axes('death', time_point, data_store['grid death rates'].get_data_point(time_point))
        graph.set_data_range('death', (self.scaling_dict['death_rate_min'],self.scaling_dict['death_rate_max']))
        graph.append_to_axes('production', time_point, data_store['grid production values'].get_data_point(time_point))
        graph.set_data_range('production', (self.scaling_dict['production_min'],self.scaling_dict['production_max']))
        graph.append_to_axes('production rate', time_point, data_store['grid production rates'].get_data_point(time_point))
        graph.set_data_range('production rate', (self.scaling_dict['production_rate_min'],self.scaling_dict['production_rate_max']))
        graph.append_to_axes('cell size', time_point, data_store['grid cell sizes'].get_data_point(time_point))
        graph.set_data_range('cell size', (self.scaling_dict['cell_size_min'],self.scaling_dict['cell_size_max']))
        graph.append_to_axes('crossfeeding', time_point, data_store['neighbor crossfeeding'].get_data_point(time_point))
        graph.set_data_range('crossfeeding', (self.scaling_dict['crossfeed_min'],self.scaling_dict['crossfeed_max']))
        graph.append_to_axes('exploitive crossfeeding', time_point, data_store['exploitive neighbor crossfeeding'].get_data_point(time_point))
        graph.set_data_range('exploitive crossfeeding', (self.scaling_dict['crossfeed_min'],self.scaling_dict['crossfeed_max']))
        graph.append_to_axes('strict crossfeeding', time_point, data_store['strict neighbor crossfeeding'].get_data_point(time_point))
        graph.set_data_range('strict crossfeeding', (self.scaling_dict['crossfeed_min'],self.scaling_dict['crossfeed_max']))
        
    def plot_mol_class_data(self, ax, mol_tc_dict, **plot_params):
        title = ax.get_title()
        ax.clear()
        ax.set_title(title)
        for mol, tc in sorted(list(mol_tc_dict.items()),key=lambda x: x[0].name):
            line_style = '-'
            if mol.is_building_block:
                line_style = '--'
            ax.plot(tc[0,:], tc[1,:], 
                    color=self.attribute_mapper.color_mol(mol), 
                    linestyle=line_style, 
                    label=str(mol),
                    **plot_params)
            #ax.set_yscale('log')
        ax.legend(fontsize=6, labelspacing=0.1)
        return ax
    
    def plot_prot_data(self, ax, prot_pert_type_tc_dict, **plot_params):
        title = ax.get_title()
        ax.clear()
        ax.set_title(title)
        for _type, prot_tc_dict in prot_pert_type_tc_dict.items():
            line_style = self.attribute_mapper.protein_type_line_style(_type)
            for prot, tc in sorted(list(prot_tc_dict.items()),key=lambda x: str(x[0].id)):
                color = self.attribute_mapper.color_protein(prot)
                if _type in ['pumps', 'enzymes']:
                    label = str(prot.reaction)
                else:
                    label = prot.ligand_class.name
                assert label != None
                ax.plot(tc[0,:],tc[1,:], 
                        color=color, 
                        linestyle=line_style, 
                        label=label,
                        **plot_params)
                #ax.set_yscale('log')
            
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                labels_dict = dict( zip(labels, handles) ) 
                labels, handles = zip(* sorted(labels_dict.items()))
            ax.legend(handles, labels,fontsize=6, labelspacing=0.1)
        return ax

    def add_mol_evo_time_course_data(self, time_point, ext_res_conc_dict): #, halfway_ext_res_conc_dict):
        g = self.graphs['population stats']
        time_point = np.array((time_point,))
        sorted_mol_end_conc = np.array([ tc for _, tc in sorted(ext_res_conc_dict.items(), key=lambda x:x[0].name) ])       
        g.append_to_axes('external resource evo', time_point, 
                                                  np.array(sorted_mol_end_conc))
        #=======================================================================
        # sorted_mol_end_conc = np.array([ tc for _, tc in sorted(halfway_ext_res_conc_dict.items(), key=lambda x:x[0].name) ])
        # self.graphs['time course'].append_to_axes('external resource evo halfway', 
        #                                           time_point, 
        #                                           np.array(sorted_mol_end_conc))
        #=======================================================================

    @util.subprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])
    def plot_phylo_tree(self, pop, env, max_depth, 
                        labels=[], save=True, write=True, suffix='.svg'):
        pop.update_ete_tree()
        phylo_tree = pop.phylo_tree
        if phylo_tree.ete_tree is None:
            print 'No ete tree'
            return
        t = self.graphs['PhyloTree']
        rate_features = t.rate_features
        for i, (root_id, ete_tree_struct) in enumerate(pop.phylo_tree.ete_trees.items()):
            _labels = labels[:]
            _labels.append(root_id.split('_')[0])
            t.update(ete_tree_struct.tree)
            if write:
                t.write_to_file(labels=_labels)
            
            phylo_tree.ete_prune_external(ete_tree_struct, max_depth)
            features=[ f.replace('rate','count') for f in rate_features ]
            phylo_tree.ete_annotate_tree(ete_tree_struct=ete_tree_struct, features=features)
            phylo_tree.ete_cummulative_features(ete_tree_struct=ete_tree_struct, features=features)
            phylo_tree.ete_prune_internal(ete_tree_struct)
            max_rate_dict = phylo_tree.ete_rate_features(ete_tree_struct=ete_tree_struct, features=features)
            value_range_dict = dict( (feature, (0, max_rate)) for feature, max_rate in max_rate_dict.items() )
            t.range_dict.update(value_range_dict)
            
            func_features={'metabolic_type':pop.metabolic_type_color,
                           'trophic_type': lambda c: c.trophic_type(env)}
            phylo_tree.ete_annotate_tree(ete_tree_struct, func_features=func_features)

            t.compress_root_branch()

            for feature in rate_features + ['metabolism','trophic_type']:
                if save:
                    save_file = t.save_fig(labels=_labels, feature=feature, suffix=suffix)
                    name_no_label = "_".join(t.name.split() + [feature] )
                    if i > 0:
                        name_no_label += '.{}'.format(i)
                    save_file_no_label = os.path.join(t.save_dir, name_no_label + suffix )
                    shutil.copy2(save_file, save_file_no_label)
                    #t.save_fig(suffix=suffix, feature=feature)
        return 'PHYLO TREE DONE'
    
    @util.queuedprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])       
    #@util.subprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])
    def plot_grid_graphs(self, small_mol_names, marker_names, labels=[], with_labels_suffix=['.png'],
                         no_labels_suffix=['.png'], video=None, save=True, write=True, save_no_labels=False, 
                         title='' ):
        g = self.graphs['grid views']
        for small_mol_name in small_mol_names:
            g.plot_in_axes(small_mol_name, cm_name='resource_conc')
        for marker_name in marker_names:
            g.plot_in_axes(marker_name, cm_name=marker_name,color_bar=False)
        g.plot_in_axes('production', cm_name='cell_vals',color_bar=True)
        g.plot_in_axes('death', cm_name='cell_vals', color_bar=True)
        g.plot_in_axes('production rate', cm_name='cell_vals', color_bar=True)
        g.plot_in_axes('cell size', cm_name='cell_vals', color_bar=True)
        g.plot_in_axes('crossfeeding', cm_name='cell_vals', color_bar=True )
        g.plot_in_axes('strict crossfeeding', cm_name='cell_vals', color_bar=True )
        g.plot_in_axes('exploitive crossfeeding', cm_name='cell_vals', color_bar=True )
        g.update_figure()
        if save:
            saved = []
            for suf in with_labels_suffix:
                copy_labels = None
                if save_no_labels and suf in no_labels_suffix:
                    copy_labels = []
                saved += g.save_fig(labels=labels, suffix=suf, title=title, copy_labels=copy_labels)
                
            if save_no_labels:
                for suf in set(no_labels_suffix) - set(with_labels_suffix):
                    saved += g.save_fig(suffix=suf, title=title)
            if video is not None:
                for save_file in saved:
                    if os.path.basename(save_file) ==  'grid_views.png':
                        g.save_video(video, frame=save_file)
            else:
                print 'skip ffmpeg video step (no suitable ffmpeg found)'
    
    @util.subprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])              
    def plot_genome_structure(self, cell, labels=[], video=None):
        g = self.graphs['Genome']
        g.plot_genome_structure(cell, labels, video)
    
    @util.queuedprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])
    #@util.subprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])  
    def plot_pop_stats(self, save=True):
        g = self.graphs['population stats'] 
        g.update_figure()
        if save:
            g.save_fig(suffix='.png')
            g.save_fig()
    
    @util.queuedprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])
    #@util.subprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])
    def plot_time_course(self, 
                         int_res_time_course_dict, 
                         ext_res_time_course_dict, 
                         protein_per_type_time_course_dict, 
                         cell_size_dat,
                         toxicity_dat,
                         production_dat,
                         labels=[], with_labels_suffix='.png',
                         no_labels_suffix='.svg', save=True, save_no_labels=False):
        g = self.graphs['time course']
        self.plot_mol_class_data(g['internal resource'], int_res_time_course_dict)
        try:
            self.plot_mol_class_data(g['external resource'], ext_res_time_course_dict)
        except KeyError:
            pass
        self.plot_prot_data(g['protein'], protein_per_type_time_course_dict)
        g['protein'].set_ylim((0.01,500))
        try:
            ax = g['cell size']
            ax.clear() 
            ax.set_title('cell size')
            ax.plot(cell_size_dat[0,:],cell_size_dat[1,:])
        except KeyError:
            pass
        try:
            ax = g['toxicity'] 
            ax.clear()
            ax.set_title('toxicity')
            ax.plot(toxicity_dat[0,:],toxicity_dat[1,:])
        except KeyError:
            pass
        try:
            ax = g['production']
            ax.clear() 
            ax.set_title('production')
            ax.plot(production_dat[0,:],production_dat[1,:])
        except KeyError:
            pass
        
        g.update_figure()
        if save:
            g.save_fig(labels=labels, suffix=with_labels_suffix)
            if save_no_labels:
                g.save_fig(suffix=no_labels_suffix)
    
        
    @util.queuedprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])    
    #@util.subprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])
    def plot_binding_network(self, cell, 
                             fig_ext_label_dict,
                             text_ext_label_dict,
                             edge_effects=['effect', 'effect_apo'],
                             prog=None, 
                             save=True, 
                             video=None, 
                             write=True, 
                             title='',
                             video_frame_name='GRN_dot.png'):
        '''
        :param cell: Who to plot
        :param prog: (???)
        :param save: Save the figure Y/N
        :param write: Save the network file (gml, dot, json, etc.)

        Nodes:
        Pumping enzymes are BLUE squares (ip = importing pump, e-p = exporting pump)
        Generic enzymes are BLUE / TURQUOISE circles  
        Specific enzymes are GREEN / YELLOW / RED circles
        TFs are BROWN diamonds
        Thick borders indicates self-binding
        
        Node-labels:        
        Labels: 
        Metabolites with brackets are building blocks
        Metabolites with asterisks are energy carriers
        
        Edges:
        Width shows the basal level of transcription for the TF
        Colours distinquish inhibiting (blue) vs activating (red) effects. Intermediates are white-ish. 
        
        !! Note: still needs the ReST references worked out !!
        '''
        grn = self.graphs['GRN']
        grn.init_network(cell)
        grn.layout_network_positions(prog=prog)
        for effect in edge_effects:
            grn.redraw_network(self_marker=True, edge_effect=effect)
            grn.update_figure()
            if save:
                saved = []
                for ext, label_sets in fig_ext_label_dict.items():
                    fn = grn.save_fig2(ext,title=title)
                    for label_set in label_sets:
                        label_set = label_set[:]
                        if effect == 'effect_apo':
                            label_set.append('apo')
                        label_set.append(prog)
                        save_file = "_".join([fn] + map(str,label_set)) + '.' + ext
                        shutil.copy2(fn, save_file)
                        saved.append(save_file)
                    os.remove(fn)
    
                if video is not None:
                    for save_file in saved:
                        if os.path.basename(save_file) ==  video_frame_name:
                            grn.save_video(video, frame=save_file)
        
            if write:
                for ext, label_sets in text_ext_label_dict.items():
                    for label_set in label_sets:
                        if effect == 'effect_apo':
                            label_set.append('apo')
                        grn.write_to_file(labels=label_set, suffix=ext)

        grn.clear_graph()
        
    @util.queuedprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])   
    #@util.subprocessor(as_subprocess=util.ugly_globals['graphs_as_subprocesses'])
    def plot_metabolic_network(self, 
                               fig_ext_label_dict,
                               text_ext_label_dict,
                               reactions_dict=None,  
                               self_marker=None, 
                               building_blocks=None,
                               save=True, 
                               video=None, 
                               write=True, 
                               title='',
                               video_frame_name='Metabolome.png',
                               ):
        mn = self.graphs['Metabolome']
        mn.redraw_network(reactions_dict=reactions_dict, 
                          building_blocks=building_blocks, 
                          self_marker=self_marker)
        mn.update_figure()
        
        if save:
            saved = []
            for ext, label_sets in fig_ext_label_dict.items():
                fn = mn.save_fig2(ext,title=title)
                for label_set in label_sets:
                    label_set = label_set[:]
                    save_file =  "_".join( [fn] + map(str,label_set)) + '.' + ext
                    shutil.copy2(fn, save_file)
                    saved.append(save_file)
                os.remove(fn)

            if video is not None:
                for save_file in saved:
                    if os.path.basename(save_file) ==  video_frame_name:
                        mn.save_video(video, frame=save_file)
    
        if write:
            for ext, label_sets in text_ext_label_dict.items():
                for label_set in label_sets:
                    mn.write_to_file(labels=label_set, suffix=ext)        
            
    def plot_grid_concentrations(self, dat):
        pass

    
    def __getitem__(self,key):
        return self.graphs[key]
