# import Input_Points
import Generate_Triple

# ALL_POINTS = Input_Points.get_all_points()

ALL_POINTS = Generate_Triple.generate_list(20)

MY_INFINITY = 1000000


def safe_div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


def safe_power(number, p):
    try:
        return number ** p
    except ZeroDivisionError:
        return 1
    except OverflowError:
        return MY_INFINITY


def safe_root(number, q):
    power = safe_power(number, safe_div(1, q))
    if isinstance(power, complex):
        return MY_INFINITY
    return power
