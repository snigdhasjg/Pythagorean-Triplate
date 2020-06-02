from operator import attrgetter
from pyspark import SparkContext, RDD


def selRandom(sc: SparkContext, individuals: RDD, k):
    """Select *k* individuals at random from the input *individuals* with
    replacement. The list returned contains references to the input
    *individuals*.

    :param sc: pyspark.SparkContext
    :param individuals: A rdd of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A rdd of selected individuals.

    This function uses the :func:`~random.choice` function from the
    python base :mod:`random` module.
    """
    # return [random.choice(individuals) for i in range(k)]
    return sc.parallelize(range(k))\
        .flatMap(individuals.takeSample(False, 1))


def selTournament(sc: SparkContext, individuals: RDD, k, tournsize, fit_attr="fitness"):
    """Select the best individual among *tournsize* randomly chosen
    individuals, *k* times. The list returned contains
    references to the input *individuals*.

    :param sc: pyspark.SparkContext
    :param individuals: A rdd of individuals to select from.
    :param k: The number of individuals to select.
    :param tournsize: The number of individuals participating in each tournament.
    :param fit_attr: The attribute of individuals to use as selection criterion
    :returns: A rdd of selected individuals.

    This function uses the :func:`~random.choice` function from the python base
    :mod:`random` module.
    """
    # chosen = []
    # for i in range(k):
    #     aspirants = selRandom(individuals, tournsize)
    #     chosen.append(max(aspirants, key=attrgetter(fit_attr)))
    # return chosen
    return sc.parallelize(range(k)).repartition(5) \
        .flatMap(selRandom(sc, individuals, tournsize)
                 .max(key=attrgetter(fit_attr)))
