from deap import gp
from time import time
import pygraphviz as pgv
import os


def draw_graph_using_pygraphviz(expr, tree_png="tree"):
    nodes, edges, labels = gp.graph(expr)
    g = pgv.AGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    g.layout(prog="dot")

    for i in nodes:
        n = g.get_node(i)
        n.attr["label"] = labels[i]

    g.draw('{}.png'.format(tree_png))


def draw(expr=None, iteration_no=-1):
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
    draw_graph_using_pygraphviz(expr, tree_name)


def make_picture(population):
    each_pops = population
    dirname = 'out/Pop-{}'.format(time())
    os.mkdir(dirname)
    print('printing ', dirname)
    for i in range(len(each_pops)):
        each_pop = each_pops[i]
        filename = '{}/{}-{}'.format(dirname, i, each_pop.fitness) \
            .replace('(', '').replace(')', '').replace(',', '')
        draw_graph_using_pygraphviz(each_pop, filename)


if __name__ == '__main__':
    for j in range(100):
        draw(iteration_no=j)
