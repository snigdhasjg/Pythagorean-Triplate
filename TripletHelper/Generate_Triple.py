import math
import random

RANGE = 50


def get_c(a, b):
    c_value = math.sqrt(a ** 2 + b ** 2)
    return round(c_value, 2)


def generate_triple(limit):
    number1 = random.randint(2, limit) + round(random.random(), 2)
    number2 = random.randint(2, limit) + round(random.random(), 2)
    number3 = get_c(number1, number2)

    return [number1, number2, number3]


def generate_list(size):
    triple_list = []
    for _ in range(size):
        triple_list.append(generate_triple(RANGE))

    return triple_list


if __name__ == '__main__':
    print(generate_list(20))
