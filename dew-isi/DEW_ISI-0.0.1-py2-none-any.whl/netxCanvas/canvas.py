from math import atan2, pi, cos, sin
import collections
import sys
import pickle
try:
    # Python 3
    import tkinter as tk
    import tkinter.messagebox as tkm
    import tkinter.simpledialog as tkd
except ImportError:
    # Python 2
    import Tkinter as tk
    import tkMessageBox as tkm
    import tkSimpleDialog as tkd

import networkx as nx

from netxCanvas.style import NodeClass, EdgeClass

def flatten(l):
    try:
        bs = basestring
    except NameError:
        bs = str
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, bs):
            for sub in flatten(el):
                yield sub
        else:
            yield el

class netxCanvas():
    def __init__(self, graph, master=None, style=None, width=0, height=0, xoffset=0, yoffset=0, **kwargs):
        self.canvas = GraphCanvas(graph, master=master, width=width, height=height, NodeClass=style, **kwargs)
        self.canvas.grid(row=0, column=0, sticky='NESW')
        
class GraphCanvas(tk.Canvas):
    xoffset = 0
    yoffset = 0
        
    def __init__(self, graph, master=None, width=0, height=0, xoffset=0, yoffset=0, **kwargs):
        self.G = graph
        self.dispG = nx.MultiGraph()
        self.initkwargs = kwargs
        self.master = master
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.width = int(width)
        self.height = int(height)
                
        self._drag_data = {'x': 0, 'y': 0, 'item': None}
        self._pan_data  = (None, None)
        
        self._node_filters = []
        
        home_node = kwargs.pop('home_node', None)
        if home_node:
            print("HOME NODE IS: %s" % str(home_node))
            levels = kwargs.pop('levels', 1)
            graph = self._neighbors(home_node, levels=levels, graph=graph)
        else:
            home_node = 0
        
        self._NodeClass = kwargs.pop('NodeClass', NodeClass)
        self._EdgeClass = kwargs.pop('EdgeClass', EdgeClass)
        
        if width != 0 and height != 0:
            print("Making canvas size: %dx%d" % (width, height))
            tk.Canvas.__init__(self, master=master, width=width, height=height, **kwargs)
            #tk.Canvas.__init__(self, master=master, **kwargs)
        else:
            print("Given %d and %d for width and height" % (width, height))
            tk.Canvas.__init__(self, master=master, **kwargs)
            
        # Are our coordinates off?
        self.x0 = self.master.winfo_rootx()
        self.y0 = self.winfo_rooty()
        #print("(0,0) at (%d,%d)" % (self.x0, self.y0))
        
        self.config(bg='white')

        self._plot_graph(graph, home_node=home_node)
        self.center_on_node(home_node or graph.nodes()[0])
        
        # Add bindings for clicking.
        self.tag_bind('node', '<ButtonPress-1>', self.onNodeButtonPress)
        self.tag_bind('node', '<ButtonRelease-1>', self.onNodeButtonRelease)
        self.tag_bind('node', '<B1-Motion>', self.onNodeMotion)
        self.tag_bind('edge', '<Button-1>', self.onEdgeClick)
        self.tag_bind('edge', '<Button-3>', self.onEdgeRightClick)
        self.bind('<ButtonPress-1>', self.onPanStart)
        self.bind('<ButtonRelease-1>', self.onPanEnd)
        self.bind('<B1-Motion>', self.onPanMotion)
        self.bind_all('<MouseWheel>', self.onZoom)
        #self.bind("<Configure>", self.configure)
        
    def configure(self, event):
        print("Configure called.")
        self.delete("all")
        w, h = event.width, event.height
        graph = self.G
        home_node = self.initkwargs.pop('home_node', None)
        if home_node:
            levels = self.initkwargs.pop('levels', 1)
            graph = self._neighbors(home_node, levels=levels, graph=graph)
        self._plot_graph(graph)
        self.center_on_node(home_node or graph.nodes()[0])
        

    def _draw_edge(self, u, v):
        try:
            fm_disp = self._find_disp_node(u)
            to_disp = self._find_disp_node(v)
        except:
            return
        
        directed = False
        type = None
        if isinstance(self.G, nx.MultiDiGraph):
            directed = True
            type = 'MULTIDI'
            edges = self.G.edges[u, v]
        elif isinstance(self.G, nx.MultiGraph):
            edges = self.G.edges[u,v]
            type = 'MULTI'
        elif isinstance(self.G, nx.Graph):
            type = 'GRAPH'
            edges = {0: self.G.edges[u,v]}
        else:
            print("Warning, unsupported graph type. Use MultiDiGraph or MultiGraph")
            exit()
        if len(edges) == 1:
            m = 0
        else:
            m = 50
        
        for key, data in edges.items():
            estyle = self._EdgeClass(data)
            if type == 'MULTI':
                G_id = (u, v, key)
            elif type == 'GRAPH':
                G_id = (u, v)
            else:
                G_id = (u, v)
            
            self.dispG.add_edge(fm_disp, to_disp, key, G_id=G_id, dispG_fm=fm_disp, token=estyle, m=m)
            
            x1,y1 = self._node_center(fm_disp)
            x2,y2 = self._node_center(to_disp)
            xa,ya = self._spline_center(x1,y1,x2,y2,m)
            
            estyle.render(host_canvas=self, coords=(x1,y1,xa,ya,x2,y2), directed=directed)
            
            if m>0:
                m = -m
            else:
                m = -(m+m)
            
    def _draw_node(self, coord, data_node):
        (x,y) = coord
        #if len(self.G) == 1:
        #    return 0
        #print("Pulling data on node %d" % data_node)
        data = self.G.nodes(data=True)[data_node]
        
        for filter_lambda in self._node_filters:
            try:
                draw_flag = eval(filter_lambda, {'u':data_node, 'd':data})
            except Exception as e:
                self._show_filter_error(filter_lambda, e)
                return
            
            if draw_flag == False:
                return
        
        nstyle = self._NodeClass(self, data, data_node)
        id = self.create_window(x,y,window=nstyle, anchor=tk.CENTER, tags='node')
        attr = {'G_id': data_node, 'token_id': id, 'token':nstyle}
        self.dispG.add_node(id,G_id=data_node, token_id=id, token=nstyle)
        return id
    
    def _get_id(self, event, tag='node'):
        for item in self.find_overlapping(event.x-self.xoffset-5, event.y-self.yoffset-5, event.x-self.xoffset+5, event.y-self.yoffset+5):
            if tag in self.gettags(item):
                return item
        #print("Found no matching item. (Yoffset is: %d)" % self.yoffset)
        return None
        #raise Exception('No Item Found')
    
    def _node_center(self, item_id):
        b = self.bbox(item_id)
        return((b[0]+b[2])/2, (b[1]+b[3])/2)
        
    def _spline_center(self, x1, y1, x2, y2, mul):
        coord1 = [x1, y1]
        coord2 = [x2, y2]
        a = (coord2[0] + coord1[0])/2
        b = (coord2[1] + coord1[1])/2
        beta = (pi/2) - atan2((coord2[1]-coord2[1]), (coord2[0]-coord1[0]))
        
        xa = a-mul*cos(beta)
        ya = b + mul*sin(beta)
        return(xa, ya)
    
    def _neighbors(self, node, levels=1, graph=None):
        if graph is None:
            graph = self.G
    
        if not isinstance(node, (list, tuple, set)):
            node = [node,]
        
        neighbors = set(node)
        blocks = [[n,] for n in node]
        for i in range(levels):
            for n in neighbors:
                new_neighbors = set(graph.neighbors(n)) - neighbors
                blocks.append(new_neighbors)
                neighbors = neighbors.union(new_neighbors)
        G = graph.subgraph(neighbors)
        
        if len(blocks) > 1:
            non_blocked = set(self.G.nodes()) - neighbors
            non_blocked = [[a,] for a in non_blocked]
            
            partitions = blocks + non_blocked
            
            #B = nx.blockmodel(graph, partitions)
            B = nx.quotient_graph(graph, partitions)
            
            num_blocks = len(blocks)
            for fm_node, to_node in zip(range(num_blocks), range(1, num_blocks -1)):
                try:
                    path = nx.shortest_path(B, fm_mode, to_node)
                except nx.NetworkXNoPath as e:
                        pass
                except nx.NetworkXError as e:
                    tkm.showerror("Node not in graph", str(e))
                    return
                else:	
                    path2 = []
                    for a in path[1:-1]:
                        for n in partitions[a]:
                            neighbors.add(n)
            G = graph.subgraph(neighbors)
        return G
        
    def _radial_behind(self, home_node, behind_node):
        base_islands = nx.number_connected_components(self.dispG)
        
        G = nx.Graph()
        G.add_nodes_from(self.dispG.nodes())
        G.add_edges_from(self.dispG.edges())
        G.remove_edge(home_node, behind_node)
        
        node_sets = list(nx.connected_components(G))
        
        if len(node_sets) == base_islands:
            return None
        else:
            for ns in node_sets:
                if behind_node in ns:
                    return ns
        

    def onPanStart(self, event):
        #print("Pan start: %d, %d" % (event.x, event.y))
        # Window or canvas?
        # self._pan_data = (self.canvasx(event.x), self.canvasy(event.y))
        self._pan_data = (event.x, event.y)
        self.winfo_toplevel().config(cursor='fleur')
    
    def onPanMotion(self, event):
        if self._pan_data[0] == None or self._pan_data[1] == None:
            return
        delta_x = event.x - self._pan_data[0]
        delta_y = event.y - self._pan_data[1]
        self.move(tk.ALL, delta_x, delta_y)
        self._pan_data = (event.x, event.y)
    
    def onPanEnd(self, event):
        #print("Pan end")
        self._pan_data = (None, None)
        self.winfo_toplevel().config(cursor='arrow')
    
    def onZoom(self, event):
        #print("Zoom")
        factor = 0.1 * (1 if event.delta < 0 else -1)
        
        x = (event.widget.winfo_rootx() + event.x) - self.winfo_rootx()
        y = (event.widget.winfo_rooty() + event.y) - self.winfo_rooty()
        
        ids  = self.find_withtag('node') # + self.find_withtag('edge')
        
        for i in ids:
            ix, iy, t1, t2 = self.bbox(i)
            
            dx = (x-ix)*factor
            dy = (y-iy)*factor
            
            self.move(i, dx, dy)
            
            for to_node, from_node, data in self.dispG.edges(data=True):
                from_xy = self._node_center(from_node)
                to_yx = self._node_center(to_node)
                if data['dispG_fm'] != from_node:
                    a = from_xy[:]
                    from_xy = to_xy[:]
                    to_xy = a[:]
                spline_xy = self._spline_center(*from_xy + to_xy + (data['m'],))
                
                data['token'].coords((from_xy+spline_xy+to_xy))
                
    def onNodeButtonPress(self, event):
        #print("Node button press")
        item = self._get_id(event)
        if item == None:
            #print("Trying to get widget from event.")
            #print(event.widget)
            pass
        if item != None:
            self._drag_data['item'] = item
            #self._drag_data['x'] = self.canvasx(event.x)
            #self._drag_data['y'] = self.canvasy(event.y)
            self._drag_data['x'] = event.x
            self._drag_data['y'] = event.y
        
            G_id = self.dispG.nodes[item]['G_id']
        
            self.onNodeSelected(G_id, self.G.nodes[G_id])
    
    def onNodeSelected(self, node_name, node_data):
        pass
        
    def onNodeButtonRelease(self, event):
        #print("Button release")
        self._drag_data['item'] = None
        self._drag_data['x'] = 0
        self._drag_data['y'] = 0
    
    
    def onNodeMotion(self, event):
        #print("Node motion")
        if self._drag_data['item'] is None:
            return
        
        delta_x = event.x - self._drag_data['x']
        delta_y = event.y - self._drag_data['y']
        
        self.move(self._drag_data['item'], delta_x, delta_y)
        
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y
        
        # Redraw
        from_node = self._drag_data['item']
        from_xy = self._node_center(from_node)
        for _, to_node, edge in self.dispG.edges(from_node, data=True):
            to_xy = self._node_center(to_node)
            if edge['dispG_fm'] != from_node:
                spline_xy = self._spline_center(*to_xy+from_xy+(edge['m'],))
                edge['token'].coords((to_xy+spline_xy+from_xy))
            else:
                spline_xy = self._spline_center(*from_xy+to_xy+(edge['m'],))
                edge['token'].coords((from_xy+spline_xy+to_xy))
    
    def onItemRightClick(self, event):
        pass
    
    def hide_behind(self, home_node, behind_node):
        pass
    
    def onNodeKey(self, event):	
        pass
    
    def remove_node(self, data_node_id):	
        # Remove it from our data graph
        try:
            self.G.remove_node(data_node_id)
        except nx.NetworkXError as e:
            print("WARNING: Cannot remove node %s: %s" % (data_node_id, e))
        
        # Find the disp_node id.
        for n in self.dispG:
            if self.dispG.nodes[n].get('G_id', -1) == data_node_id:
                self.hide_node(n)
                return
        print("Warning: Removed node from data, but did not find display node.")
        
    
    def hide_node(self, disp_node):
        for n, m, d in self.dispG.edges(disp_node, data=True):
            d['token'].delete()
        self.delete(disp_node)
        self.dispG.remove_node(disp_node)
        self._graph_changed()
    
    def mark_node(self, disp_node):
        item = self.dispG.nodes[disp_node]['token']
        item.mark()
    
    def center_on_node(self, data_node):
        #print("CENTERED ON NODE")
        try:
            disp_node = self._find_disp_node(data_node)
        except ValueError as e:
            #tkm.showerror("Message", "")
            #print("Unable to find center node?")
            #w = self.winfo_width()/2
            #h = self.winfo_height()/2
            #if w == 0:
            #    w = int(self['width'])/2
            #    h = int(self['height'])/2
            
            w = int(int(self.width)/2)
            h = int(int(self.height)/2)
            print("Moving by %d %d" % (w,h))
            self.move(tk.ALL, w, h+self.yoffset)
            return
        
        x,y = self.coords(self.dispG.nodes[disp_node]['token_id'])
        
        w = int(self['width'])
        h = int(self['height'])
        print("Measured canvas w/h: %dx%d, offsets are: %d, %d"  % (w*2,h*2, self.xoffset, self.yoffset))
        
        delta_x = w/2 + x 
        delta_y = h/2 + y
    
        self.move(tk.ALL, delta_x, delta_y)
    
    def onEdgeRightClick(self, event):
        print("Not implemented yet.")
        pass
    
    def onEdgeClick(self, event):
        print("Edge CLICK")
        item = self._get_id(event, 'edge')
        for u,v,k,d in self.dispG.edges(keys=True, data=True):
            if d['token'].id == item:
                break
        G_id = self.dispG.edges[u,v,k]['G_id']
        self.onEdgeSelected(G_id, self.G.get_edge_data(*G_id))
    
    def onEdgeSelected(self, edge_name, edge_data):
        print("Not implemented yet.")
        pass
    
    def hide_edge(self, edge_id):
        pass
    
    def mark_edge(self, disp_u, disp_v, key):
        token = self.dispG[disp_u][disp_v][key]['token']
        token.mark()
    
    def clear(self):
        self.delete(tk.ALL)
        self.dispG.clear()
    
    def plot(self, home_node, levels=1):
        self.clear()
        
        graph=self._neighbors(home_node, levels=levels)
        self._plot_graph(graph)
        
        if isinstance(home_node, (list, tuple, set)):
            self.center_on_node(home_node[0])
        else:
            self.center_on_node(home_node)
    
    
    def plot_additional(self, home_nodes, levels=0):
        """Plot new nodes"""
        
        new_nodes = self._neighbors(home_nodes, levels=levels)
        new_nodes = home_nodes.union(new_nodes)
        
        displayed_data_nodes = set([v['G_id'] for k,v in self.dispG.node.items()])
        
        current_num_islands = nx.number_connected_components(self.dispG)
        new_num_islands = nx.number_connected_components(self.G.subgraph(displayed_data_nodes.union(new_nodes)))
        if new_num_islands > current_num_islands:
            all_nodes = set(self.G.nodes())
            singleton_nodes = all_nodes - displayed_data_nodes - new_nodes
            singleton_nodes = map(lambda x: [x], singleton_nodes)
            partitions = [displayed_data_nodes, new_nodes] + list(singleton_nodes)
            B = nx.blockmodel(self.G, partitions, multigraph=True)
            
            try:
                path = nx.shortest_path(B, 0, 1)
            except nx.NetworkXNoPath:
                pass
            else:
                ans = tkm.askyesno("Plot path?", "A path exists between the current graph and"
                        "the nodes you have added. Would you like to plot that path?")
                if ans:
                    for u in path[1:-1]:
                        Gu = B.node[u]['graph'].nodes()
                        assert len(Gu) ==1; Gu=Gu[0]
                        new_nodes.add(Gu)
        self._plot_additional(new_nodes)
            
        
    def replot(self):
        nodes = [d['G_id'] for n, d in self.dispG.nodes(data=True)]
        
        # Plass to worry about edge and node marks
        
        self.plot(nodes, levels=0)
        
        # Remark nodes.
    
    def refresh(self):
        for u,v,k,d in self.dispG.edges(keys=True, data=True):
            item = d['token']
            G_id = d['G_id']
            item.edge_data = self.G.get_edge_data(*G_id)
            item.itemconfig()
        
        for u, d in self.dispG.nodes(data=True):
            item = d['token']
            node_name = d['G_id']
            try:
                data = self.G.nodes[node_name]
                item.render(data, node_name)
            except KeyError:
                print("WARNING: Not rending %s" % node_name)
        
        self._graph_changed()
    
    def plot_path(self, fm_node, to_node, levels=1, add_to_existing=False):
        try:
            path = nx.shortest_path(self.G, fm_node, to_node)
        except nx.NetworkXNoPath as e:
            tkm.showerror("No Path", str(e))
            return
        except nx.NetworkXError as e:
            tkm.showerror("Node not in graph", str(e))
            return
        
        graph = self.G.subgraph(self._neighbors(path,levels=levels))
        
        if add_to_existing:
            self._plot_additional(graph.nodes())
        else:
            self.clear()
            self._plot_graph(graph)
        
        if levels > 0 or add_to_existing:
            for u, v in zip(path[:-1], path[1:]):
                u_disp = self._find_disp_node(u)
                v_disp = self._find_disp_node(v)
                for key, value in self.dispG.edge[u_disp][v_disp].items():
                    self.mark_edge(u_disp, v_disp, key)
    
    def _plot_graph(self, graph, home_node=0):
        scale = int(min(self.width, self.height))
        scale = scale/100
        print("SCALE IS: %d " % scale)
        #scale -= 50
        if len(graph) > 1:
            layout = self.create_layout(graph, scale=scale, min_distance=10)
            for n in graph.nodes():
                self._draw_node(layout[n]+20, n)
        else:
            self._draw_node((scale/2, scale/2), home_node)
        
        for fm, to in set(graph.edges()):
            self._draw_edge(fm, to)
        
        self._graph_changed()
    
    def _plot_additional(self, nodes):
        existing_data_nodes = set([ v['G_id'] for k,v in self.dispG.node.items() ])
        nodes = set(nodes).union(existing_data_nodes)
        grow_graph = self.G.subgraph(nodes).copy()
        
        print(grow_graph)
        
        fixed = {}
        for n,d in self.dispG.nodes(data=True):
            fixed[d['G_id']] = self.coords(n)
        
        if len(existing_data_nodes) == 0:
            self._plot_graph(self.G)
            self._graph_changed()
            return
        layout = self.create_layout(grow_graph, pos=fixed, fixed=list(fixed.keys()))
    
        for n,m in grow_graph.copy().edges():
            if(n in existing_data_nodes) and (m in existing_data_nodes):
                grow_graph.remove_edge(n,m)
        
        #for n, degree in grow_graph.copy().degree():
        #    if degree == 0:
        #        grow_graph.remove_node(n)
        
        if len(grow_graph.nodes()) == 0:
            return
        
        for n in grow_graph.nodes():
            if n in existing_data_nodes:
                continue
            self._draw_node(layout[n], n)

        for n, m in set(grow_graph.edges()):
            if(n in existing_data_nodes) and (m in existing_data_nodes):
                continue
            self._draw_edge(n, m)
            
        self._graph_changed()
    
    def _graph_changed(self):
        for n, d in self.dispG.nodes(data=True):
            item = d['token']
            if self.dispG.degree[n] == self.G.degree[d['G_id']]:
                item.mark_complete()
            else:	
                print("NOT COMPLETE")
                for n in nx.all_neighbors(self.G, d['G_id']):
                    self._draw_edge(n, d['G_id'])
                item.mark_incomplete()
    
    def _find_disp_node(self, data_node):
        disp_node = [a for a, d in self.dispG.nodes(data=True) if d['G_id'] == data_node]

        if len(disp_node) == 0 and str(data_node).isdigit():
            data_node = int(data_node)
            disp_node = [a for a, d in self.dispG.nodes(data=True) if d['G_id'] == data_node]
            
        if len(disp_node) == 0:
            for f in self._node_filters:
                try:
                    show_flag = eval(f, {'u':data_node, 'd':self.G.nodes[data_node]})
                except Exception as e:
                    break
                if show_flag == False:
                    raise NodeFiltered
            print("Data node '%s' is not currently displayed"%data_node)
            raise ValueError("Data Node '%s' is not currently displayed"%data_node)
        elif len(disp_node) != 1:
            raise AssertionError("Data node '%s' is displayed multiple times" % data_node)
        return disp_node[0]
    
    def create_layout(self, G, pos=None, fixed=None, scale=1.0, min_distance=None):
        dim = 2
        try:
            import numpy as np
        except ImportError:
            raise ImportError("Need numpy.")
        if fixed is not None:
            nfixed = dict(zip(G,range(len(G))))
            fixed=np.asarray([nfixed[v] for v in fixed])
        
        if pos is not None:
            dom_size = max(flatten(pos.values()))
            pos_arr = np.asarray(np.random.random((len(G), dim)))*dom_size
            for i,n in enumerate(G):
                if n in pos:
                    pos_arr[i] = np.asarray(pos[n])
        else:
            pos_arr = []
            dom_zie = 1.0
        
        if len(G) == 0:
            return {}
        elif len(G) == 1:
            #return {G.nodes()[0]:(1,)*dim}
            return{0:(1,)*dim}
        
        A = nx.to_numpy_matrix(G)
        nnodes,_ = A.shape
        
        # WAS .66 (ODcupy 2/3s of the window), now much less.
        if fixed is not None:
            k = (min(self.width, self.height)*.66)/np.sqrt(nnodes)
        else:
            k = None
        
        pos = self._fruchterman_reingold(A,dim,k,pos_arr,fixed)
        
        if fixed is None:	
            pos = nx.layout.rescale_layout(pos, scale=scale)
        
        if min_distance and fixed is None:
            delta = np.zeros((pos.shape[0], pos.shape[0], pos.shape[1]), dtype=A.dtype)
            for i in range(pos.shape[1]):
                delta[:,:,i] = pos[:,i,None] - pos[:,i]
            distance = np.sqrt((delta**2).sum(axis=-1))
            
            cur_min_dist = np.where(distance==0, np.inf, distance).min()
            
            if cur_min_dist < min_distance:
                rescale = (min_distance/cur_min_dist) * pos.max()
                pos = nx.layout.rescale_layout(pos, scale=rescale)

        return(dict(zip(G,pos)))
    
    def _fruchterman_reingold(self, A, dim=2, k=None, pos=[], fixed=None, iterations=50):
        try:
            import numpy as np
        except ImportError:
            raise ImportError("Need numpy.")
        
        try:
            nnodes,_ = A.shape
        except AttributeError:
            raise nx.NetworkXError("fruchterman_reingold() requires an adjacency matrix as input.")
        
        A = np.array(A)
        
        if pos == []:
            pos = np.asarray(np.random.random((nnodes, dim)), dtype=A.dtype)
        else:
            pos = pos.astype(A.dtype)
        
        # Optimal distance between nodes
        if k is None:
            k = np.sqrt(1.0/nnodes)
        
        t = max(max(pos.T[0]) - min(pos.T[0]), max(pos.T[1]) - min(pos.T[1]))*0.1
        
        dt = t/float(iterations+1)
        delta = np.zeros((pos.shape[0],pos.shape[0],pos.shape[1]), dtype=A.dtype)
        
        for iteration in range(iterations):
            for i in range(pos.shape[1]):
                delta[:,:,i] = pos[:,i,None] - pos[:,i]
            distance = np.sqrt((delta**2).sum(axis=-1))
            distance = np.where(distance<0.01,0.01,distance)
            displacement = np.transpose(np.transpose(delta)*(k*k/distance**2-A*distance/k)).sum(axis=1)
            
            length = np.sqrt((displacement**2).sum(axis=1))
            length = np.where(length<0.01,0.1, length)
            delta_pos = np.transpose(np.transpose(displacement)*t/length)
            if fixed is not None:
                delta_pos[fixed] = 0.0
            pos+=delta_pos
            t-=dt
            
        return pos

class NodeFiltered(Exception):
    pass

        
        
             
        
        