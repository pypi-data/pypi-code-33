import networkx as nx
import sys
from appJar import gui

try:
    # Python 3
    import tkinter as tk
    import tkinter.messagebox as tkm
    import tkinter.simpledialog as tkd
    from tkinter.font import Font
except ImportError:
    # Python 2
    import Tkinter as tk
    import tkMessageBox as tkm
    import tkSimpleDialog as tkd
    from tkFont import Font

sys.path.append("..")

import globals
from netxCanvas.canvas import netxCanvas, GraphCanvas
from netxCanvas.style import NodeClass


class topoStyle(NodeClass):
    def render(self, data, node_name):
        label_txt = data.get('label', None)
        font = Font(family="Helvetica", size=12)
        h = font.metrics("linespace") + 6
        if label_txt:
            w = font.measure(label_txt) + 8
        else:
            w = font.measure("....") + 2
        self.config(width=w, height=h)
        marker_options = {'fill': data.get('color','orange'), 'outline': 'orange'}
            
        if data.get('circle', False) or data.get('type', 'NOTLAN') == 'LAN':
            self.create_oval(0,0,w-1,h-1, **marker_options)
            self.config(width=w, height=h)
            if label_txt:
                self.create_text((w)/2, (h)/2, text=label_txt, font=font, fill="black")
        else:
            self.create_rectangle(0,0,w,h, **marker_options)
            if label_txt:
                self.create_text(w/2, h/2, text=label_txt, font=font, fill="black")

class topoHandler(GraphCanvas, object):
    def __init__(self, canvas, width=0, height=0, **kwargs):
        self.node_index = 1
        G = nx.Graph()
   
        G.add_node('lan0', label='lan0')
        G.node['lan0']['label'] = 'lan0'
        G.node['lan0']['type'] = 'LAN'

        try:
            # Python 3
            super().__init__(G, master=canvas, width=width, height=height, NodeClass=topoStyle,home_node = 'lan0', **kwargs)
        except TypeError:
            # Python 2
            super(topoHandler, self).__init__(G, master=canvas, width=width, height=height, NodeClass=topoStyle, home_node = 'lan0', **kwargs)
        self.pack()
    
    def setoffsets(self, xoffset=0, yoffset=0, width=0, height=0):
        self.xoffset = xoffset
        self.yoffset = yoffset
        if width!=0:
            self.width = width
        if height!=0:
            self.height = height
    

    def process_constraints(self):
        print("CONSTRAINTS")
        print(globals.constraints)
        print("Process constraints. NODES LIST:")
        print(globals.nodes)
        print("Links:")
        print(globals.links)
        print("Lans:")
        print(globals.lans)
        new_nodes = []
        new_lans = []
        remove_nodes = []
        
        # First, check what we have, and remove nodes and lans
        # that are no longer in the constraint lists.
        for n in self.G.nodes():
            if n not in globals.nodes and n not in globals.lans:
                print("Topo: Removing node: %s" % str(n))
                remove_nodes.append(n)
            else:
                # If the type has changed (a node is now a lan or vise versa) 
                # just remove and add again.
                if 'type' not in self.G.nodes(data=True)[n]:
                    print("WARNING: Topo data graph has node %s, but no type for it." % n)
                    continue
                if n in globals.nodes:
                    print(n) 
                    if self.G.nodes(data=True)[n]['type'] == 'LAN':
                        remove_nodes.append(n)
                        new_nodes.append(n)
                elif n in globals.lans:
                    if self.G.nodes(data=True)[n]['type']  == 'NODE':
                        remove_nodes.append(n)
                        new_lans.append(n)
                    
        for n in remove_nodes:
            self.remove_node(n)
        #if len(remove_nodes) > 0:
        #    self.refresh()
            
        # Add nodes and lans we don't yet have.
        for n in globals.nodes:
            if n not in self.G.nodes():
                new_nodes.append(n)
        for n in new_nodes:
            self.G.add_node(n)
            self.G.nodes[n]['label'] = str(n)
            self.G.nodes[n]['type'] = 'NODE'
        for l in globals.lans:
            if l not in self.G.nodes():
                new_lans.append(l)
        for l in new_lans:
            self.G.add_node(l)
            self.G.nodes[l]['label'] = str(l)
            self.G.nodes[l]['type'] = 'LAN'
        
        
        # Be sure our graph dosn't have connections that no longer exist.
        remove_edges = []
        add_back = []
        for edge in self.G.edges():
            if not self._islinked(edge[0], edge[1]):
                remove_edges.append(edge)
        for edge in remove_edges:
            print("Node %s and %s are no longer connected." % (edge[0], edge[1]))
            try:
                self.G.remove_edge(edge[0], edge[1])
            except NetworkXError:
                try:
                    self.G.remove_edge(edge[1], edge[0])
                except NetworkXError:
                    pass
            # XXX Not clear why removing the edge doesn't do the trick!
            for n in edge:
                data = self.G.nodes(data=True)[n]
                self.remove_node(n)
                add_back.append(n)
        for n in add_back:
            self.G.add_node(n)
            self.G.nodes[n]['label'] = str(n)
            if n in globals.lans:	
                self.G.nodes[n]['type'] = 'LAN'
            else:
                self.G.nodes[n]['type'] = 'NODE'
            
        # Go through all links and lans and be sure everything is connected.
        for l in globals.lans:
            for x in globals.lans[l]:
                self._connect(x, l)
        for l in globals.links:
            for x in globals.links[l]:
                self._connect(x, l)
        

        #new = new_lans + new_nodes + add_back
        new = [ n for n in self.G.nodes()]
        if len(new) > 0:
            print("Doing plot update for:")
            print(new)
            self._plot_additional(new)
        
        print("Doing a topo graph refresh.")
        self.refresh()        
        

    def _islinked(self, n1, n2):
        # Checks if our globals links and lans list these as connected parties.
        if n1 in globals.lans and n2 in globals.lans[n1]:
            return True
        if n2 in globals.lans and n1 in globals.lans[n2]:
            return True
        if n1 in globals.links and n2 in globals.links[n1]:
            return True
        if n2 in globals.links and n1 in globals.links[n2]:
            return True
        return False
                
                
    def _connect(self, n1, n2):
        if n1 in self.G.nodes() and n2 in self.G.nodes():
            if n1 not in self.G.neighbors(n2):	
                self.G.add_edge(n1, n2)
            print("Node %s and %s should be connected." % (n1, n2))
        else:
            print("WARNING: Asked to link %s and %s in topology graph, but one of these is not in our graph data." %(n1,n2)) 
    
        
    def save(self, f):
        l=0
        lans=dict()
        num_nodes = len(self.G)
        print("Have %d nodes ", (num_nodes))
        nodes = nx.get_node_attributes(self.G, 'label')
        for n in nodes:
            f.write("node:\n")
            f.write("\tid: " + str(n) + '\n')
            f.write("\tendpoints: [" + nodes[n] + ']\n')
            f.write("\tprops: {}\n")
        edges = nx.edges(self.G);
        for e in edges:
            if nodes[e[0]].startswith("lan"):
                if e[0] not in lans:
                    lans[e[0]] = []
                lans[e[0]].append(e[1])
                print(lans[e[0]])
            else:
                f.write("link:\n")
                f.write("\tid: link" + str(l) + '\n')
                l=l+1
                f.write("\tendpoints: [[" + nodes[e[0]] + "],[" + nodes[e[1]]+"\n")
                f.write("\tprops: {}\n");
        for n in lans:
            f.write("net:\n")
            f.write("\tid: " + str(n) + '\n')
            f.write("\tnodes: [")
            first = 0
            for i in lans[n]:
                if first == 1:
                    f.write(",")
                first = 1
                f.write(str(i));
            f.write("]\n");
            
