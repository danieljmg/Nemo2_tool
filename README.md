![NEMO2_LOGO](https://raw.githubusercontent.com/danieljmg/Nemo2_tool/main/nemo2logo.png)

# Nemo2 (Numbers, fEatures, MOdels, version 2)

Nemo2 is a boolean and numerical constraint language and tool with first-class support for numerical feature modeling based in a collaboration between Universidad de Malaga and University of Texas in Austin.

It is licensed under the [MIT license](https://github.com/danieljmg/Nemo2_tool/blob/master/LICENSE.txt).

For Nemo version 1, we refer stakeholders to its repository: https://github.com/danieljmg/Nemo_tool


## At a glance

Nemo2 support extending classic variability models with numerical features and arithmetic in the formats [**DIMACS**](https://logic.pdmi.ras.ru/~basolver/dimacs.html) and Universal Variability Language [**(UVL)**](https://leopard.tu-braunschweig.de/servlets/MCRFileNodeServlet/dbbs_derivate_00047673/Engelhardt_Thesis.pdf) 

***Numerical Feature Models*** (NFMs) must be defined in Nemo2 by using Nemo's modeling language in a *.txt* file.

Nemo2 transforms and optimize NFMs by means of Bit-Blasting into classic variability models which then are supported by any first-order logic reasoner.

Nemo2 outputs support three formats: a) a UVL model, b) a **propositional formula**, and c) a Tseitin’s *Conjunctive Normal Form* (CNF) **propositional formula**. 
Besides the transformed model, we make use of comment lines to identify each original feature name and domain (i.e., boolean or numerical) with their respectives bit-blasted features.

Nemo2 is a cross-platform tool that have been developed in Python 11.x.


## Supported Definitions

**Feature types**: boolean, natural and integers.

**Numerical definitions**: constant, ranges and enumerated.

**Constraint operations**: cross-tree constraints (equivalence, implication and negation), inequalities (e.g., greater or equal) and mathematical operators (e.g., multiplication). 



## Modeling Language

As one image is worth a thousand words, the following extended example shows most of the possibilities.

`def A bool 0    # 0 means new feature`  
`def B bool f8   # named in adjunt FM as f8`  
`def C bool 0`  
`def D_unsigned [0:1]`  
`def E_unsigned [0:3]`  
`def F_signed [-1:1]`  
`def G_enum_signed [-9, -3, 0, 3]`  
`def H_constant [-2]`
`ct  C -> B`
`ct  A -> (G = 0)`  
`ct  A or B`  
`ct (G_enum_signed*H_constant) ≤ E_unsigned`

Real world models pre and post transformation are to be found in the examples folder.



## Installation

Nemo has been tested in Python 3.11 x86_64 at the moment, with up-to-date libraries (`pycosat`, `files`,  `re` and `z3py` modules must be installed). 

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

1. *Do you want to run the model in the Z3 SMT solver (y)?* Answer `y` to run the model in the Z3 SMT solver. The enumerated generated solutions are written in the *smtsolutions.txt* file.
2. *Do you want to transform the model into UVL (uvl), classic PF (pf), or Tseitin DIMACS (td)?* The three options bit-blast the mode. Answer `uvl` to transform it into a UVL with .uvl extension. Answer `pf` to transform it into a classic proposional formula with .txt extension. Answer `td` to transform it into a Tseitin's CNF proposional formula with .dimacs extension.
   1. *Which is the model .txt to transform?* You must write the path/name of the *.txt* file. If in the same folder, just the name is necessary.
   2. *If you are extending a DIMACS model, please write its name, BLANK otherwise*. You must write the path/name of the *.dimacs* file to evolve. If in the same folder, just the name is necessary. If you are not evolving, press Enter.
   3. The transformed model is available in the *transformedmodel.{uvl/txt/dimacs}* file.

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

Besides common Python modules, Nemo makes use of the tactics functionality of [Z3py](https://github.com/Z3Prover), as means to base its transformations in a solid library. Tactics is a side functionality, do not confuse it with the Z3 SMT solver. Additional corrections and pre-processing optimizations are encoded aside the library; any Z3py modification had occurred and all credits and issues are referred to [its github page](https://github.com/Z3Prover/z3). 
