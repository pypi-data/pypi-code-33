#!/usr/local/bin/python
# coding: utf-8

import argparse

from compression import compression
from graph import proof_graph as pgr
from visualize import visual_proof_graph as vpg
from util import convert


def main():

    parser = argparse.ArgumentParser()

    # file argument
    parser.add_argument("file", type=file,
                        help="read proof_graph from file")

    # visualize argument
    parser.add_argument("--visualize", dest='visualize', action='store_true',
                        help="generate PDF view")
    parser.add_argument("--no-visualize", dest='visualize',
                        action='store_false',
                        help="not generate PDF view")
    parser.set_defaults(visualize=True)

    parser.add_argument("--convert", dest='convert', action='store_true',
                        help="convert input graph")
    parser.add_argument("--no-convert", dest='convert',
                        action='store_false',
                        help="not convert input graph")
    parser.set_defaults(visualize=False)

    args = parser.parse_args()

    if args.convert:
        proof_graph = pgr.ProofGraph(convert.convert_input(args.file),
                                     init_data=True)
    else:
        proof_graph = pgr.ProofGraph(file_path=args.file, init_data=True)

    visual_pg = vpg.VisualProofGraph(proof_graph)

    if args.visualize:
        visual_pg.draw_input()

    print "Compressing (start)"

    repeated_formulas = compression.get_nodes_repeated_formulas(proof_graph)
    collapse = 1
    for level, repeated_nodes in repeated_formulas.items():
        for nodes in repeated_nodes:
            node_u = nodes.pop()
            for node_v in nodes:
                rule_function = \
                    compression.identify_rule(proof_graph, node_u, node_v)
                rule_name = rule_function.__name__
                # print "Collapse:", collapse, "(rule: ", rule_name, ")"
                graph_name = "collapse " + str(collapse) + "-" + rule_name
                p1, p2, a_edges = \
                    visual_pg.draw_collapse(graph_name+"-Antes",
                                            [node_u, node_v], before=True)
                node_u = compression.exec_rule(rule_function, proof_graph,
                                               node_u, node_v)
                visual_pg.draw_collapse(graph_name+"-Depois", [node_u],
                                        after=True, premisses_1=p1,
                                        premisses_2=p2, a_edges=a_edges)
                collapse += 1
                # print ""

    compression.redirect_multi_ancestor_edges(proof_graph)
    compression.demote_ancestor_edges(proof_graph)
    compression.remove_unused_colors(proof_graph)

    print "Compressing (done)"

    if args.visualize:
        print "Generating PDF files (start)"
        visual_pg.draw_final()
        print "Generating PDF files (done)"

    print "Vertices: ", len(proof_graph.get_nodes())
    print "Edges: ", len(proof_graph.get_edges())


if __name__ == '__main__':
    main()
