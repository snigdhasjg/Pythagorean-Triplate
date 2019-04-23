from TripletHelper import Generate_Triple, Input_Points

# ALL_POINTS = Input_Points.get_all_points()

ALL_POINTS = Generate_Triple.generate_list(40)

MY_INFINITY = 10000000000


def safe_div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


def safe_power(number, p, q):
    if p is not None and q is not None:
        try:
            power = number ** safe_div(p, q)
            if isinstance(power, complex):
                return MY_INFINITY
            return power
        except ZeroDivisionError:
            return 1
        except OverflowError:
            return MY_INFINITY
    return MY_INFINITY
