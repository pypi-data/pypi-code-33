"""    def save_network(self):
        if self.view is None or self.network is None:
            return

        filename = QFileDialog.getSaveFileName(
            self, 'Save Network', '',
            'NetworkX graph as Python pickle (*.gpickle)\n'
            'NetworkX edge list (*.edgelist)\n'
            'Pajek network (*.net *.pajek)\n'
            'GML network (*.gml)')
        if filename:
            _, ext = os.path.splitext(filename)
            if not ext: filename += ".net"
            items = self.network.items()
            for i in range(self.network.number_of_nodes()):
                graph_node = self.network.node[i]
                plot_node = self.networkCanvas.networkCurve.nodes()[i]

                if items is not None:
                    ex = items[i]
                    if 'x' in ex.domain: ex['x'] = plot_node.x()
                    if 'y' in ex.domain: ex['y'] = plot_node.y()

                graph_node['x'] = plot_node.x()
                graph_node['y'] = plot_node.y()

            network.readwrite.write(self.network, filename)


"""
