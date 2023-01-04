'''
    File name: optimisedparsing.py
    Author: Daniel-Jesus Munoz
    Date created: 30/11/2022
    Python Version: 3.11.
    Description: It optimises and transforms into Z3 code a Nemo Numerical Feature Model
'''
def readNFM(filepath, vars, cts):
    with open(filepath) as input_file:
        input_file_content = input_file.read().splitlines()

    ##### Let's keep the constraints in memory for future usages (e.g., optimisations) #####
    aux_file_cts = []
    for input_line in input_file_content:
        if 'ct' == input_line[:2]:
            aux_file_cts.append(input_line[2:])
    increased_bit = []

    ##### Iterate every line of the transforming model #####
    for input_line in input_file_content:
        #print(input_line)

        ##### If it is a variable definition... #####
        if 'def' == input_line[:3]:

            ##### Debugging details begin #####
            ##### Check if involved in signed ops #####
            signed = False
            # for aux_file_ct in aux_file_cts:
            #    name_file_var = input_line.split(' ')[1]
            #    if(name_file_var in aux_file_ct) and ((' / ' in aux_file_ct) or (' % ' in aux_file_ct)):
            #        signed = True
            #        break
            ##### Debugging details end #####

            ##### Registering boolean features ('feature name', bit-width, feature type) #####
            if ' bool ' in input_line:
                boolvardef = input_line.split(' ')
                vars.append([boolvardef[1], int(boolvardef[3]), 'boolean'])

            ##### Registering NFs with a ranged definition #####
            elif ':' in input_line:


                ##### Retrieve the range of this number defition to calculate the sign and width #####
                var_sign = ''
                w = 0
                var_ranges = input_line.split('def ')[1].split(' [')
                rrange = var_ranges[1][:-1].split(':')

                ##### Empty limit is by default 0 #####
                if rrange[0] == '': rrange[0] = '0'
                if rrange[1] == '': rrange[1] = '0'

                ##### Converts String List to a Int List #####
                rrange = list(map(int, rrange))

                ##### We are dealing with a signed ranged NF #####
                if signed or rrange[0] < 0:

                    var_sign = 'signed'
                    if abs(rrange[1]) >= abs(rrange[0]) - 1:
                        ##### Two's complement where the top limit is the bigger number #####
                        w = rrange[1].bit_length() + 1
                    else:
                        ##### Two's complement where the bottom limit is the bigger number e.g.: [-7:3] #####
                        w = (rrange[0] + 1).bit_length() + 1

                    ##### HACK: To prevent literal removal if within width, we add an extra bit #####
                    if (abs(rrange[0]) / (2 ** (w - 1)) == 1.0) and ((abs(rrange[1]) + 1) / (2 ** (w - 1)) == 1.0):
                        w += 1
                        ##### HACK: We register the increased bits as a record to prevent unnecessary future bit-width extensions #####
                        increased_bit += var_ranges[0]

                    ##### Add constraint if the bottom range is not Pw(2) #####
                    if (abs(rrange[0]) / (2 ** (w - 1)) != 1.0):
                        ##### More efficient constraint #####
                        cts.append(f'{var_ranges[0]} > {rrange[0] - 1}')
                    else:
                        cts.append(f'{var_ranges[0]} >= {rrange[0]}')
                        # w += 1

                    ##### Add constraint if the top range is not Pw(2) #####
                    if ((abs(rrange[1]) + 1) / (2 ** (w - 1)) != 1.0):
                        ##### More efficient constraint #####
                        cts.append(f'{var_ranges[0]} < {rrange[1] + 1}')
                    else:
                        cts.append(f'{var_ranges[0]} <= {rrange[1]}')
                    # w += 1

                ##### We are dealing with an unsigned ranged NF #####
                else:
                    var_sign = 'unsigned'

                    w = rrange[1].bit_length()

                    ##### HACK: Temporary HACKS Adjustments, inclusing HiPac #####
                    if (var_ranges[0] == 'Blocksize' or var_ranges[0] == 'Padding'):
                        w += 1

                    if rrange[0] != '' and rrange[0] > 0:
                        ##### More efficient constraint #####
                        cts.append(f'{var_ranges[0]} > {rrange[0] - 1}')
                    else:
                        ##### Empty limit is by default 0 #####
                        cts.append(f'{var_ranges[0]} >= 0')
                        # w += 1

                    if w > 1 and ((rrange[1] + 1) / (2 ** w) != 1.0):
                        ##### More efficient constraint #####
                        cts.append(f'{var_ranges[0]} < {rrange[1] + 1}')
                    ##### HACK: To prevent literal removal if within width, we add an extra bit if starts on ZERO and is within the limits #####
                    # elif (rrange[0] == 0):
                    #     w += 1
                    #     cts.append(f'{var_ranges[0]} < {rrange[1] + 1}')
                    #     ##### HACK: We register the increased bits as a record to prevent unnecessary future bit-width extensions #####
                    #     increased_bit += var_ranges[0]
                    ##### It is within the upper limit, but as it does not start in ZERO, there is no necessity of a hack #####
                    else:
                        cts.append(f'{var_ranges[0]} <= {rrange[1]}')
                        # w += 1

                ##### Whether signed or unsigned, variable definition is registered, range constraints were previously added #####
                vars.append([var_ranges[0], w, var_sign])

            ##### Registering NFs with enumerated definition #####
            elif ',' in input_line:

                ##### Retrieve the range of this number definition to calculate the sign and width #####
                var_sign = ''
                w = 0
                var_ranges = input_line.split('def ')[1].split(' [')
                var_values = var_ranges[1][:-1].split(',')

                ##### Converts String List to a Int List #####
                var_values = list(map(int, var_values))

                ##### Add enumerated constraints (NFa = 1 or NFa = 4 or...) #####
                aux_constraint = 'Or('
                for var_value in var_values:
                    aux_constraint += f'{var_ranges[0]} == {var_value}, '
                cts.append(aux_constraint[:-2] + ')')

                ##### Initialise absolute bottom and top values #####
                rrange = ["", ""]
                rrange[0] = var_values[0]
                rrange[1] = var_values[-1]

                ##### We are dealing with a signed enumerated NF #####
                if signed or rrange[0] < 0:
                    var_sign = 'signed'
                    if abs(rrange[1]) >= abs(rrange[0]) - 1:
                        ##### Two's complement where the top limit is the bigger number #####
                        w = rrange[1].bit_length() + 1
                    else:
                        ##### Two's complement where the bottom limit is the bigger number e.g.: [-7:3] #####
                        w = (rrange[0] + 1).bit_length() + 1

                ##### We are dealing with an unsigned enumerated NF #####
                else:
                    var_sign = 'unsigned'
                    w = rrange[1].bit_length()

                ##### Whether signed or unsigned, variable definition is registered, enumerated constraints were previously added #####
                vars.append([var_ranges[0], w, var_sign])

            ##### Registering NFs with constant definition #####
            else:
                var_sign = ''
                w = 0
                var_ranges = input_line.split('def ')[1].split(' [')
                var_value = int(var_ranges[1][:-1])

                ##### We are dealing with a signed constant NF #####
                if var_value >= 0:
                    w = var_value.bit_length()

                ##### We are dealing with an unsigned constant NF #####
                else:
                    w = var_value.bit_length() + 1
                var_sign = f'constant_{var_value}'

                ##### Whether signed or unsigned, variable definition is registered, no extra constraints are needed #####
                vars.append([var_ranges[0], w, var_sign])

        ##### Registering constraints #####
        elif 'ct' == input_line[:2]:
            cts.append(input_line.split('ct ')[1])

    #####

    ##### Adjuts variables widths based on operations out-of-bound #####
    for i, var_check_a in enumerate(vars):

        if var_check_a[2] != 'boolean':
            pluses = 0
            mults = 0

            ##### Check if the width has already been increased #####
            reduce_one = 0
            if (var_check_a[0] in increased_bit):
                reduce_one = 1

            ##### One more per '+' (it can be optimise) #####
            ##### Over one mult we need ((N+1) times * (width - extra_prevention_bit)) #####
            for aux_file_ct in aux_file_cts:
                ##### Searching for the largest repetition of each operation (it must be improved considering parenthesis) #####
                if (var_check_a[0] in aux_file_ct):
                    aux_pluses = aux_file_ct.count("+")
                    aux_mults = aux_file_ct.count("*")
                    if aux_pluses > pluses:
                        pluses = aux_pluses
                    if aux_mults > mults:
                        mults = aux_mults

            ##### We must check their implications choosing the largest from the two #####
            if (pluses > 0) and (mults > 0):
                ##### Already extended width is considered (reduce_one) #####
                int_var = int(vars[i][1]) - reduce_one
                new_width_pluses = int_var + pluses
                new_width_mults = int_var * (mults + 1)
                if new_width_pluses >= new_width_mults:
                    vars[i][1] = new_width_pluses
                else:
                    vars[i][1] = new_width_mults
            elif (pluses > 0):
                ##### Already extended width is considered (reduce_one) #####
                vars[i][1] = int(vars[i][1]) + pluses - reduce_one
            elif (mults > 0):
                ##### Already extended width is considered (reduce_one) #####
                vars[i][1] = (int(vars[i][1]) - reduce_one) * (mults + 1)

    #####

    ##### Adjust variables widths between variables sharing constraints; the largest width must be the general width of those variables #####
    for i, var_check_a in enumerate(vars):
        if(var_check_a[2] != 'boolean') and (var_check_a[0] != 'PixelPerThread'):
            for ct in cts:
                for j, var_check_b in enumerate(vars):
                    ##### Small temporary HACK #####
                    if (var_check_b[2] != 'boolean') and (var_check_b[0] != 'PixelPerThread'):
                        if (var_check_a[0] in ct) and (var_check_b[0] in ct):
                            ##### Adjusting signs first #####
                            if (var_check_a[2] == 'signed') and (var_check_b[2] == 'unsigned'):
                                vars[j][2] = 'signed'
                            elif (var_check_b[2] == 'signed') and (var_check_a[2] == 'unsigned'):
                                vars[i][2] = 'signed'
                            if int(var_check_a[1]) > int(var_check_b[1]):
                                vars[j][1] = vars[i][1]
                            elif int(var_check_b[1]) > int(var_check_a[1]):
                                vars[i][1] = vars[j][1]

    #####

    ##### Optimise operations for unsigned OPs #####
    for i, ct in enumerate(cts):

        ##### Double checking if all variables are unsigned #####
        unsigned_op = -1
        for var_check in vars:
            if (var_check[0] in ct) and (var_check[2] == 'unsigned'): unsigned_op = 1

        ##### Tranforms all the operations to the alternative unsigned ones #####
        while unsigned_op == 1 and (' < ' in ct or ' > ' in ct or ' >= ' in ct or ' <= ' in ct or ' / ' in ct or ' % ' in ct):
            #print(ct)
            if ' / ' in ct:
                ct = ct.split(' / ')
                prev = ct[0][::-1].find('(')
                post = ct[1].find(')')
                if prev and post:
                    cts[i] = f"{ct[0][:-prev]}UDiv({ct[0][-prev:]}, {ct[1][:post]}){ct[1][post:]}"
                elif prev:
                    cts[i] = f"{ct[0][:-prev]}UDiv({ct[0][-prev:]}, {ct[1]})"
                elif post:
                    cts[i] = f"UDiv({ct[0]}, {ct[1][:post]}){ct[1][post:]}"
                else:
                    cts[i] = f"UDiv({ct[0]}, {ct[1]})"
            elif ' % ' in ct:
                ct = ct.split(' % ')
                prev = ct[0][::-1].find('(')
                post = ct[1].find(')')
                if prev and post:
                    cts[i] = f"{ct[0][:-prev]}URem({ct[0][-prev:]}, {ct[1][:post]}){ct[1][post:]}"
                elif prev:
                    cts[i] = f"{ct[0][:-prev]}URem({ct[0][-prev:]}, {ct[1]})"
                elif post:
                    cts[i] = f"URem({ct[0]}, {ct[1][:post]}){ct[1][post:]}"
                else:
                    cts[i] = f"URem({ct[0]}, {ct[1]})"
            elif ' < ' in ct:
                ct = ct.split(' < ')
                cts[i] = f"ULT({ct[0]}, {ct[1]})"
            elif ' > ' in ct:
                ct = ct.split(' > ')
                cts[i] = f"UGT({ct[0]}, {ct[1]})"
            elif ' >= ' in ct:
                ct = ct.split(' >= ')
                cts[i] = f"UGE({ct[0]}, {ct[1]})"
            elif ' <= ' in ct:
                ct = ct.split(' <= ')
                cts[i] = f"ULE({ct[0]}, {ct[1]})"
            ct = cts[i]
            #print(ct)

    #####

    ##### Translate Boolean ops to Z3 format (IF for future versions) #####
    for i, ct in enumerate(cts):
        if ' -> ' in ct:
            ct = ct.split(' -> ')
            cts[i] = f"Implies({ct[0]}, {ct[1]})"
        elif ' <-> ' in ct:
            ct = ct.split(' <-> ')
            cts[i] = f"({ct[0]}) == ({ct[1]})"
        elif ' Or ' in ct:
            ct = ct.split(' Or ')
            cts[i] = f"Or({ct[0]}, {ct[1]})"
        elif ' And ' in ct:
            ct = ct.split(' And ')
            cts[i] = f"And({ct[0]}, {ct[1]})"

    #####

    ##### Optimise for implicit bit-width constraints deleting them (avoid redundancy) + HACK preventing Z3's literal erasal #####
    for var_optimise in vars:
        toerase = []

        ##### Count in how many constraints this variable appears, in order to leave AT LEAST ONE constraint #####
        var_times = 0
        for j in cts:
            if var_optimise[0] in j:
                var_times += 1

        ##### Checking width unsigned constraints to erase #####
        if var_optimise[2] == 'unsigned':
            toerases = [f'UGE({var_optimise[0]}, 0)', f'UGT({var_optimise[0]}, 1)',
                        f'ULE({var_optimise[0]}, {(2 ** var_optimise[1]) - 1})',
                        f'ULT({var_optimise[0]}, {(2 ** var_optimise[1])})']
            for toerase in toerases:
                for i, ct_eval in enumerate(cts):
                    if var_times > 1 and toerase == ct_eval:
                        del cts[i]
                        var_times -= 1

        ##### Checking width signed constraints to erase #####
        elif var_optimise[2] == 'signed':
            toerases = [f'{var_optimise[0]} >= -{(2 ** (var_optimise[1] - 1)) - 1}', f'{var_optimise[1]} > -{(2 ** (var_optimise[1] - 1))}',
                        f'{var_optimise[0]} <= {(2 ** (var_optimise[1] - 1)) - 1}',
                        f'{var_optimise[0]} < {(2 ** (var_optimise[1] - 1))}']
            for toerase in toerases:
                for i, ct_eval in enumerate(cts):
                    if var_times > 1 and toerase == ct_eval:
                        del cts[i]
                        var_times -= 1
    return (vars, cts)