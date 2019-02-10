
from graph import proof_graph as pgr
from visualize import visual_proof_graph as vpg

import compression.compression.compression as comp


class HorizontalCompression(object):

    def __init__(self, file_path):
        self.proof = pgr.ProofGraph(file_path=file_path, init_data=True)
        self.visual_pg = vpg.VisualProofGraph(self.proof)

    def compress(self, comp_file_path):
        repeated_formulas = comp.get_nodes_repeated_formulas(self.proof)

        collapse = 1
        for level, repeated_nodes in repeated_formulas.items():
            for nodes in repeated_nodes:
                node_u = nodes.pop()
                for node_v in nodes:
                    rule_function = \
                        comp.identify_rule(self.proof, node_u, node_v)
                    # rule_name = rule_function.__name__
                    # # print "Collapse:", collapse, "(rule: ", rule_name, ")"
                    # graph_name = "collapse " + str(collapse) + "-" + rule_name
                    # p1, p2, a_edges = \
                    #     visual_pg.draw_collapse(graph_name + "-Antes",
                    #                             [node_u, node_v], before=True)
                    node_u = comp.exec_rule(rule_function, self.proof,
                                                   node_u, node_v)
                    # visual_pg.draw_collapse(graph_name + "-Depois", [node_u],
                    #                         after=True, premisses_1=p1,
                    #                         premisses_2=p2, a_edges=a_edges)
                    collapse += 1
                    # print ""

        comp.redirect_multi_ancestor_edges(self.proof)
        comp.demote_ancestor_edges(self.proof)
        comp.remove_unused_colors(self.proof)

        self.visual_pg.draw_final(comp_file_path)
