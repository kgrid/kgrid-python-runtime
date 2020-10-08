def write_to_file(json_input):
    file = open('./shelf/output/output.txt', 'w')
    file.write(json_input["content"])
    file.close()
    file = open('./shelf/output/output.txt', 'r')
    return file.read()
