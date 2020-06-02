from pyspark import SparkContext


def initRepeat(sc: SparkContext, func, n):
    """Call the function *container* with a generator function corresponding
    to the calling *n* times the function *func*.
    :param sc: pyspark.SparkContext
    :param func: The function that will be called n times to fill the
                 container.
    :param n: The number of times to repeat func.
    :returns: An instance of rdd filled with data from func.

    This helper function can be used in conjunction with a Toolbox
    to register a generator of filled containers, as individuals or
    population.

        >>> import random
        >>> from pyspark import SparkContext
        >>> sc = SparkContext('depack')
        >>> random.seed(42)
        >>> init_repeat(sc, random.random, 2) # doctest: +ELLIPSIS,
        ...                                    # doctest: +NORMALIZE_WHITESPACE
        [0.6394..., 0.0250...]

    See the :ref:`list-of-floats` and :ref:`population` tutorials for more examples.
    """
    # return container(func() for _ in range(n))
    return sc.parallelize(range(n)).repartition(5).map(func())
