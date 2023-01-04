'''
    File name: cnftrans.py
    Author: Daniel-Jesus Munoz
    Date created: 30/11/2022
    Python Version: 3.11.
    Description: It creates the code and run the Z3/SMT solver parting from a Nemo Numerical Feature Model
'''
def main(bbmodel):

    ##### Create the CNF transformation code #####
    auxf = open("auxcnf.py", "w+")
    auxf.write("from sympy.logic.boolalg import to_cnf \n")
    auxf.write("from sympy.core import symbols \n")
    auxf.write("def cnftrans():\n")

    ##### Find the largest bit-blasted feature ID #####
    maxfetid = -1
    for bbline in bbmodel:
        ksplits = str(bbline).split('k!')
        for ksplit in ksplits:
            numfet = ksplit.split(')')[0].split(',')[0]
            if numfet.isnumeric() and int(numfet) > int(maxfetid):
                maxfetid = numfet

    ##### Create the main sympy code #####
    maxfetid = int(maxfetid) + 1
    fetdefs = ''
    for fetid in range (0, maxfetid):
        fetdefs += 'k' + str(fetid) + ', '
    fetdefs = fetdefs[:-2]
    auxf.write(f"    {fetdefs} = symbols('{fetdefs}') \n")
    auxf.write(f"    sympyadapted = '' \n")


    auxf.write(f"    print(to_cnf(sympyadapted, True))")
    auxf.close()
    #print(bbmodel)

#pip install sympy
# from sympy.logic.boolalg import to_cnf
# from sympy.abc import a, b, c, d, e, f, g, h, i, j, k, l
# b = ~(a) &~(f) &~(~((~(k) |~((j |(h |i |~((~(i) |~(h)))) |~((~(j) |~((h |i |~((~(i) |~(h)))))))))))) &(~((~((h |i |j |k)) &~((d |e |f |g)))) |~((l |a |b |c))) &~(b) &~(c) &~(g)
# print(to_cnf(b))
# https://github.com/sympy/sympy/blob/master/sympy/abc.py