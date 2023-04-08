import math
from sympy import *
from random import *

def function_eval(function, variables, point):
    output = function
    for v in variables:
            output = output.subs(v, point[v])

    return output


def initial_mover(constraint, variables, initial, epsilon, t_var):
    gradient = gradient_gen(variables, constraint)
    num_grad = gradient_eval(variables, gradient, initial, epsilon)
    stepping_function = stepping_function_gen(initial, num_grad, constraint, variables)
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
            print("No feasible region available.")
            return None

        if constriction > 0:
            continue
        else:
            initial = initial_mover(constraint, variables, initial, epsilon, t_var)
            count = 0

    print(initial)
    return initial


def gradient_gen(variables, function):
    gradient = {}
    for var in variables:
        gradient[var] = function.diff(var)

    return gradient


def constraint_check(constraints, solution, variables):
    feasible = True
    for constraint in constraints:
        if function_eval(constraint, variables, solution) <= 0:
            feasible = False

    return feasible


def gradient_eval(variables, gradient, current, epsilon):
    num_grad = {}

    for var in variables:
        grad = function_eval(gradient[var], variables, current)
        if abs(grad) < epsilon:
            num_grad[var] = 0
        else:
            num_grad[var] = grad

    return num_grad


def stepping_function_gen(current, num_grad, function, variables):
    new_sol = {}
    t_var = Symbol("t_var")

    for var in current:
        new_sol[var] = current[var] + t_var * num_grad[var]

    stepping_function = function

    for var in variables:
        stepping_function = stepping_function.subs(var, new_sol[var])

    return stepping_function


def mover_function(variables, num_grad, current, stepping_function, constraints):
    t_var = Symbol("t_var")
    t_step = stepping_function.diff(t_var)
    t_star = solveset(t_step, t_var)

    potential = {}

    for var in variables:
        potential[var] = 0

    if len(t_star) > 1:
        optimal = 0
        for t in t_star:
            if stepping_function.subs(t_var, t).is_real:
                if stepping_function.subs(t_var, t) > stepping_function.subs(t_var, optimal):
                    for var in variables:
                        potential[var] = current[var] + t * num_grad[var]
                    
                    if constraint_check(constraints, potential, variables):
                        optimal = t

                    for var in variables:
                        potential[var] = 0

        t_star = float(optimal)
    else:
        t_star = float(t_star.args[0])

    for var in variables:
        current[var] += t_star * num_grad[var]

    return current


def gradient_search(variables, function, current, epsilon, constraints, r_value):
    gradient = gradient_gen(variables, function)
    next = {}
    
    for I in current:
        next[I] = float(f"{current[I]}")  

    num_grad = gradient_eval(variables, gradient, current, epsilon)
    
    stop = True
    for var in variables:
        if abs(num_grad[var]) > epsilon:
            stop = False
    if stop:
        return current
    
    stepping_function = stepping_function_gen(next, num_grad, function, variables)
    next = mover_function(variables, num_grad, next, stepping_function, constraints)

    for var in variables:
        if distance_traveled(variables, current, next) < epsilon * (r_value + epsilon):
            return next

    print(next)

    return gradient_search(variables, function, next, epsilon, constraints, r_value)


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


def p_function_gen(constraints, objective, r_value):
    p_function = objective

    for constraint in constraints:
        p_function -= r_value/constraint

    return p_function


def distance_traveled(variables, current, next):
    square_length = 0

    for var in variables:
        square_length += (current[var] - next[var])**2

    length = sqrt(square_length)

    return length


def SUMT(variables, epsilon, current, constraints, objective):
    r_value = 1
    p_function = p_function_gen(constraints, objective, r_value)

    while True:
        next = gradient_search(variables, p_function, current, epsilon, constraints, r_value)

        if distance_traveled(variables, current, next) < epsilon:
            current = next
            break

        r_value = r_value * 0.01
        p_function = p_function_gen(constraints, objective, r_value)
        current = next
        print(current)

    return current


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
    x = Symbol('x')
    y = Symbol('y')
    initial = initialization(constraints, variables, epsilon)
    # initial = {x:1,y:1}

    if initial != None:
        solution = SUMT(variables, epsilon, initial, constraints, objective)
        print(solution)



# functin = "x*y-1/(-x**2-y+3)-1/x-1/y"

# func = parse_expr(functin)

# gradient = gradient_gen(func.free_symbols, func)

# print(gradient)

# x = Symbol('x')
# y = Symbol('y')
# initial = {x:1,y:1}

# print(gradient_search([x,y], x*y-1/(3-x**2-y)-1/x-1/y, initial, 0.01, [3-x**2-y, x, y]))