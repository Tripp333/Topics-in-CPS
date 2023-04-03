import math
from sympy import *

input_fnctn = "2*x*y+2*y-x**2-2*y**4"

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

variables = par.free_symbols
current = {}

for var in variables:
    current[var] = 0

x, y = symbols("x y")
z = sympify(input_fnctn)
def gradient_search(variables, function, current):
    gradient = {}
    new_sol = {}
    for var in variables:
        gradient[var] = diff(function, var)

    num_grad = {}

    for var in variables:
        num_grad[var] = gradient[var]
        for v in variables:
            try:
                num_grad[var] = num_grad[var].subs(v, current[v])
            except:
                pass

    t_var = Symbol("t_var")
    for var in current:
        new_sol[var] = current[var] + t_var * num_grad[var]

    stepping_function = function

    for var in variables:
        stepping_function = stepping_function.subs(var, new_sol[var])

    t_step = stepping_function.diff(t_var)
    t_star = solveset(t_step, t_var)

    if len(t_star) > 1:
        optimal = 0
        for t in t_star:
            if (stepping_function.subs(t_var, t), stepping_function.subs(t_var, optimal)):
                optimal = t
    

    return t_star

n = gradient_search(variables, par, current)
    
print(n)

