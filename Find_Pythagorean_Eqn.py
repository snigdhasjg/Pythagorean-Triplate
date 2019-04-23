import operator
import math
from random import randint

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

from TripletHelper.My_Helper import ALL_POINTS, safe_div, safe_power


def return_int(obj):
    return None


__type__ = float
pset = gp.PrimitiveSetTyped("MAIN", [__type__, __type__], __type__)

pset.addPrimitive(operator.add, [__type__, __type__], __type__)
pset.addPrimitive(operator.sub, [__type__, __type__], __type__)
pset.addPrimitive(operator.mul, [__type__, __type__], __type__)
# pset.addPrimitive(safe_div, [__type__, __type__], __type__)

pset.addPrimitive(safe_power, [__type__, int, int], __type__, name='power')

pset.addPrimitive(return_int, [__type__], int, name='dummy')

pset.addEphemeralConstant('rand1-2', lambda: randint(1, 2), int)
pset.renameArguments(ARG0='A', ARG1='B')

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=6)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


def evalSymbReg(individual, points):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # Evaluate the mean squared error between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    sqerrors = ((func(x[0], x[1]) - x[2]) ** 2 for x in points)
    return math.sqrt(math.fsum(sqerrors)),


toolbox.register("evaluate", evalSymbReg, points=ALL_POINTS)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=6)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=3))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=3))


def main():

    pop = toolbox.population(n=500)
    hof = tools.HallOfFame(1)

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg\t", numpy.mean)
    mstats.register("std\t", numpy.std)
    mstats.register("min\t", numpy.min)
    mstats.register("max\t", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.9, 0.3, 50, stats=mstats, halloffame=hof, verbose=True)

    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()
    print('Best individual : ', hof[0], hof[0].fitness)
