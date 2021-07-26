import math


def calculate_hypotenuse(json_input):
    return math.sqrt(math.pow(json_input['a'], 2) + math.pow(json_input['b'], 2))


def calculate_side(json_input):
    return math.sqrt(math.pow(json_input['c'], 2) - math.pow(json_input['a'], 2))
