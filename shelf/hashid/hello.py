def hello(input):
    return f'Welcome to Knowledge Grid, {input["name"]}. \n Happy {input["age"]}{getAgeSuffix(input["age"])} birthday!'
    
def getAgeSuffix(age):
    if str(age)[-1:] == '1':
        return 'st'
    if str(age)[-1:] == '2':
        return 'nd'
    if str(age)[-1:] == '3':
        return 'rd'
    return 'th'
