import math
from sympy import *
from random import *

input_fnctn = "2*x-x**2+3*y-y**2-1/(2-x-y)-1/x-1/y"
constraint_fnctns = ["x+y-5", "5-x", "5-y"]

par = parse_expr(input_fnctn)

constraints = []

for constraint in constraint_fnctns:
    constraints.append(parse_expr(constraint))

variables = par.free_symbols


def function_eval(function, variables, point):
    output = function
    for v in variables:
            output = output.subs(v, point[v])

    return output


def initial_mover(constraint, variables, initial, epsilon, t_var):
    gradient = gradient_gen(variables, constraint)
    num_grad = gradient_eval(variables, gradient, initial)
    stepping_function = stepping_function_gen(initial, num_grad, constraint)
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


def stepping_function_gen(current, num_grad, function):
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
    
    stepping_function = stepping_function_gen(current, num_grad, function)

    current = mover_function(variables, num_grad, current, stepping_function)

    return gradient_search(variables, function, current, epsilon)

n = initialization(constraints, variables, 0.01)


def constraint_gen(variables):
    while True:
        num_constraints = input("Please input number of constraints: ")

        try:
            num_constraints = int(num_constraints)
        except:
            print("Please input an integer value.")
            continue

        break

    print("Please input constraints of the form:")
    print("g(x) INEQUALITY constant")

    constraints = []

    for i in range(int(num_constraints)):
        while True:
            inequality = input()
            split_ineq = inequality.split(" ")

            if len(split_ineq) != 3:
                print("Please input constraint function of a valid form.")
                continue

            LHS = split_ineq[0]
            INEQUALITY = split_ineq[1]
            RHS = split_ineq[2]

            try:
                RHS = float(RHS)
            except:
                print("Please input constraint function of a valid form.")
                continue

            try:
                LHS = parse_expr(LHS)
            except:
                print("Please input constraint function of a valid form.")
                continue

            if INEQUALITY == '<' or INEQUALITY == '<=':
                constraint = RHS - LHS

            elif INEQUALITY == '>' or INEQUALITY == '>=':
                constraint = LHS - RHS

            else:
                print("Please input constraint function of a valid form.")
                continue

            break

        constraints.append(constraint)

    for var in variables:
        if var not in constraints:
            constraints.append(var)

    return constraints


if __name__ == '__main__':
    print("Exponentials should be of the form a**b, multiplication should use the * symbol, and quotient denominators should be put in parenthesis.")
    
    while True:
        objective = input("Please input objective function: ")
        
        try:
            objective = parse_expr(objective)
        except:
            print("Please input objective function of a valid form.")
            continue

        break

    variables = objective.free_symbols
    
    constraints = constraint_gen(variables)

    while True:
        epsilon = input("Default accepted error is 0.01. If a different one is needed, please input now. Otherwise press return: ")

        if epsilon == '':
            epsilon = 0.01

        else:
            try:
                epsilon = float(epsilon)
            except:
                print("Please input a valid error value.")
                continue

        break

    initial = initialization(constraints, variables, epsilon)
    print(initial)

    