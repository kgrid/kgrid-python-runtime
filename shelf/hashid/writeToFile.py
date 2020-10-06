def writeToFile(input):
    file = open('./output.txt', 'w')
    file.write(input["content"])
    file.close()
    
    file = open('./output.txt','r')
    return(file.read())
