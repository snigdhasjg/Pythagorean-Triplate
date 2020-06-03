import operator
from logging import getLogger
from random import randint
from time import time_ns

from deap import gp
from pyspark import SparkContext

from TripletHelper.My_Helper import safe_power, safe_div
from TripletHelper.Saving import save_halloffame
from depark import algorithms as dealgorithms
from depark import tools as detool
from depark import base as debase

__type__ = float
NO_OF_POPULATION = 500
logger = getLogger(__name__)
logger.info("Hwllo")


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
    pset.addTerminal(1, int)
    # pset.addEphemeralConstant('rand%d' % time_ns(), lambda: randint(1, 10), int)
    pset.renameArguments(ARG0='A', ARG1='B')

    return pset


def get_rdd_stats():
    stats_fit = detool.Statistics(lambda ind: ind.fitness.values)
    stats_size = detool.Statistics(len)
    stats = detool.MultiStatistics(fitness=stats_fit, size=stats_size)

    return stats


def main(verbose=True):
    pset = create_primitive_set()
    toolbox = debase.Toolbox(pset)
    hof = detool.HallOfFame(1)

    sc = SparkContext(appName="DEAP")
    pop, log = dealgorithms.eaSimple(sc, toolbox, 0.8, 0.2, 100, 500, stats=get_rdd_stats(), halloffame=hof,
                                     verbose=verbose)

    print('Best individual : ', hof[0], hof[0].fitness)
    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()
    save_halloffame(hof)
