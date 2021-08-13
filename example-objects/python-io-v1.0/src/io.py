
def input_number(number):
    return "Your number is " + str(number)


def input_list(list_input):
    str_list = [str(i) for i in list_input]
    return "Your array is " + " ".join(str_list)


def input_dict(dict_input):
    return "Your dict is " + str(dict_input) + " the name in the dict is " + dict_input["name"]


def output_number(input):
    return 3


def output_list(input):
    return ["This", "is", "a", "list"]


def output_dict(input):
    return {"this": "dict"}

