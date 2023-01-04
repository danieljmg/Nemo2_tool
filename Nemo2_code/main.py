'''
    File name: main.py
    Author: Daniel-Jesus Munoz
    Date created: 30/11/2022
    Python Version: 3.11.
    Description: Mainfile of the tool that transform Numerical Feature Models into a CNF DIMACS file by means of Bit-Blasting (Nemo)
'''

from z3 import *
from optimisedparsing import readNFM
from mode import calculatemedian
import re

##### Debugging details begin #####
# set_option(verbose = 10)
# set_option(html_mode=False)
# set_option(trace = True)
# traces = ["tseitin_cnf_bug", "tseitin_cnf", "simplify", "before_search", "after_search", "asserted_formulas", "bv", "resolve_conflict", "set_conflict", "arith", "rewriter"]
# for tr in traces:
#    enable_trace(tr)
##### Debugging details end #####
set_option(max_args=100000000, max_lines=10000000, max_depth=100000000, max_visited=10000000)
import time
start = time.time()
filepath = 'transformingmodel.txt'
z3flag = input("Do you want to run the model in the Z3 SMT solver (y)?: ")
if z3flag != 'y': cnfflag = input("Do you want to transform the model into UVL (uvl), classic PF (pf), or Tseitin DIMACS (td)?: ")
# z3flag = 'n'
# cnfflag = 'y'

if z3flag == 'y':

    from smtsolver import main
    main(start)

elif (cnfflag == 'td') | (cnfflag == 'pf') | (cnfflag == 'uvl') :
    filepath = input("Which is the model .txt to transform?: ")
    filepath = 'transformingmodel.txt'

    booleanmodelname = input("If you are extending a DIMACS model, please write its name, BLANK otherwise: ")
    if (booleanmodelname): booleanmodelname = "" + ".dimacs"  # basemodel.dimacs"
    # booleanmodelname = ""

    ##### Initialise resulting file and the Z3 constraints variable #####
    modelname = "transformedmodel"
    if cnfflag == 'td': f = open(f"{modelname}.dimacs", "w")
    elif (cnfflag == 'pf'):
        fvars = open(f"VARS{modelname}.txt", "w")
        f = open(f"{modelname}.txt", "w")
    elif (cnfflag == 'uvl'):
        fvars = open(f"VARS{modelname}.txt", "w")
        f = open(f"{modelname}.uvl", "w")
    constraints = Goal()

    ##### Input model NFs initialisation #####
    file_vars = []
    file_cts = []


    ##### Parse, adjust and optimise NFM #####
    (file_vars, file_cts) = readNFM(filepath, file_vars, file_cts)
    print(f'Defined features (Name, Adjusted_width, Type) = {file_vars}')
    print(f'Adjusted constraints = {file_cts}')

    ##### Start generating the dynamic Z3 python module #####
    auxf = open("auxdefs.py", "w+")
    auxf.write("from z3 import *\n")
    auxf.write("def embeed(constraints):")
    ##### Dynamically define NFM variables in Z3py format #####
    for file_var in file_vars:
        if file_var[2] == 'boolean':
            auxf.write(f"\n    {file_var[0]} = Bool('{file_var[0]}')")
        elif 'constant_' in file_var[2]:
            constant_value = str(file_var[2]).split('_')[1]
            auxf.write(f"\n    {file_var[0]} = BitVecVal({constant_value}, {file_var[1]})")
        else:
            auxf.write(f"\n    {file_var[0]} = BitVec('{file_var[0]}', {file_var[1]})")

    ##### Dynamically define NFM constraints in Z3py format #####
    for file_ct in file_cts:
        auxf.write(f"\n    constraints.add({file_ct})")
    ##### Close the file and execute the dinamically generated code #####
    auxf.close()
    from auxdefs import embeed
    embeed(constraints)

    ##### Debugging details begin #####
    #p = ParamsRef()
    # params_to_false = ["elim_ite", "flat", "bit2bool", "algebraic_number_evaluator", "distributivity",  "common_patterns", "common_patterns", "ite_chaing", "ite_extra", "elim_and", "blast_distinct", "elim_sign_ext", "hi_div0", "ignore_patterns_on_ground_qbody", "push_to_real"]
    # params_to_false = ["elim_ite", "flat", "bit2bool", "algebraic_number_evaluator", "elim_and", "blast_distinct", "elim_sign_ext", "hi_div0", "ignore_patterns_on_ground_qbody", "push_to_real"]
    # for param in params_to_false:
    #    p.set(param, False)
    # p.set("distributivity_blowup", 0)

    # t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), distributivity=False)
    #t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), p)
    # t = WithParams(Then('simplify', 'bit-blast'), p)
    # print(t.__setattr__("distributivity", False))
    ##### Debugging details end #####

    ##### Tactics definition and assertion test #####
    p = ParamsRef()
    if cnfflag != 'td': t = WithParams(Then('simplify', 'bit-blast'), p)
    else: t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), p)
    #t = WithParams(Th en('simplify', 'bit-blast', 'tseitin-cnf'), p)

    subgoal = t(constraints)
    assert len(subgoal) == 1

    ##### Debugging details begin #####
    # auxbb = open("pbb.txt","w+")
    # for pbb in subgoal[0]:
    # auxbb.write(str(pbb))
    # auxbb.write(" and\n")
    # auxbb.close()
    #print(subgoal[0])
    ##### Debugging details end #####

    ##### subgoal[0] is the CNF PF #####
    maxrange = len(subgoal[0])

    ##### Initialise array to register the order in which the Features and bits are converted, in order to identify them later in the DIMACS file 'c' section #####
    bitvarsmap = []

    ##### Traverse each clause: If the model contain constraints ... #####
    for constraint in constraints:
        # print(constraint)
        ##### Remove parenthesis and negations as they are not necessary to calculate the order #####
        complexstrconstraint = str(constraint).replace('\n  ', '')
        complexstrconstraint = complexstrconstraint.replace('Not(', '')
        complexstrconstraint = complexstrconstraint.replace('(', '')
        complexstrconstraint = complexstrconstraint.replace(')', '')
        if 'Implies' == complexstrconstraint[0:7]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[7:].split(', ')
        elif 'UDiv' == complexstrconstraint[0:4]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[7:].split(', ')
        elif 'URem' == complexstrconstraint[0:4]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[7:].split(', ')
        elif 'Or' == complexstrconstraint[0:2]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[2:].split(', ')
        elif 'And' == complexstrconstraint[0:3]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[2:].split(', ')
        else:
            ##### Not a nested group of constraints => Nothing to split #####
            found_complex_ops = [complexstrconstraint]

        for strconstraint in found_complex_ops:
            if 'ULT' in strconstraint or 'UGE' in strconstraint:
                ##### Reverse Order #####
                found_ops = strconstraint[3:].split(', ')[::-1]
            elif " < " in strconstraint:
                ##### Reverse Order #####
                found_ops = strconstraint.split(' < ')[::-1]
            elif " >= " in strconstraint:
                ##### Reverse Order #####
                found_ops = strconstraint.split(' >= ')[::-1]
            elif " <= " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' <= ')
            elif " > " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' > ')
            elif " == " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' == ')
            elif " != " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' !=')
            elif 'ULE' in strconstraint or 'UGT' in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint[3:].split(', ')
            elif 'UDiv' in strconstraint or 'URem' in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint[4:].split(', ')
            else:
                ##### Not a nested group of constraints => Nothing to split #####
                found_ops = [strconstraint]

            ##### Group of arithmetic operations in sequential Order #####
            equation_vars = re.split(' \+ | - |\*|/|%', found_ops[0])
            if len(found_ops) > 1:
                ##### Register variables temporary #####
                equation_vars += re.split(' \+ | - |\*|/|%', found_ops[1])

            ##### Preventing duplicated variables #####
            for found_var in equation_vars:
                if not found_var.isnumeric() and found_var.replace(" ", "").replace("And", "").replace("Or", "").replace("UDiv", "").replace("URem", "") not in bitvarsmap: bitvarsmap.append(found_var.replace(" ", "").replace(" ", "").replace("And", "").replace("Or", "").replace("UDiv", "").replace("URem", ""))

    ##### Initialise var and clauses counters by means of 'c' identification, and copy the variables of the extending model (if exists) #####
    if (booleanmodelname):
        with open(booleanmodelname) as input_file:
            input_file_content = input_file.read().splitlines()
            for input_line in input_file_content:
                if 'c ' == input_line[0:2]:
                    f.write(input_line)
                    f.write("\n")
                elif 'p cnf ' == input_line[0:6]:
                    ##### New variables and constraints start to count from the extending count #####
                    vars_and_constraints = input_line[6:].split(' ')
                    initvars = int(vars_and_constraints[0]) + 1
                    initconstraints = int(vars_and_constraints[1])
                    break
    else:
        ##### Or we rather part from the first ids #####
        initvars = 1
        initconstraints = 0

    ##### Initialise the variables counter #####
    varcounter = initvars
    ##### Mapping of Boolean vars and their ids #####
    booleanvarsids = []
    # print(bitvarsmap)

    # DIMACS CONVERSION VERSION
    if cnfflag == 'uvl':

        import bitblasteduvl
        bitblasteduvl.main(bitvarsmap, file_vars, f, fvars, varcounter, initvars, maxrange, subgoal, initconstraints, booleanvarsids)

    elif cnfflag == 'td':

        import tseitindimacs
        tseitindimacs.main(booleanmodelname, bitvarsmap, file_vars, f, varcounter, initvars, maxrange, subgoal, initconstraints, booleanvarsids)

    # Propositional Formula CONVERSION VERSION
    elif cnfflag == 'pf':

        import bitblastedpf
        bitblastedpf.main(bitvarsmap, file_vars, f, fvars, varcounter, initvars, maxrange, subgoal, initconstraints, booleanvarsids)

    f.close()
    end = time.time() - start  # - 0.05
    print(f"Transformation time: {str(end).replace('.', ',')} seconds")
    calculatemedian(filepath)