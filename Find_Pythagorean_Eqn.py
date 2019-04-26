import math
import operator
from random import randint

import numpy
from deap import algorithms
from deap import base
from deap import creator
from deap import gp
from deap import tools

from TripletHelper.My_Helper import ALL_POINTS, safe_power

from time import time


__type__ = float


def create_primitive_set():
    pset = gp.PrimitiveSetTyped("MAIN", [__type__, __type__], __type__)

    pset.addPrimitive(operator.add, [__type__, __type__], __type__)
    pset.addPrimitive(operator.sub, [__type__, __type__], __type__)
    pset.addPrimitive(operator.mul, [__type__, __type__], __type__)
    # pset.addPrimitive(safe_div, [__type__, __type__], __type__)

    pset.addPrimitive(safe_power, [__type__, int, int], __type__, name='power')

    def return_int(obj):
        return None

    pset.addPrimitive(return_int, [__type__], int, name='dummy')

    pset.addEphemeralConstant('rand1-2 %f' % time(), lambda: randint(1, 3), int)
    pset.renameArguments(ARG0='A', ARG1='B')

    return pset


def create_toolbox(pset: gp.PrimitiveSetTyped):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    def eval_symb_reg(individual, points):
        # Transform the tree expression in a callable function
        func = toolbox.compile(expr=individual)
        # Evaluate the mean squared error between the expression
        # and the real function : x**4 + x**3 + x**2 + x
        sqerrors = ((func(x[0], x[1]) - x[2]) ** 2 for x in points)
        return math.sqrt(math.fsum(sqerrors)),

    toolbox.register("evaluate", eval_symb_reg, points=ALL_POINTS)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=3)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=3))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=3))

    return toolbox


def get_numpy_stats():
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg\t", numpy.mean)
    mstats.register("std\t", numpy.std)
    mstats.register("min\t", numpy.min)
    mstats.register("max\t", numpy.max)

    return mstats


def main(verbose=True):
    pset = create_primitive_set()
    toolbox = create_toolbox(pset)
    pop = toolbox.population(n=500)
    hof = tools.HallOfFame(1)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.9, 0.3, 200, stats=get_numpy_stats(), halloffame=hof, verbose=verbose)

    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()
    print('Best individual : ', hof[0], hof[0].fitness)
