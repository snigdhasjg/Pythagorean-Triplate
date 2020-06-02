import math
import operator
from logging import getLogger
from random import randint
from time import time_ns

from deap import base
from deap import creator
from deap import gp
from deap import tools
from pyspark import SparkContext

from TripletHelper.My_Helper import ALL_POINTS, safe_power, safe_div
from TripletHelper.Saving import save_halloffame
from depark import algorithms as dealgorithms
from depark import gp as degp
from depark import tools as detool

__type__ = float
NO_OF_POPULATION = 500
logger = getLogger(__name__)


def create_primitive_set():
    pset = gp.PrimitiveSetTyped("MAIN", [__type__, __type__], __type__)

    pset.addPrimitive(operator.add, [__type__, __type__], __type__)
    pset.addPrimitive(operator.sub, [__type__, __type__], __type__)
    pset.addPrimitive(operator.mul, [__type__, __type__], __type__)
    pset.addPrimitive(safe_div, [__type__, __type__], __type__)

    pset.addPrimitive(safe_power, [__type__, int, int], __type__, name='power')

    def return_int(obj):
        return None

    pset.addPrimitive(return_int, [__type__], int, name='dummy')

    pset.addEphemeralConstant('rand%d' % time_ns(), lambda: randint(1, 10), int)
    pset.renameArguments(ARG0='A', ARG1='B')

    return pset


def create_toolbox(pset: gp.PrimitiveSetTyped):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=4)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
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


def get_rdd_stats():
    stats_fit = detool.Statistics(lambda ind: ind.fitness.values)
    stats_size = detool.Statistics(len)
    stats = detool.MultiStatistics(fitness=stats_fit, size=stats_size)

    return stats


def main(verbose=True):
    pset = create_primitive_set()
    toolbox = create_toolbox(pset)
    hof = detool.HallOfFame(1)

    sc = SparkContext(appName="DEAP")
    pop, log = dealgorithms.eaSimple(sc, toolbox, 0.8, 0.2, 100, 500, stats=get_rdd_stats(), halloffame=hof,
                                     verbose=verbose)

    print('Best individual : ', hof[0], hof[0].fitness)
    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()
    save_halloffame(hof)
