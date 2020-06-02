from bisect import bisect_right
from copy import deepcopy
from operator import eq

from pyspark import RDD


def identity(obj):
    """Returns directly the argument *obj*.
    """
    return obj


class Statistics(object):

    def __init__(self, key=identity):
        self.key = key

    def compile(self, data: RDD):
        """Apply to the input sequence *data* each registered function
        and return the results as a dictionary.

        :param data: Sequence of objects on which the statistics are computed.
        """
        # values = tuple(self.key(elem) for elem in data)
        values = data.map(lambda x: self.key(x))

        entry = dict()

        entry["avg\t"] = values.mean()
        entry["std\t"] = values.stdev()
        entry["min\t"] = values.min()
        entry["max\t"] = values.max()

        return entry


class MultiStatistics(dict):

    def compile(self, data):
        """Calls :meth:`Statistics.compile` with *data* of each
        :class:`Statistics` object.

        :param data: Sequence of objects on which the statistics are computed.
        """
        record = {}
        for name, stats in list(self.items()):
            record[name] = stats.compile(data)
        return record

    @property
    def fields(self):
        return sorted(self.keys())


class HallOfFame(object):
    """The hall of fame contains the best individual that ever lived in the
    population during the evolution. It is lexicographically sorted at all
    time so that the first element of the hall of fame is the individual that
    has the best first fitness value ever seen, according to the weights
    provided to the fitness at creation time.

    The insertion is made so that old individuals have priority on new
    individuals. A single copy of each individual is kept at all time, the
    equivalence between two individuals is made by the operator passed to the
    *similar* argument.

    :param maxsize: The maximum number of individual to keep in the hall of
                    fame.
    :param similar: An equivalence operator between two individuals, optional.
                    It defaults to operator :func:`operator.eq`.

    The class :class:`HallOfFame` provides an interface similar to a list
    (without being one completely). It is possible to retrieve its length, to
    iterate on it forward and backward and to get an item or a slice from it.
    """

    def __init__(self, maxsize, similar=eq):
        self.maxsize = maxsize
        self.keys = list()
        self.items = list()
        self.similar = similar

    def update(self, population: RDD):
        """Update the hall of fame with the *population* by replacing the
        worst individuals in it by the best individuals present in
        *population* (if they are better). The size of the hall of fame is
        kept constant.

        :param population: A list of individual with a fitness attribute to
                           update the hall of fame with.
        """
        if len(self) == 0 and self.maxsize != 0 and population.count() > 0:
            # Working on an empty hall of fame is problematic for the
            # "for else"
            self.insert(population.takeSample(False, 1))

        population.foreach(lambda ind: self._find_best_ind(ind))

    def _find_best_ind(self, ind):
        if ind.fitness > self[-1].fitness or len(self) < self.maxsize:
            for hofer in self:
                # Loop through the hall of fame to check for any
                # similar individual
                if self.similar(ind, hofer):
                    break
            else:
                # The individual is unique and strictly better than
                # the worst
                if len(self) >= self.maxsize:
                    self.remove(-1)
                self.insert(ind)

    def insert(self, item):
        """Insert a new individual in the hall of fame using the
        :func:`~bisect.bisect_right` function. The inserted individual is
        inserted on the right side of an equal individual. Inserting a new
        individual in the hall of fame also preserve the hall of fame's order.
        This method **does not** check for the size of the hall of fame, in a
        way that inserting a new individual in a full hall of fame will not
        remove the worst individual to maintain a constant size.

        :param item: The individual with a fitness attribute to insert in the
                     hall of fame.
        """
        item = deepcopy(item)
        i = bisect_right(self.keys, item.fitness)
        self.items.insert(len(self) - i, item)
        self.keys.insert(i, item.fitness)

    def remove(self, index):
        """Remove the specified *index* from the hall of fame.

        :param index: An integer giving which item to remove.
        """
        del self.keys[len(self) - (index % len(self) + 1)]
        del self.items[index]

    def clear(self):
        """Clear the hall of fame."""
        del self.items[:]
        del self.keys[:]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

    def __iter__(self):
        return iter(self.items)

    def __reversed__(self):
        return reversed(self.items)

    def __str__(self):
        return str(self.items)
