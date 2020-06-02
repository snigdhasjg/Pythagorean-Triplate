import math
import operator
from random import randint
from time import time_ns

from deap import base
from deap import creator
from deap import gp
from deap import tools
from pyspark import SparkContext, RDD

from TripletHelper.My_Helper import ALL_POINTS, safe_power, safe_div
from TripletHelper.Saving import save_halloffame
from depark import algorithms as dealgorithms
from depark import gp as degp
from depark import tools as detool

__type__ = float
NO_OF_POPULATION = 500

sc = SparkContext(appName="DEAP")
log4jLogger = sc.jvm.org.apache.log4j
log = log4jLogger.LogManager.getLogger(__name__)
log.warn("Hello world")


def spark_map(algorithm, population):
    return sc.parallelize(population).map(algorithm)


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
    toolbox.register("population", detool.initRepeat, sc, toolbox.individual)
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
    toolbox.register("select", detool.selTournament, sc=sc, tournsize=4)
    toolbox.register("mate", degp.cxOnePoint, sc)
    toolbox.register("expr_mut", gp.genFull, min_=0, max_=5)
    toolbox.register("mutate", degp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=5))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=5))

    return toolbox


def get_rdd_stats():
    stats_fit = detool.Statistics(lambda ind: ind.fitness.values)
    stats_size = detool.Statistics(len)
    mstats = detool.MultiStatistics(fitness=stats_fit, size=stats_size)

    return mstats


overflow_error = []


def my_eaSimple(population: RDD, toolbox, cxpb, mutpb, ngen, stats=None, halloffame: tools.HallOfFame = None,
                verbose=True):
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    # invalid_ind = [ind for ind in population if not ind.fitness.valid]
    # fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    # for ind, fit in zip(invalid_ind, fitnesses):
    #     ind.fitness.values = fit
    invalid_ind = population.filter(lambda x: not x.fitness.valid) \
        .map(lambda x: toolbox.evaluate(x))

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    try:
        gen = 1
        # last_few_pop_to_consider = 50
        # starting_condition = last_few_pop_to_consider
        # is_last_few_fitness_same = lambda stats_array: abs(numpy.mean(stats_array) - stats_array[0]) < 0.1
        while gen < ngen + 1:
            # Select the next generation individuals
            offspring = toolbox.select(population, population.count())

            # Vary the pool of individuals
            new_offspring = dealgorithms.varAnd(sc, offspring, toolbox, cxpb, mutpb)

            # Evaluate the individuals with an invalid fitness
            # invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            try:
                # fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
                # for ind, fit in zip(invalid_ind, fitnesses):
                #     ind.fitness.values = fit
                invalid_ind = new_offspring.filter(lambda x: not x.fitness.valid) \
                    .map(lambda x: toolbox.evaluate(x))
            except OverflowError:
                print(OverflowError, '\nResetting population')
                overflow_error.append(gen)
                continue

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(new_offspring)

            # Replace the current population by the offspring
            population = new_offspring

            # Append the current generation statistics to the logbook
            record = stats.compile(population) if stats else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            if verbose:
                print(logbook.stream)

            # stopping criteria
            min_fitness = record['fitness']['min\t']
            # max_fitness = record['fitness']['max\t']

            if min_fitness < 0.1:
                print('Reached desired fitness')
                break

            # if gen > starting_condition:
            #     min_stats = logbook.chapters['fitness'].select('min\t')[-last_few_pop_to_consider:]
            #     if is_last_few_fitness_same(min_stats):
            #         print('Defining new population')
            #         population = toolbox.population(n=500)
            #         starting_condition = gen + last_few_pop_to_consider

            if gen % 20 == 0:
                print('Defining new population after 20 gen')
                population = toolbox.population(n=NO_OF_POPULATION)

            gen += 1

    except KeyboardInterrupt:
        print(' Keyboard Interrupted')
    except Exception as error:
        print(error)
    finally:
        return population, logbook


def main(verbose=True):
    pset = create_primitive_set()
    toolbox = create_toolbox(pset)
    pop = toolbox.population(n=NO_OF_POPULATION)
    hof = detool.HallOfFame(1)

    pop, log = my_eaSimple(pop, toolbox, 0.8, 0.2, 100, stats=get_rdd_stats(), halloffame=hof,
                           verbose=verbose)

    print('Best individual : ', hof[0], hof[0].fitness)
    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main()
    save_halloffame(hof)
