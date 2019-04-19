import operator
import math
import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

# import Generate_Triple
#
# ALL_POINTS = Generate_Triple.generate_list(20)

import Input_Points

ALL_POINTS = Input_Points.get_all_points()


# Define new functions for division
def safe_div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


def my_power(number, p):
    try:
        return number ** p
    except ZeroDivisionError:
        return 1
    except OverflowError:
        return 1


def my_root(number, q):
    power = my_power(number, safe_div(1, q))
    if isinstance(power, complex):
        return 1000000
    return power


pset = gp.PrimitiveSet("MAIN", 2)
pset.addPrimitive(operator.add, 2)
# pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(math.sqrt, 1)
# pset.addPrimitive(my_power, 2)
# pset.addPrimitive(my_root, 2)
# pset.addPrimitive(safeDiv, 2)
# pset.addPrimitive(operator.neg, 1)
# pset.addPrimitive(math.cos, 1)
# pset.addPrimitive(math.sin, 1)
# pset.addPrimitive(abs, 1)
# pset.addEphemeralConstant("rand101", lambda: random.randint(1, 2))
pset.renameArguments(ARG0='A', ARG1='B')

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


def evalSymbReg(individual, points):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # Evaluate the mean squared error between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    try:
        sqerrors = ((func(x[0], x[1]) - x[2]) ** 2 for x in points)
        return math.sqrt(math.fsum(sqerrors)),
    except OverflowError:
        return 100000000,


toolbox.register("evaluate", evalSymbReg, points=ALL_POINTS)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=6)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))


def main():
    random.seed(518)

    pop = toolbox.population(n=500)
    hof = tools.HallOfFame(1)

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg\t", numpy.mean)
    mstats.register("std\t", numpy.std)
    mstats.register("min\t", numpy.min)
    mstats.register("max\t", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.9, 0.2, 50, stats=mstats, halloffame=hof, verbose=True)

    # print('Best individual : ', hof[0], hof[0].fitness)
    # print log
    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()
    print('Best individual : ', hof[0], hof[0].fitness)
