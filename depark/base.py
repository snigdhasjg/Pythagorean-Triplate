import math
import operator
from functools import partial

from deap import base
from deap import gp
from deap import tools

from TripletHelper.My_Helper import ALL_POINTS
from . import tools as detool, gp as degp


class Toolbox(object):

    def __init__(self, pset: gp.PrimitiveSetTyped):
        self.pset = pset
        self.expr = partial(gp.genHalfAndHalf, pset=self.pset, min_=1, max_=4)
        self.individual = partial(tools.initIterate, PrimitiveTree, self.expr)
        self.population = partial(detool.initRepeat, func=self.individual)
        self.compile = partial(gp.compile, pset=self.pset)

        def eval_symb_reg(tb: Toolbox, individual, points):
            if not individual.fitness.valid:
                # Transform the tree expression in a callable function
                func = tb.compile(expr=individual)
                # Evaluate the mean squared error between the expression
                # and the real function : x**4 + x**3 + x**2 + x
                sqerrors = ((func(x[0], x[1]) - x[2]) ** 2 for x in points)
                score = math.sqrt(math.fsum(sqerrors)),
                individual.fitness.values = score
            return individual

        self.evaluate = partial(eval_symb_reg, tb=self, points=ALL_POINTS)
        self.select = partial(detool.selTournament, tournsize=4)
        self.mate = partial(degp.cxOnePoint)
        self.expr_mut = partial(gp.genFull, min_=0, max_=5)
        self.mutate = partial(degp.mutUniform, expr=self.expr_mut, pset=self.pset)


def create_toolbox(pset):
    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=4)
    toolbox.register("individual", tools.initIterate, PrimitiveTree, toolbox.expr)
    toolbox.register("population", detool.initRepeat, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def eval_symb_reg(individual, points):
        # Transform the tree expression in a callable function
        func = toolbox.compile(expr=individual)
        # Evaluate the mean squared error between the expression
        # and the real function : x**4 + x**3 + x**2 + x
        sqerrors = ((func(x[0], x[1]) - x[2]) ** 2 for x in points)
        score = math.sqrt(math.fsum(sqerrors)),
        individual.fitness.values = score
        return individual

    toolbox.register("evaluate", eval_symb_reg, points=ALL_POINTS)
    toolbox.register("select", detool.selTournament, tournsize=4)
    toolbox.register("mate", degp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=5)
    toolbox.register("mutate", degp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=5))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=5))

    return toolbox


class Fitness(base.Fitness):
    weights = (-1.0,)

    def __init__(self, values=()):
        super().__init__(values)


class PrimitiveTree(gp.PrimitiveTree):
    def __init__(self, content):
        self.fitness = Fitness()
        super().__init__(content)


if __name__ == '__main__':
    from Find_Pythagorean_Eqn import create_primitive_set
    from pyspark import SparkContext

    scp = SparkContext(appName="DEAP")

    toolbox = Toolbox(create_primitive_set())
    toolbox.population(sc=scp, n=500).count()
    print('Hi')
