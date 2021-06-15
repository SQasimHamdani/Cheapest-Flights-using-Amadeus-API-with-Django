# import csv
# from csv import reader

def read_cities(file_path):
    string_input = ""
    f = open(file_path, "r")
    string_input = f.read()

    cites = []
    for line in string_input.split("\n"):
        if len(line)>1 and len(line) <= 3:

            cites.append(line)
    return cites


