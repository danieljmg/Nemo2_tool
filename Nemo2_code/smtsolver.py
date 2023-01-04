'''
    File name: smtsolver.py
    Author: Daniel-Jesus Munoz
    Date created: 30/11/2022
    Python Version: 3.11.
    Description: It creates the code and run the Z3/SMT solver parting from a Nemo Numerical Feature Model
'''

from optimisedparsing import readNFM
import time
def main(start):

    ##### Input model NFs initialisation #####
    file_vars = []
    file_cts = []
    filepath = input("Which is the model .txt to run?: ")
    #filepath = 'transformingmodel.txt'
    ##### Parse, adjust and optimise NFM #####
    (file_vars, file_cts) = readNFM(filepath, file_vars, file_cts)
    print(f'Defined features (Name, Adjusted_width, Type) = {file_vars}')
    print(f'Adjusted constraints = {file_cts}')

    ##### Create the SMT solver running code #####
    auxf = open("auxsmt.py", "w+")
    auxf.write("from z3 import *\n")
    auxf.write("def smtsolverexec():\n")
    auxf.write("    constraints = Then('simplify', 'bit-blast', 'tseitin-cnf', 'smt').solver()")

    ##### Registering the features #####
    for file_var in file_vars:
        if file_var[2] == 'boolean':
            auxf.write(f"\n    {file_var[0]} = Bool('{file_var[0]}')")
        elif 'constant_' in file_var[2]:
            constant_value = str(file_var[2]).split('_')[1]
            auxf.write(f"\n    {file_var[0]} = BitVecVal({constant_value}, {file_var[1]})")
        else:
            auxf.write(f"\n    {file_var[0]} = BitVec('{file_var[0]}', {file_var[1]})")

    ##### Define NFM constraints in Z3py format #####
    for file_ct in file_cts:
        auxf.write(f"\n    constraints.add({file_ct})")

    ##### Create the solutions file #####
    auxf.write(f"\n    f = open('smtsolutions.txt', 'w')")
    auxf.write(f"\n    numbersolutions = 0")
    auxf.write(f"\n    print('Calculating solutions:')")

    ##### A loop is needed to generate all solutions #####
    auxf.write(f"\n    while constraints.check() == sat:")
    auxf.write(f"\n        m = constraints.model()")
    auxf.write(f"\n        numbersolutions += 1")
    auxf.write(f"\n        print(str(numbersolutions))")
    auxf.write(f"\n        f.write(f'Solution number: '+str(numbersolutions)+'\\n')")
    #auxf.write(f"\n        print(m)")
    auxf.write(f"\n        f.write(str(m)+'\\n')")

    ##### Every new solution generated must be constrained in each loop iteration #####
    auxf.write(f"\n        constraints.add(Or(")
    allsols = ""
    for file_var in file_vars:
        allsols += f"{file_var[0]} != m[{file_var[0]}], "
    auxf.write(allsols[:-2])
    auxf.write(f"))")

    ##### Closing files and executing the dinamically generated code #####
    auxf.write(f"\n    f.close()")
    auxf.close()
    from auxsmt import smtsolverexec
    smtsolverexec()

    end = time.time() - start  # - 0.05
    print(f"\nTransformation and SMT solver time: {str(end).replace('.', ',')} seconds")