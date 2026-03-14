import vrplib
import numpy as np
import glob
import pandas as pd

from clarke_wright import solve_clarke_wright
from simulated_annealing import solve_outsiders
from aco import aco


params_ants = {"alpha": 0.1, "beta": 2, "q0": 0.9}
params_outsiders = {"theta_0": 50, "mult": 0.95}



def solve_with_ants(instance, groups, params):
    best_routes = []
    cost = 0

    for group in groups:
        best_route, best_distance = aco(instance, group, params)
        
        best_routes.append(best_route)
        cost += best_distance

    solution = {"cost": cost, "routes": best_routes}
    return solution




def solve_problem(path, params_ants, params_outsiders):
    instance = vrplib.read_instance(path)
    optimal_solution = vrplib.read_solution(path.replace(".vrp", ".sol"))

    total_distance = 0

    for way in optimal_solution['routes']:
        for i in range(len(way) - 1):
            if i == 0:
                total_distance += instance["edge_weight"][0][way[i]]
            else:
                total_distance += instance["edge_weight"][way[i]][way[i + 1]]
        total_distance += instance["edge_weight"][way[len(way) - 1]][0]

    # get number vehicles
    name = instance["name"]
    number_vehicles = int(name[name.rfind('k') + 1:])

    # distances are int
    instance["edge_weight"] = np.round(instance["edge_weight"]).astype(int)


    solution = solve_clarke_wright(instance, number_vehicles, int(instance["depot"][0]))

    #print(number_vehicles, len(solution["routes"]))
    
    #for items in solution.items():
    #    print(items[0], ": ", items[1])

    #print('\n')

    groups = solution["routes"]

    if len(groups) > number_vehicles:
        groups = solve_outsiders(instance, number_vehicles, groups, params_outsiders)

    #print(len(groups))
    #print(groups, '\n')

    solution_ants = solve_with_ants(instance, groups, params_ants)
    
    for items in solution_ants.items():
        print(items[0], ": ", items[1])

    share = round(solution_ants["cost"]/optimal_solution["cost"], 2)
    print(share)

    return solution_ants, share



if __name__ == '__main__':
   solve_problem('instances/E/E-n23-k3.vrp', params_ants, params_outsiders)

    
