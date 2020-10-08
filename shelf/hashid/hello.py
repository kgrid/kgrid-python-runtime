def hello(json_input):
    return f'Welcome to Knowledge Grid, {json_input["name"]}. \n Happy {json_input["age"]}{get_age_suffix(json_input["age"])} birthday!'


def get_age_suffix(age):
    if str(age)[-1:] == '1':
        return 'st'
    if str(age)[-1:] == '2':
        return 'nd'
    if str(age)[-1:] == '3':
        return 'rd'
    return 'th'
