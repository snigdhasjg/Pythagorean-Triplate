from random import random

from deap.gp import cxOnePoint as onePointCrossover, mutUniform as uniformMutation
from pyspark import SparkContext


def cxOnePoint(sc: SparkContext, ind_pair: [], cxpb):
    if len(ind_pair) is 2 and random() < cxpb:
        left, right = onePointCrossover(ind_pair[0], ind_pair[1])
        del left.fitness.values, right.fitness.values
        return sc.parallelize([left, right])
    return sc.parallelize(ind_pair)


def mutUniform(individual, mutpb, expr, pset):
    if random() < mutpb:
        ind, = uniformMutation(individual, expr, pset)
        del ind.fitness.values
        return ind
    return individual
