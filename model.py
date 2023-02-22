#Topics in Optimization: 
#Computational Project
# Tripp Lawrence and Luke Lewis


def dummy_supply(costs, sent, supply_size, demand_size, dummy_size):
    sent[(supply_size, demand_size - 1)] = dummy_size

    dummy_cost = 100 * max([costs[arc] for arc in costs])
    
    for j in range(demand_size):
        costs[(supply_size, j)] = dummy_cost
    
    costs[supply_size] = True

    return costs, sent, dummy_size

def dummy_demand(costs: dict, sent: dict, supply_size, demand_size, dummy_size):
    sent[(supply_size - 1, demand_size)] = dummy_size

    dummy_cost = 100 * max([costs[arc] for arc in costs])
    
    for i in range(supply_size):
        costs[(i, demand_size)] = dummy_cost
    
    costs[demand_size] = False

    return costs, sent, dummy_size

def dummy_test(supplies: list, demands: list, costs, sent):
    supply = sum(supplies)
    demand = sum(demands)

    if supply == demand:
        return None
    
    elif supply > demand:
        return dummy_demand(costs, sent, supply_size, demand_size, supply - demand)

    else:
        return dummy_supply(costs, sent, supply_size, demand_size, demand - supply)


def initialization(supply_size, demand_size, supplies, demands, costs):
    sent = {} # Initialization of the dictionary that contains the amount of supply sent from source i to demand j
    supply_count = 0 #
    demand_count = 0 #
    dummy_size = 0

    while supply_count < supply_size and demand_count < demand_size:
        if supplies[supply_count] <= demands[demand_count]:
            sent[(supply_count, demand_count)] = supplies[supply_count]
            demands[demand_count] -= supplies[supply_count]
            supplies[supply_count] = 0
            supply_count += 1
        else:
            sent[(supply_count, demand_count)] = demands[demand_count]
            supplies[supply_count] -= demands[demand_count]
            demands[demand_count] = 0
            demand_count += 1

    solutions = dummy_test(supplies, demands, costs, sent)

    if solutions:
        costs = solutions[0]
        sent = solutions[1]
        dummy_size = solutions[2]

    return sent, costs, dummy_size

def compound_var(supply_size: int, demand_size: int, sent: dict, costs: dict):
    first_arc = (0,0)
    U = [0 for i in range(supply_size)]
    V = [0 for j in range(demand_size)]

    for arc in sent.keys():
        if arc[0] == 0:
            first_arc = arc

    U, V = row_col_finder(first_arc, list(sent.keys()), costs, supply_size, demand_size, U, V)
    return U, V

    
def row_col_finder(arc: tuple, keys: list, costs: dict, supply_size, demand_size, U, V):
    for j in range(demand_size):
        new_arc = (arc[0], j)
        if new_arc in keys:
            V[j] = costs[new_arc] - U[arc[0]]
            keys.remove(new_arc)
            U, V = row_col_finder(new_arc, keys, costs, supply_size, demand_size, U, V)

    for i in range(supply_size):
        new_arc = (i, arc[1])
        if new_arc in keys:
            U[i] = costs[new_arc] - V[arc[1]]
            keys.remove(new_arc)
            U, V = row_col_finder(new_arc, keys, costs, supply_size, demand_size, U, V)
    
    return U, V

def find_reduced_costs(costs: dict, U: list, V: list):
    reduced_matrix = {}

    for i in range(len(U)):
        for j in range(len(V)):
            reduced_matrix[(i, j)] = costs[(i, j)] - U[i] - V[j]

    return reduced_matrix

def optimality_test(reduced_matrix: dict):
    minimum_reduced_cost = 0
    minimum_arc = (0, 0)
    for reduced_arc in reduced_matrix.keys():
        if reduced_matrix[reduced_arc] < minimum_reduced_cost:
            minimum_reduced_cost = reduced_matrix[reduced_arc]
            minimum_arc = reduced_arc
    if minimum_reduced_cost >= 0:
        return True
    else:
        return minimum_arc

def find_row_cycle(cycle: list, keys: list, original_min_arc: tuple, potential_arc: tuple, supply_size, demand_size, cycle_size):
    if potential_arc in keys:
        keys.remove(potential_arc)


    for j in range(demand_size):
        new_row_arc = (potential_arc[0], j)
        if new_row_arc == original_min_arc and cycle_size > 1:
            cycle.append(potential_arc)
            return cycle
    
    for j in range(demand_size):
        new_arc = (potential_arc[0], j)
        if new_arc in keys and new_arc != potential_arc:
            cycle.append(potential_arc)
            cycle_size += 1
            keys.append(potential_arc)
            cycle = find_col_cycle(cycle, keys, original_min_arc, new_arc, supply_size, demand_size, cycle_size)
            if cycle[0] == True:
                keys.remove(potential_arc)
                cycle[1].remove(potential_arc)
                cycle_size -= 1
                cycle = cycle[1]
            else:
                return cycle

    return True, cycle

def find_col_cycle(cycle: list, keys: list, original_min_arc: tuple, potential_arc: tuple, supply_size, demand_size, cycle_size):
    if potential_arc in keys:
        keys.remove(potential_arc)

    for i in range(supply_size):
        new_col_arc = (i, potential_arc[1])
        if new_col_arc == original_min_arc and cycle_size > 1:
            cycle.append(potential_arc)
            return cycle

    for i in range(supply_size):
        new_arc = (i, potential_arc[1])
        if new_arc in keys and new_arc != potential_arc:
            keys.remove(new_arc)
            cycle.append(potential_arc)
            cycle_size += 1
            keys.append(potential_arc)
            cycle = find_row_cycle(cycle, keys, original_min_arc, new_arc, supply_size, demand_size, cycle_size)
            if cycle[0] == True:
                keys.remove(potential_arc)
                cycle[1].remove(potential_arc)
                cycle_size -= 1
                cycle = cycle[1]
            else:
                return cycle

    return True, cycle


def enter_and_leave(sent: dict, cycle: list, entering: tuple):
    count = 0
    odds = []

    sent[entering] = 0

    for k in range(len(cycle)):
        if k % 2 == 1:
            odds.append(cycle[k])

    minimum_odd = max([sent[arc] for arc in odds])
    leaving = ()
    for arc in odds:
        if sent[arc] <= minimum_odd:
            minimum_odd = sent[arc]
            leaving = arc

    for arc in cycle:
        if count % 2 == 0:
            sent[arc] += minimum_odd
        else:
            sent[arc] -= minimum_odd
        count += 1

    sent.pop(leaving)

    return sent


def find_total_cost(sent: dict, costs: dict):
    total_cost = 0

    for key in sent.keys():
        total_cost += sent[key] * costs[key]

    return total_cost

def tuple_adder(tuple, amount):
    new_tuple = (tuple[0] + amount, tuple[1] + amount)
    return new_tuple

def row_col_remover(sent: dict, costs, found):
    to_be_deleted = []
    non_dummy_coord = None
    if costs[found]:
        for arc in sent:
            if arc[0] == found:
                non_dummy_coord = arc[1]
                to_be_deleted.append(arc)
    else:
        for arc in sent:
            if arc[1] == found:
                non_dummy_coord = arc[0]
                to_be_deleted.append(arc)

    for perishable in to_be_deleted:
        sent.pop(perishable)

    return sent, found, costs[found], non_dummy_coord

def dummy_finder(sent, costs):
    found = None

    for arc in costs:
        if type(arc) != tuple:
            found = arc

    if found:
        return row_col_remover(sent, costs, found)
    
    return sent, found, None, None
            


def transportation_algorithm(supply_size, demand_size, supplies, demands, costs):

    sent, costs, dummy_size = initialization(supply_size, demand_size, supplies, demands, costs)
    U, V = compound_var(supply_size, demand_size, sent, costs)
    
    reduced_matrix = find_reduced_costs(costs, U, V)
    optimum = optimality_test(reduced_matrix)

    while optimum != True:
        cycle = find_row_cycle([], list(sent.keys()), optimum, optimum, supply_size, demand_size, 0)
        sent = enter_and_leave(sent, cycle, optimum)
        U, V = compound_var(supply_size, demand_size, sent, costs)
        reduced_matrix = find_reduced_costs(costs, U, V)
        optimum = optimality_test(reduced_matrix)

    sent = dummy_finder(sent, costs)

    total_cost = find_total_cost(sent[0], costs)
    arcs = list(sent[0].keys())
    arcs.sort()
    sorted_sent = {tuple_adder(i, 1): sent[0][i] for i in arcs}
        
    if sent[1]:
        if sent[2]:
            print(f"Demand {sent[3] + 1} will not receive {dummy_size} units.")
        else:
            print(f"Supply {sent[3] + 1} will not send {dummy_size} units.")
    return sorted_sent, total_cost


if __name__=="__main__":
    supply_size = int(input("Please enter number of supplies: "))
    demand_size = int(input("Please enter number of demands: "))
    supplies = []
    demands = []
    costs = {}

    for i in range(supply_size):
        supply = int(input(f"Input supply {i+1}: "))
        supplies.append(supply)

    for j in range(demand_size):
        demand = int(input(f"Input demand {j+1}: "))
        demands.append(demand)

    for i in range(supply_size):
        for j in range(demand_size):
            costs[(i, j)] = int(input(f"Cost to move from supply {i+1} to demand {j+1}: "))

    print(transportation_algorithm(supply_size, demand_size, supplies, demands, costs))