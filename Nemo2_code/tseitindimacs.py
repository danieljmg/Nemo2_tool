'''
    File name: tseitindimacs.py
    Author: Daniel-Jesus Munoz
    Date created: 30/11/2022
    Python Version: 3.11.
    Description: It constructs the Tseitin CNF DIMACS file.
'''

from z3 import *
def main(booleanmodelname, bitvarsmap, file_vars, f, varcounter, initvars, maxrange, subgoal, initconstraints, booleanvarsids):

##### Identify true variables #####
        for bitvar in bitvarsmap:
            ##### Look for type and width #####
            for auxvardefs in file_vars:
                ##### Matching current with declared variables #####
                if auxvardefs[0] == bitvar:
                    auxvardef = auxvardefs
            if auxvardef[2] != 'boolean':
                ##### NF => #Bits IDs, Boolean Fs are treated later on #####
                for bit in range(1, auxvardef[1] + 1):
                    # print(f"c {varcounter} {bitvar}_{bit}")
                    f.write(f"c {varcounter} {bitvar}_{bit}")
                    f.write("\n")
                    varcounter += 1
            #else:
            #    print(varcounter)
            #    print(bitvar)
            #    f.write(f"c {varcounter} {bitvar}")
                #varcounter += 1

        ##### To calculate Tseitin Variables, we parse the transformation looking for the largest feature ID #####
        aux_vars_z3 = z3util.get_vars(subgoal.as_expr())
        num_vars = 0
        for aux_counter in aux_vars_z3:
            if '!' in str(aux_counter):
                current_aux = int(str(aux_counter).split('!')[1]) + 1
                if num_vars < current_aux:
                    num_vars = int(current_aux)
        # print(num_vars)

        ##### We now identify Tseitin variables in the 'c' section of the DIMACS file #####
        tseitincounter = 1
        if varcounter < (num_vars + initvars):
            for totalvarsid in range(varcounter, num_vars + initvars):
                # print(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
                f.write(f"c {totalvarsid} Tseitin_Variable_{tseitincounter}")
                f.write("\n")
                tseitincounter += 1
        else:
            totalvarsid = varcounter - 1

        ##### Boolean vars are always defined at the end (if they were not predefined in a base model) => Last IDs #####
        for bitvar in bitvarsmap:
            ##### Look for type and width #####
            for auxvardefs in file_vars:
                ##### Matching current with declared variables #####
                if auxvardefs[0] == bitvar:
                    auxvardef = auxvardefs
            if auxvardef[2] == 'boolean':
                ##### Count and register new boolean features #####
                if auxvardef[1] == 0:
                    totalvarsid += 1
                    f.write(f"c {totalvarsid} {bitvar} boolean")
                    f.write("\n")
                    booleanvarsids.append([bitvar, totalvarsid])
                ##### Register the proper ID of an already defined in the extending model boolean feature #####
                else:
                    booleanvarsids.append([bitvar, auxvardef[1]])

        ##### Write the main header in the 'p' section of the DIMACS file #####
        # print(f"p cnf {numvars} {maxrange}")
        f.write(f"p cnf {totalvarsid} {maxrange + initconstraints}")
        f.write("\n")

        ##### Add clauses of the extending model if extending one #####
        if (booleanmodelname):
            with open(booleanmodelname) as input_file:
                input_file_content = input_file.read().splitlines()
                for input_line in input_file_content:
                    if input_line[0:4] != "def " and input_line[0:2] != "c " and input_line[0:2] != "p ":
                        f.write(input_line)
                        f.write("\n")
        # print(booleanvarsids)
        print(str(subgoal[0]))
        ##### Transform Z3 output to DIMACS CNF NFM #####
        for c in range(maxrange):
            aux = str(subgoal[0][c]).replace("Or(", "")
            aux = aux.replace("\n  ", "")
            aux = aux.replace("k!", "")
            aux = aux.replace("Not(", "-")
            aux = aux.replace("))", "")
            aux = aux.replace(")", "")
            aux = aux.replace(",", "")

            ##### Adjust the variables IDs, as Z3 starts in 0, and DIMACS in 1 (larger init_id if extending a model) #####
            auxarray = aux.split(' ')
            updatedaux = ''
            for literalvar in auxarray:
                ##### HACK => prevent python considering -0 equivalent to 0 #####
                if (literalvar == '-0'):
                    updatedaux += str(f"-{initvars}") + ' '
                else:
                    ##### Adjust Z3 IDs considering the sign #####
                    if literalvar.lstrip("-").isnumeric():
                        numliteralvar = int(literalvar)
                        if numliteralvar < 0:
                            updatedaux += str(numliteralvar - initvars) + ' '
                        else:
                            updatedaux += str(numliteralvar + initvars) + ' '
                    else:
                        ##### All Z3 boolean features are transformed all at once in the next line #####
                        updatedaux += str(f"{literalvar}") + ' '

            ##### Replace Z3 boolean features by their DIMACS IDs #####
            for bv in booleanvarsids:
                updatedaux = updatedaux.replace(bv[0], str(bv[1]))
            # print(updatedaux+'0')

            ##### DIMACS clauses finish with a '0' #####
            f.write(updatedaux + '0')

            ##### Remove the last 'new line' if it is the last clause #####
            if (c < maxrange - 1): f.write("\n")