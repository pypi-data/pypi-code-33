class GameLogic(object):

    def find_path(self, graph, start_node, end_node, path=[]):
        path = path + [start_node]
        if start_node == end_node:
            return path
        if start_node not in graph:
            return None
        for node in graph[start_node]:
            if node not in graph:
                new_path = self.find_path(graph, node, end_node, path)
                if new_path:
                    return new_path
        return None

    def find_all_paths(self, graph, start_node, end_node, path=[]):
        path = path + [start_node]
        if start_node == end_node:
            return path
        if start_node not in graph:
            return []
        paths = []
        for node in graph[start_node]:
            if node not in graph:
                new_paths = self.find_all_paths(graph, node, end_node, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    def find_shortest_path(self, graph, start_node, end_node, path=[]):
        path = path + [start_node]
        if start_node == end_node:
            return path
        if start_node not in graph:
            return None
        shortest = None
        for node in graph[start_node]:
            if node not in graph:
                new_path = self.find_shortest_path(graph, node, end_node, path)
                if new_path:
                    if not shortest or len(new_path) < len(shortest):
                        shortest = new_path
        return shortest
