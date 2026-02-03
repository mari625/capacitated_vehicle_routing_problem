import vrplib
import numpy as np

from clarke_wright import solve_clarke_wright
from aco import aco

def solve_with_ants(instance, groups, params):
    best_routes = []
    cost = 0

    for group in groups:
        best_route, best_distance = aco(instance, group, params)
        
        best_routes.append(best_route)
        cost += best_distance

    solution = {"cost": cost, "routes": best_routes}
    return solution



def solve_problem(path, params):
    instance = vrplib.read_instance(path)
    optimal_solution = vrplib.read_solution(path.replace(".vrp", ".sol"))

    # get number vehicles
    name = instance["name"]
    number_vehicles = int(name[name.rfind('k') + 1:])

    # distances are int
    instance["edge_weight"] = np.round(instance["edge_weight"]).astype(int)

    solution = solve_clarke_wright(instance, number_vehicles, int(instance["depot"][0]))
    
    for items in solution.items():
        print(items[0], ": ", items[1])

    solution_ants = solve_with_ants(instance, solution["routes"], params)
    
    for items in solution_ants.items():
        print(items[0], ": ", items[1])

    print(round(solution["cost"]/optimal_solution["cost"], 2))

params = {"alpha": 0.1, "beta": 2, "q0": 0.9}
solve_problem("instances/P/P-n16-k8.vrp", params)
