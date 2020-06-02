from pyspark import SparkContext, RDD


def varAnd(sc: SparkContext, population: RDD, toolbox, cxpb, mutpb):
    """Part of an evolutionary algorithm applying only the variation part
    (crossover **and** mutation). The modified individuals have their
    fitness invalidated. The individuals are cloned so returned population is
    independent of the input population.

    :param sc: pyspark.SparkContext
    :param population: A rdd of individuals to vary.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :returns: A rdd of varied individuals that are independent of their
              parents.

    The variation goes as follow. First, the parental population
    :math:`P_\mathrm{p}` is duplicated using the :meth:`toolbox.clone` method
    and the result is put into the offspring population :math:`P_\mathrm{o}`.  A
    first loop over :math:`P_\mathrm{o}` is executed to mate pairs of
    consecutive individuals. According to the crossover probability *cxpb*, the
    individuals :math:`\mathbf{x}_i` and :math:`\mathbf{x}_{i+1}` are mated
    using the :meth:`toolbox.mate` method. The resulting children
    :math:`\mathbf{y}_i` and :math:`\mathbf{y}_{i+1}` replace their respective
    parents in :math:`P_\mathrm{o}`. A second loop over the resulting
    :math:`P_\mathrm{o}` is executed to mutate every individual with a
    probability *mutpb*. When an individual is mutated it replaces its not
    mutated version in :math:`P_\mathrm{o}`. The resulting :math:`P_\mathrm{o}`
    is returned.

    This variation is named *And* beceause of its propention to apply both
    crossover and mutation on the individuals. Note that both operators are
    not applied systematicaly, the resulting individuals can be generated from
    crossover only, mutation only, crossover and mutation, and reproduction
    according to the given probabilities. Both probabilities should be in
    :math:`[0, 1]`.
    """
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
