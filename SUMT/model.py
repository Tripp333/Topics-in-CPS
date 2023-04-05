import math
from sympy import *
from random import *

input_fnctn = "2*x-x**2+3*y-y**2-1/(2-x-y)-1/x-1/y"

par = parse_expr(input_fnctn)



variables = par.free_symbols
current = {}

for var in variables:
    current[var] = .5

def function_eval(function, variables, point):
    output = function
    for v in variables:
            try:
                output = output.subs(v, point[v])
            except:
                pass

    return output


def initial_mover(constraint, variables, initial, epsilon, t_var):
    gradient = gradient_gen(variables, constraint)
    num_grad = gradient_eval(variables, gradient, initial)
    stepping_function = stepping_function_gen(num_grad, constraint)
    t_star = solveset(Eq(stepping_function, epsilon), t_var)
    
    minimum = t_star.args[0]
    
    if len(t_star) > 1:
        for t in t_star:
            if stepping_function.subs(t_var, t) < stepping_function.subs(t_var, minimum):
                minimum = t

    for var in variables:
        initial[var] += num_grad[var] * minimum

    return initial


def initialization(constraints, variables, epsilon):
    count = 0
    feasibility_count = 0
    initial = {}
    t_var = Symbol("t_var")

    for var in variables:
        initial[var] = random()

    while True:
        if count == len(constraints):
            break

        constraint = constraints[count]
        constriction = function_eval(constraint, variables, initial)
        count += 1
        feasibility_count += 1

        if feasibility_count > len(constraints)*99:
            break

        if constriction > 0:
            continue
        else:
            initial = initial_mover(constraint, variables, initial, epsilon, t_var)
            count = 0

    return initial


def gradient_gen(variables, function):
    gradient = {}
    for var in variables:
        gradient[var] = diff(function, var)

    return gradient


def gradient_eval(variables, gradient, current):
    num_grad = {}

    for var in variables:
        num_grad[var] = function_eval(gradient[var], variables, current)

    return num_grad


def stepping_function_gen(num_grad, function):
    new_sol = {}
    t_var = Symbol("t_var")

    for var in current:
        new_sol[var] = current[var] + t_var * num_grad[var]

    stepping_function = function

    for var in variables:
        stepping_function = stepping_function.subs(var, new_sol[var])

    return stepping_function


def mover_function(variables, num_grad, current, stepping_function):
    t_var = Symbol("t_var")
    t_step = stepping_function.diff(t_var)
    t_star = solveset(t_step, t_var)

    if len(t_star) > 1:
        optimal = 0
        for t in t_star:
            if stepping_function.subs(t_var, t).is_real:
                if stepping_function.subs(t_var, t) > stepping_function.subs(t_var, optimal):
                    optimal = t
        t_star = optimal
    else:
        t_star = t_star.args[0]

    for var in variables:
        current[var] += t_star * num_grad[var]

    return current


def gradient_search(variables, function, current, epsilon):
    gradient = gradient_gen(variables, function)

    num_grad = gradient_eval(variables, gradient, current)
    
    stop = True
    for var in variables:
        if abs(num_grad[var]) > epsilon:
            stop = False
        print(num_grad[var])
    if stop:
        return current
    
    stepping_function = stepping_function_gen(num_grad, function)

    current = mover_function(variables, num_grad, current, stepping_function)

    return gradient_search(variables, function, current, epsilon)


n = gradient_search(variables, par, current, 0.01)
    
print(n)


