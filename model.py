#Topics in Optimization: 
#Computational Project
# Tripp Lawrence and Luke Lewis
# 02/24/2023


def dummy_supply(costs, sent, supply_size, demand_size, dummy_size): # This will create a dummy supply in our network.
    sent[(supply_size, demand_size - 1)] = dummy_size # This takes the size of the dummy (determined in the dummy_test) and adds it to the sent dictionary (it becomes lowest row).

    dummy_cost = 100 * max([costs[arc] for arc in costs]) # This sets the cost of the dummy at 100 times larger than the largest cost in the network (big M cost).
    
    for j in range(demand_size): # This for loop actually connects the dummy_cost to every demand in the dummy_supply row.
        costs[(supply_size, j)] = dummy_cost # And thus, all of the costs to send supply from this dummy supply are big M costs.
    
    costs[supply_size] = True # This adds one more item to the costs dictionary. This will allow us to remove the big M cost from the objective function later.

    return costs, sent, dummy_size

def dummy_demand(costs: dict, sent: dict, supply_size, demand_size, dummy_size): # This will create a dummy demand in our network.
    sent[(supply_size - 1, demand_size)] = dummy_size # This takes the size of the dummy (determined in the dummy_test) and adds it to the sent dictionary (it becomes the rightmost column).
            #(The keys are the coordinates in the matrix)
    dummy_cost = 100 * max([costs[arc] for arc in costs]) # This sets the cost of the dummy at 100 times larger than the largest cost in the network (big M cost).
    
    for i in range(supply_size): # This for loop actually connects the dummy_cost to every supply in the dummy_demand column.
        costs[(i, demand_size)] = dummy_cost # And thus, all of the costs to send supply to this dummy demand are big M costs.
    
    costs[demand_size] = False # This adds one more item to the costs dictionary. This will allow us to remove the big M cost from the objective function later.

    return costs, sent, dummy_size

def dummy_test(supplies: list, demands: list, costs, sent): # This will test to see if there is a dummy supply/demand needed.
    supply = sum(supplies) # This changes the list of supplies sent into a total number of supplies available.
    demand = sum(demands) # This changes the list of demands requested into a total number demands needed.

    if supply == demand: # This tests to see if the amount of supplies = the amount of demands.
        return None # If they are equal, then no dummy is needed.
    
    elif supply > demand: # If the supply is greater than the demand, create a dummy demand.
        return dummy_demand(costs, sent, supply_size, demand_size, supply - demand) # The last variable in this function (supply - demand) is the amount that the dummy demand is requesting.

    else: # Otherwise, the demand has to be greater than the supply, and thus create a dummy supply.
        return dummy_supply(costs, sent, supply_size, demand_size, demand - supply) # The last variable in this function (demand - supply) is the amount that the dummy supply needs to provice.


def initialization(supply_size, demand_size, supplies, demands, costs): # Initial Basic Feasible solution generator (using the NW Corner Method).
    sent = {} # Initialization of the dictionary that contains the amount of supply sent from source i to demand j
    supply_count = 0 # This is the supply coordinate that we start at. It will be updated as we look for our initial solution.
    demand_count = 0 # This is the demand coordinate that we start at. It will be updated as we look for our initial solution.
    dummy_size = 0 # This will be updated if we need to use a dummy.

    while supply_count < supply_size and demand_count < demand_size: # This makes us continue to look for a solution until we get through the matrix.
        if supplies[supply_count] <= demands[demand_count]: # This checks to see if the supply from source i is less than the demand from demand j.
            sent[(supply_count, demand_count)] = supplies[supply_count] # This adds the amount of supply sent from source i to demand j to the sent dictionary. The "key" to the dictionary is a Tuple (i,j).
            demands[demand_count] -= supplies[supply_count] # This updates the amount of demand at j be subtracting the supplies at i from the demand at j.
            supplies[supply_count] = 0 # This updates the amount of supplies at i to 0.
            supply_count += 1 # This moves us over to the next supply.
        else:
            sent[(supply_count, demand_count)] = demands[demand_count] # This sets the amount of supplies sent from i to the demand at j.
            supplies[supply_count] -= demands[demand_count] # This reduces the supplies at i by the demand at j.
            demands[demand_count] = 0 # This sets the demand at j to 0.
            demand_count += 1 # This moves us over to the next demand.

    solutions = dummy_test(supplies, demands, costs, sent) # A check to see if we actually need to add a dummy supply or demand.

    if solutions: # If the dummy_test returns a value, then we go into this if statement.
        costs = solutions[0] # Sets the cost of the dummy.
        sent = solutions[1] 
        dummy_size = solutions[2] # Sets the amount sent to or from the dummy.

    return sent, costs, dummy_size

def compound_var(supply_size: int, demand_size: int, sent: dict, costs: dict): # This function is used to find U and V.
    first_arc = (0,0)
    U = [0 for i in range(supply_size)]
    V = [0 for j in range(demand_size)]

    for arc in sent.keys():
        if arc[0] == 0:
            first_arc = arc

    U, V = row_col_finder(first_arc, list(sent.keys()), costs, supply_size, demand_size, U, V)
    return U, V

    
def row_col_finder(arc: tuple, keys: list, costs: dict, supply_size, demand_size, U, V): # This basically allows us to step across the rows/columns. This will be used when finding U, V.
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

def find_reduced_costs(costs: dict, U: list, V: list): # This will find the reduced costs for the non-basic variables.
    reduced_matrix = {}

    for i in range(len(U)):
        for j in range(len(V)):
            reduced_matrix[(i, j)] = costs[(i, j)] - U[i] - V[j]

    return reduced_matrix

def optimality_test(reduced_matrix: dict): # This will test to see if the reduced costs are optimal (all positive).
    minimum_reduced_cost = 0
    minimum_arc = (0, 0)
    for reduced_arc in reduced_matrix.keys(): # Looks through the reduced costs to see if any of them are negative.
        if reduced_matrix[reduced_arc] < minimum_reduced_cost:
            minimum_reduced_cost = reduced_matrix[reduced_arc]
            minimum_arc = reduced_arc
    if minimum_reduced_cost >= 0: # If the minimum reduced is positive, then the solution is optimal.
        return True
    else:
        return minimum_arc # Otherwise, we need to return the coordinates of the minimum reduced cost. This is the arc that will enter our tree.

def find_row_cycle(cycle: list, keys: list, original_min_arc: tuple, potential_arc: tuple, supply_size, demand_size, cycle_size): # This function will check the rows to see if there is a cycle. 
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

def find_col_cycle(cycle: list, keys: list, original_min_arc: tuple, potential_arc: tuple, supply_size, demand_size, cycle_size): # This checks the columns to see if they are part of a cycle.
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


def enter_and_leave(sent: dict, cycle: list, entering: tuple): # This will let us know which coordinates are in the cycle. 
    count = 0 #                    It will add or subract the or subtract the necessary value from the sent items in the cycle.
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


def find_total_cost(sent: dict, costs: dict): # This will find the final total cost of our objective function.
    total_cost = 0 # Initially the cost is 0.

    for key in sent.keys(): # This looks through the sent dictionary and basically does a sum-product.
        total_cost += sent[key] * costs[key]

    return total_cost # Returns the final total cost.

def tuple_adder(tuple, amount): # Since computer science likes to start with 0, and we like to start with 1, this function fixes the coordinates to make them understandable to us.
    new_tuple = (tuple[0] + amount, tuple[1] + amount)
    return new_tuple

def row_col_remover(sent: dict, costs, found): # This function allows us to remove a row or column from the final printout. It will be used to make sure that the dummy costs (if there are any), are not part of the final cost.
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

def dummy_finder(sent, costs): # This will allow us to identify the dummy and later remove it from the final printout.
    found = None

    for arc in costs:
        if type(arc) != tuple:
            found = arc

    if found:
        return row_col_remover(sent, costs, found)
    
    return sent, found, None, None
            


def transportation_algorithm(supply_size, demand_size, supplies, demands, costs): # Here is the actual algorithm function in all its glory.

    sent, costs, dummy_size = initialization(supply_size, demand_size, supplies, demands, costs) # This will initialize the algorithm, giving a basic feasible solution using the NW corner method.
    U, V = compound_var(supply_size, demand_size, sent, costs) # This finds the initial U and V. The way this function works, U_1 always = 0.
    
    reduced_matrix = find_reduced_costs(costs, U, V) # Taking the U's and V's, this function finds the reduced costs for the non-basic variables.
    optimum = optimality_test(reduced_matrix) # Tests to see if the solution is optimal.

    while optimum != True: # If the solution is not optimal, follow the steps below.
        cycle = find_row_cycle([], list(sent.keys()), optimum, optimum, supply_size, demand_size, 0) # Find a cycle.
        sent = enter_and_leave(sent, cycle, optimum) # Find which one is going to enter (and leave) the solution path.
        U, V = compound_var(supply_size, demand_size, sent, costs) # Finds our U's and V's.
        reduced_matrix = find_reduced_costs(costs, U, V) # Finds the new reduced costs.
        optimum = optimality_test(reduced_matrix) # Checks to see if the solution is optimal. If False, then the while loop continues.

    sent = dummy_finder(sent, costs) # Checks to see if we have a dummy supply/demand.

    total_cost = find_total_cost(sent[0], costs) # Finds our total cost.
    arcs = list(sent[0].keys())
    arcs.sort()
    sorted_sent = {tuple_adder(i, 1): sent[0][i] for i in arcs} # Updates the coordinates from starting at (0,0) to starting at (1,1)
        
    if sent[1]: # This section only happens if there is a dummy.
        if sent[2]: # If there is a dummy supply, this will let you know which demand won't get everything that they asked for.
            print(f"Demand {sent[3] + 1} will not receive {dummy_size} units.")
        else: # If there is a dummy demand, this will let you know which supply won't send all of its units.
            print(f"Supply {sent[3] + 1} will not send {dummy_size} units.")
    return sorted_sent, total_cost


if __name__=="__main__": # This is basically the way that python runs programs. When you run the program, everything in this section will happen.
    supply_size = int(input("Please enter number of supply rows: ")) # User inputs the number of supply rows.
    demand_size = int(input("Please enter number of demand columns: ")) # User inputs the number of demand columns.
    supplies = [] # Sets up an empty list for the supply amounts.
    demands = [] # Sets up an empty list for the demand amounts.
    costs = {} # Sets up an empty dictionary for the costs to take each path.

    for i in range(supply_size): # This will continue until the supplies for each row have been inputted by the user.
        supply = int(input(f"Input supply for row {i+1}: ")) # Asks the user to input the amount of supply at each source.
        supplies.append(supply) # Adds that amount to the supplies list.

    for j in range(demand_size): # This will continue until the demands for each column have been inputted by the user.
        demand = int(input(f"Input demand for column {j+1}: ")) # Asks the user to input the requested supplies at each demand.
        demands.append(demand) # Adds that amount to the demands list.

    for i in range(supply_size): # For every row...
        for j in range(demand_size): # Check every column...
            costs[(i, j)] = int(input(f"Cost to move from supply {i+1} to demand {j+1}: ")) # And ask the user to input the cost to use the (i,j) path.

    print(transportation_algorithm(supply_size, demand_size, supplies, demands, costs)) # Prints out our final result (see notes on transportation_algorithm for more details).