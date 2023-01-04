'''
    File name: bitblasteduvl.py
    Author: Daniel-Jesus Munoz
    Date created: 30/11/2022
    Python Version: 3.11.
    Description: It constructs the UVL model file.
'''

from z3 import *
import re
def main(bitvarsmap, file_vars, f, fvars, varcounter, initvars, maxrange, subgoal, initconstraints, booleanvarsids):
    ### UVL Header ###
    f.write(f"features\n\tv0\n\t\toptional\n")

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
                fvars.write(f"c {varcounter} {bitvar}_{bit}")
                fvars.write("\n")

                f.write(f"\t\t\tv{varcounter}\n")

                varcounter += 1
        else:
            f.write(f"\t\t\t{auxvardef[0]}\n")
            # varcounter += 1

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
            fvars.write(f"c {totalvarsid} Tseitin_Variable_{tseitincounter}")
            fvars.write("\n")
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
                fvars.write(f"c {totalvarsid} {bitvar} boolean")
                fvars.write("\n")
                booleanvarsids.append([bitvar, totalvarsid])
            ##### Register the proper ID of an already defined in the extending model boolean feature #####
        else:
            booleanvarsids.append([bitvar, auxvardef[1]])

    ##### Write the main header in the 'p' section of the DIMACS file #####
    # print(f"p cnf {numvars} {maxrange}")
    fvars.write(f"p cnf {totalvarsid} {maxrange + initconstraints}")
    fvars.close()
    ##### Add clauses of the extending model if extending one #####
    # if (booleanmodelname):
    #    with open(booleanmodelname) as input_file:
    #        input_file_content = input_file.read().splitlines()
    #        for input_line in input_file_content:
    #            if input_line[0:4] != "def " and input_line[0:2] != "c " and input_line[0:2] != "p ":
    #                f.write(input_line)
    #                f.write("\n")
    # print(booleanvarsids)

    ##### Transform Z3 output to ULV NFM #####
    f.write(f"constraints\n\t")

    for c in range(maxrange):
        # print(subgoal[0][c])
        aux = str(subgoal[0][c]).replace("Or", "")
        ##### Replace Z3 boolean features by their DIMACS IDs #####
        aux = aux.replace("\n  ", "")
        ux = aux.replace("\t  ", "")
        aux = aux.replace("k!", "")
        aux = aux.replace("==", "<=>")
        # Must be - to readjust the variables numbers, replaced by ! later on
        aux = aux.replace("Not", "-")
        aux = aux.replace(",", " |")

        ### Remove parentheses surrounding numbers
        aux = re.sub(r'(\()([\d*\.]+)(\))', r"\2", aux)
        aux = " ".join(aux.split())
        # print(aux)
        ##### Adjust the variables IDs, as Z3 starts in 0, and DIMACS in 1 (larger init_id if extending a model) #####
        auxarray = aux.split(' ')
        updatedaux = ''
        for literalvar in auxarray:
            # print(literalvar)
            ##### Adjust Z3 IDs considering the sign #####
            auxarraynum = re.sub('.*?(-?[0-9]*)\)*?$', r'\1', literalvar)
            # print(f'{auxarraynum}')
            if auxarraynum.isnumeric() or (auxarraynum.startswith('-') and auxarraynum[1:].isnumeric()):
                # print(f'var:*{auxarraynum}*')
                numliteralvar = int(auxarraynum)
                if numliteralvar < 0:
                    # print("hola")
                    updatedaux += literalvar.replace(auxarraynum, "-v" + str(abs(int(numliteralvar - initvars)))) + ' '
                else:
                    updatedaux += literalvar.replace(auxarraynum, "v" + str(numliteralvar + initvars)) + ' '
            else:
                ##### All Z3 boolean features are transformed all at once in the next line #####
                updatedaux += str(f"{literalvar}") + ' '

        ##### Replace Z3 boolean features by their DIMACS IDs #####
        # for bv in booleanvarsids:
        #    updatedaux = updatedaux.replace(bv[0], str(bv[1]))
        # print(updatedaux+'0')

        # updateaux = updateaux.replace(",", " ||")
        # print(updatedaux)

        # readjust - by !
        updatedaux = updatedaux.replace("-", "!")

        ##### Write PF file #####
        f.write(updatedaux[:-1])

        ##### Remove the last 'new line' if it is the last clause #####
        if (c < maxrange - 1): f.write("\n\t")