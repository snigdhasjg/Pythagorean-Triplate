from deap import gp

import Find_Pythagorean_Eqn as fpe


def draw_graph_using_pygraphviz(nodes, edges, labels, tree_png="tree"):
    import pygraphviz as pgv
    g = pgv.AGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    g.layout(prog="dot")

    for i in nodes:
        n = g.get_node(i)
        n.attr["label"] = labels[i]

    g.draw('output/{}.png'.format(tree_png))


def draw():
    pop, log, hof = fpe.main()
    expr = hof[0]
    nodes, edges, labels = gp.graph(expr)
    print('Best individual : ', expr, expr.fitness)

    tree_name = '{}'.format(expr.fitness).replace('(', '').replace(')', '').replace(',', '')
    draw_graph_using_pygraphviz(nodes, edges, labels, tree_name)


if __name__ == '__main__':
    for _ in range(100):
        draw()
