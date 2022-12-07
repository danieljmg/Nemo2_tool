![NEMO_LOGO](https://i.ibb.co/jW4JLDL/nemo.png)

# Nemo2 (Numbers, fEatures, MOdels, version 2)

Nemo2 is a boolean and numerical constraint language and tool with first-class support for numerical feature modeling based in a collaboration between Universidad de Malaga and University of Texas in Austin.

It is licensed under the [MIT license](https://github.com/danieljmg/Nemo2_tool/blob/master/LICENSE.txt).



## At a glance

The current version of Nemo transforms ***Numerical Feature Models*** (NFMs) into: a) an optimized Tseitin’s *Conjunctive Normal Form* (CNF) **propositional formula** by means of Bit-Blasting. Nemo is a cross-platform tool that have been developed in Python.

The input NFM must be specified using Nemo's modeling language in a *.txt* file.

The output is a [**DIMACS**](https://logic.pdmi.ras.ru/~basolver/dimacs.html) file. We make use of the comment lines 'c' to identify each feature and bit-blasted features and their original type -- boolean or numerical. DIMACS is SAT-based solvers ready format, including **#SATs** (i.e., **Model Counting**).



## Supported Definitions

**Feature types**: boolean, natural and integers.

**Numerical definitions**: constant, ranges and enumerated.

**Constraint operations**: cross-tree constraints (equivalence, implication and negation), inequalities (e.g., greater or equal) and mathematical operators (e.g., multiplication). 



## Modeling Language

As one image is worth a thousand words, the following extended example shows most of the possibilities. It represents the model <*(G or F) and ((A * B) > C) requires (F or (E = D))*>

`def A_constant [3]`  
`def B_natural [0:3] `  
`def C_natural_2 [:3]`  
`def D_integer [ -2:1]`  
`def E_enumerated_integer [-1, 2, 4, 8]`  
`def F_new_boolean bool 0 `  
`def G_predifined_boolean bool 23`  
`ct G_predifined_boolean or F_new_boolean`  
`ct (( A_constant * B_natural ) > C_natural ) ->`  
`( F_new_boolean Or ( E_enumerated_integer == D_integer ))`

Real world models pre and post transformation are to be found in the examples folder.



## Installation

Nemo has been tested in Python 3.8.1 x86_64 at the moment, with up-to-date libraries (`pycosat`, `files`,  `re` and `z3py` modules must be installed). 

To install pycosat in windows:

- Install Microsoft Build Tools for Visual Studio 16
  - Select: Workloads → C++ build tools.
  - Select only “Windows 10 SDK” (assuming the computer is Windows 10). To use MSVC cl.exe C / C++ compiler from the command line, additionally select the C++ build tools.
- `pip install pycosat`

To simply install Z3py:

`pip install z3-solver`

Now you can pull/download and run Nemo.



## Usage

Run `main.py`

You will be asked:

1. *Do you want to run the model in the Z3 SMT solver?* Answer `y` to run the model in the Z3 SMT solver. The enumerated generated solutions are written in the *smtsolutions.txt* file.
2. *Do you want to transform the model into DIMACS?* Answer `y` to transform the model into a Tseitin's CNF proposional formula in DIMACS format by means of bit-blasting.
   1. *Which is the model .txt to transform?* You must write the path/name of the *.txt* file. If in the same folder, just the name is necessary.
   2. *If you are extending a DIMACS model, please write its name, BLANK otherwise*. You must write the path/name of the *.dimacs* file to evolve. If in the same folder, just the name is necessary. If you are not evolving, press Enter.
   3. The transformed model is available in the *transformedmodel.dimacs* file.

At all cases, in the terminal are presented:

- Runtimes in seconds.
- Calculated *Defined features* following the (Name, Adjusted_width, Type) format.
- Calculated *Adjusted constraints* of the model.



## Test

The next tiny example is the definition of A + B >= C of 2-bits variables.

`def A [0:3]`  
`def B [0:3] `  
`def C [0:3]`  
`ct A + B >= c`

It must produce 54 different valid solutions.



## Contact Author and Code Management

1. **[Daniel-Jesus Munoz](https://github.com/danieljmg)**: [ITIS](https://www.uma.es/institutos-uma/info/118460/instituto-de-tecnologias-e-ingenieria-del-software/), [CAOSD](http://caosd.lcc.uma.es/), Dpt. LCC, Universidad de Málaga, Andalucía Tech, Spain

## Other Tool Authors

1. **Mónica Pinto**: [ITIS](https://www.uma.es/institutos-uma/info/118460/instituto-de-tecnologias-e-ingenieria-del-software/), [CAOSD](http://caosd.lcc.uma.es/), Dpt. LCC, Universidad de Málaga, Andalucía Tech, Spain

2. **Lidia Fuentes**: [ITIS](https://www.uma.es/institutos-uma/info/118460/instituto-de-tecnologias-e-ingenieria-del-software/), [CAOSD](http://caosd.lcc.uma.es/), Dpt. LCC, Universidad de Málaga, Andalucía Tech, Spain

## Publication Supporters

1. **[Don Batory](https://www.cs.utexas.edu/~dsb/)**: Department of Computer Science Austin, Texas, USA


   

## Credits

Besides common Python modules, Nemo makes use of the tactics functionality of a local compilation of [Z3py 4.8.8](https://github.com/Z3Prover/z3/issues/2775), as means to base its transformations in a solid library. Tactics is a side functionality, do not confuse it with the Z3 SMT solver. Additional corrections and pre-processing optimizations are encoded aside the library; any Z3py modification had occurred and all credits and issues are referred to [its github page](https://github.com/Z3Prover/z3). 
