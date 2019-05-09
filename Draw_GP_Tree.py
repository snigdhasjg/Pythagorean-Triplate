from deap import gp
from time import time
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

    g.draw('{}.png'.format(tree_png))


def draw(hof=None, iteration_no=-1):
    if hof is None:
        pop, log, hof = fpe.main(False)

    expr = hof[0]
    nodes, edges, labels = gp.graph(expr)
    print('Best individual : ', expr, expr.fitness)

    tree_name = '{}-{}'.format(expr.fitness, iteration_no) \
        .replace('(', '') \
        .replace(')', '') \
        .replace(',', '')
    file_previously_exists = True
    try:
        open(tree_name, 'r')
    except FileNotFoundError:
        file_previously_exists = False
    if file_previously_exists:
        tree_name += '-{}'.format(time())
    draw_graph_using_pygraphviz(nodes, edges, labels, tree_name)


if __name__ == '__main__':
    for i in range(100):
        draw(iteration_no=i)
