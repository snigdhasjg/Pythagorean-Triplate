from deap import tools
from pyspark import SparkContext, RDD


def varAnd(population: RDD, toolbox, cxpb, mutpb):
    # offspring = [toolbox.clone(ind) for ind in population]
    offspring = population.map(toolbox.clone)

    # Apply crossover and mutation on the offspring
    # for i in range(1, len(offspring), 2):
    #     if random.random() < cxpb:
    #         offspring[i - 1], offspring[i] = toolbox.mate(offspring[i - 1],
    #                                                       offspring[i])
    #         del offspring[i - 1].fitness.values, offspring[i].fitness.values

    crossover_offspring = offspring.zipWithIndex().map(lambda x: (x[1] / 2, x[0])) \
        .reduceByKey(lambda x, y: x + y) \
        .map(lambda x: [a for a in x[1]]) \
        .flatMap(lambda x: toolbox.mate(x, cxpb))

    # for i in range(len(offspring)):
    #     if random.random() < mutpb:
    #         offspring[i], = toolbox.mutate(offspring[i])
    #         del offspring[i].fitness.values

    mutated_offspring = crossover_offspring.map(lambda x: toolbox.mutate(x, mutpb))

    return mutated_offspring


overflow_error = []


def eaSimple(sc: SparkContext, toolbox, cxpb, mutpb, ngen, no_of_population, stats=None, halloffame: tools.HallOfFame = None,
             verbose=True):
    population: RDD = toolbox.population(sc=sc, n=no_of_population)
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
            offspring = toolbox.select(sc, population, population.count())

            # Vary the pool of individuals
            new_offspring = varAnd(offspring, toolbox, cxpb, mutpb)

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
                population = toolbox.population(sc=sc, n=no_of_population)

            gen += 1

    except KeyboardInterrupt:
        print(' Keyboard Interrupted')
    except Exception as error:
        print(error)
    finally:
        return population, logbook
