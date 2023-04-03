import math
from sympy import *

input_fnctn = "x**2 + 2*y*x + 1"

par = parse_expr(input_fnctn)
print(par.free_symbols)

# str_par = ""

# for var in par.free_symbols:
#     str_par += str(var)

# str_par = sorted(str_par)
# par = []

# for var in str_par:
#     par.append(Symbol(var))

# print(str_par)

x, y = symbols("x y")
z = sympify(input_fnctn)
def gradient_search(variables, function, current):
    gradient = {}
    new_sol = {}
    for var in variables:
        gradient[var] = diff(function, var)

    d_var = Symbol("d_var")
    for var in current:
        new_sol[var] = current[var] + d_var * gradient[var]
    


z_diff = Derivative(z, x)
print(z_diff)
print(z_diff.doit())