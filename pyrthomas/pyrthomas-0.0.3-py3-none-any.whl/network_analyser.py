import itertools

from networkx import DiGraph, nx
from networkx.classes.reportviews import EdgeView

from core.pyrthomas import utils


class NetworkAnalyser:

    @staticmethod
    def get_predecessors(network: DiGraph):
        result = dict()
        for node in network.nodes:
            predecessors = tuple(nx.DiGraph.predecessors(network, node))
            combinations = utils.all_subsets(predecessors)
            result[node] = tuple(combinations)
        return result

    @staticmethod
    def generate_state_space(graph: DiGraph):
        nodes = graph.nodes
        parameters = list()
        for node in nodes:
            edges_from_node = graph.edges(node, data=True)
            max_weighted_edge = max(edges_from_node, key=lambda x: utils.get_weight(x, True))
            max_threshold = utils.get_weight(max_weighted_edge, True)
            values = tuple(range(max_threshold + 1))
            parameters.append(values)
        state_space = tuple(itertools.product(*parameters))
        for element in state_space:
            yield dict(zip(nodes, element))

    @staticmethod
    def get_state_graph(network: DiGraph, parameters) -> DiGraph:
        state_space = list(NetworkAnalyser.generate_state_space(network))
        state_graph = nx.DiGraph()
        state_space_nodes = [utils.create_node_from_dict(entry) for entry in state_space]
        state_graph.add_nodes_from(state_space_nodes)

        resources = NetworkAnalyser.calculate_resources(network, state_space)

        k_states = NetworkAnalyser.calculate_k(resources, parameters)

        next_states = NetworkAnalyser.calculate_next_states(k_states)

        edges = NetworkAnalyser.generate_edges(next_states)
        state_graph.add_edges_from(edges)
        return state_graph

    @staticmethod
    def generate_edges(next_states):
        edges = list()
        for key, states in next_states.items():
            previous_value = dict(key)
            source = utils.create_node_from_dict(previous_value)
            for state in states:
                target = utils.create_node_from_dict(state)
                edges.append((source, target))
        return edges

    @staticmethod
    def calculate_next_states(k_states):
        for state_key, state in k_states.items():
            previous_entities = dict(state_key)
            new_val = list()
            temp_previous = previous_entities.copy()
            for entity_key, previous_entity in previous_entities.items():
                next_value = k_states[state_key][entity_key]

                if next_value > previous_entity:
                    previous_entities[entity_key] = previous_entity + 1
                elif next_value < previous_entity:
                    previous_entities[entity_key] = previous_entity - 1

                if not (previous_entities in new_val) and not previous_entities == temp_previous:
                    new_val.append(previous_entities.copy())
                    previous_entities[entity_key] = temp_previous[entity_key]
            k_states[state_key] = new_val
        return k_states

    @staticmethod
    def calculate_k(resources, parameters):
        for resource_key, entities in resources.items():
            for entity_key, entity in entities.items():
                matched_interaction = filter(lambda x: sorted(x[0]) == sorted(entity),
                                             parameters[entity_key])
                first_interaction = next(matched_interaction)
                entities[entity_key] = first_interaction[1]
        return resources

    @staticmethod
    def get_cycles(network: nx.DiGraph):
        return nx.simple_cycles(network)

    @staticmethod
    def get_deadlock_states(network: nx.DiGraph):
        out_degree_iter = network.out_degree(network.nodes)
        return [node for node, out_degree in out_degree_iter if out_degree == 0]

    @staticmethod
    def calculate_resources(network, state_space):
        resources = dict()
        for state in state_space:
            node = dict()
            for key in state:
                entity_resources = list()
                in_edges = network.in_edges(key, data=True)
                for edge in in_edges:
                    is_resource = NetworkAnalyser.is_resource_of_state(state, edge)
                    if is_resource:
                        entity_resources.append(edge[0])
                entity_resources.sort()
                node[key] = entity_resources

            state_key = tuple(state.items())
            resources[state_key] = node
        return resources

    @staticmethod
    def get_required_parameters(network: DiGraph):
        nodes = network.nodes
        parameters = dict()
        for node in nodes:
            predecessors = tuple(nx.DiGraph.predecessors(network, node))
            required_interactions = [{'interaction': interaction, 'value': None} for interaction in
                                     utils.all_subsets(predecessors)]
            parameters[node] = required_interactions
        return parameters

    @staticmethod
    def is_resource_of_state(state: dict, edge: EdgeView):
        weight = utils.get_weight(edge)
        is_positive = weight >= 0
        value = state[edge[0]]
        return (is_positive and value >= abs(weight)) or (not is_positive and value < abs(weight))
