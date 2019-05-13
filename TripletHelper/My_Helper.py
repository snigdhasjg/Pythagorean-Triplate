from TripletHelper import Generate_Triple, Input_Points
from pygame import mixer
import time

# ALL_POINTS = Input_Points.get_all_points()
LIST_SIZE = 200

ALL_POINTS = Generate_Triple.generate_list(LIST_SIZE)

MY_INFINITY = 10000000000


def safe_div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


def safe_power(number, p, q):
    if p is not None and q is not None:
        if p is q:
            return MY_INFINITY
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


def play_song():
    mixer.init()
    mixer.music.load("TripletHelper/song.mp3")
    mixer.music.play()
    time.sleep(5)
    mixer.music.fadeout(5000)
    time.sleep(5)
