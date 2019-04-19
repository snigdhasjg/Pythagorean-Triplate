from deap import gp
import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz as pgv

import Find_Pythagorean_Eqn as fpe


def get_graph_data():
    pop, log, hof = fpe.main()
    expr = hof[0]
    nodes, edges, labels = gp.graph(expr)
    return nodes, edges, labels


# ### Graphviz Section ###
def draw_graph_using_pygraphviz(nodes, edges, labels):
    g = pgv.AGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    g.layout(prog="dot")

    for i in nodes:
        n = g.get_node(i)
        n.attr["label"] = labels[i]

    g.draw("tree.pdf")


def draw_graph_using_matplotlib(nodes, edges, labels):
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    pos = nx.graphviz_layout(g, prog="dot")

    nx.draw_networkx_nodes(g, pos)
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_labels(g, pos, labels)
    plt.show()


if __name__ == '__main__':
    n, e, l = get_graph_data()
    draw_graph_using_pygraphviz(n, e, l)
