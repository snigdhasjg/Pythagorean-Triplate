import math
import random


def get_c(a, b):
    c_value = math.sqrt(a ** 2 + b ** 2)
    return round(c_value, 4)


def generate_triple(limit):
    number1 = random.randint(2, limit)
    number2 = random.randint(2, limit)
    number3 = get_c(number1, number2)

    return [number1, number2, number3]


def generate_list(size):
    triple_list = []
    for _ in range(size):
        triple_list.append(generate_triple(20))

    return triple_list


if __name__ == '__main__':
    print(generate_list(20))
