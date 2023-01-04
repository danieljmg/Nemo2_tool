'''
    File name: mode.py
    Author: Daniel-Jesus Munoz
    Date created: 30/11/2022
    Python Version: 3.11.
    Description: It calculates the clauses-mode of a DIMACS file.
'''

def calculatemedian(filepath):
    with open(filepath) as input_file:
        input_file_content = input_file.read().splitlines()
    counter = 0
    vars = 0
    for input_line in input_file_content:
        if input_line[0:2] != 'c ' and input_line[0:2] != 'p ':
            counter += 1
            vars += len(input_line.replace(" 0","").split(' '))
    print(f"Clauses Length Median: {str(vars/counter).replace('.', ',')}")
