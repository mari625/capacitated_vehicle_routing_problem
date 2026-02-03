import random
import numpy as np


def count_initial_pheromone(instance, group):
    min_dist = float("inf")

    for i in range(len(group)):
        for j in range(len(group)):
            if i == j:
                continue
            if instance["edge_weight"][group[i]][group[j]] != 0:
                min_dist = min(min_dist, instance["edge_weight"][group[i]][group[j]])
    
    return float(1/((len(group) + 1) * min_dist))


def count_client_proba(current_client, utilities):
    total_utility = sum(utilities)

    if total_utility == 0:
        return 0

    return utilities[current_client]/ total_utility


def count_client_utilities(instance, group, visited, pheromones, previous_client, params):
    utilities = [0 for _ in range(len(group))]

    for i in range(len(group)):
        if i == 0:
            continue

        if i not in visited:
            if instance["edge_weight"][group[previous_client]][group[i]] != 0:
                utilities[i] = float(pheromones[previous_client][i] / ((instance["edge_weight"][group[previous_client]][group[i]]) ** params["beta"]))
            else:
                utilities[i] = float("inf")
    
    return utilities


def local_pheromone_update(previous_client, current_client, pheromones, params, t_0):
    return pheromones[previous_client][current_client] * (1 - params["alpha"]) + t_0 * params["alpha"]


def ant_run(group, instance, pheromones, params, t_0):
    visited = set()
    depot = 0
    weight = 0
    route = [depot]
    visited.add(depot)

    while True:
        if len(visited) == len(group):
            break

        utilities = count_client_utilities(instance, group, visited, pheromones, route[-1], params)

        max_utility = max(utilities)

        if max_utility ==0:
            break

        chosen_index = 0


        if max_utility == float("inf") or np.random.rand() < params["q0"]:
            for j, utility in enumerate(utilities):
                if utility == max_utility:
                    chosen_index = j
                    break
        else:
            probabilities = []
            client_indices = []

            for i in range(len(group)):
                probabilities.append(count_client_proba(i, utilities))
                client_indices.append(i)

            chosen_index = random.choices(client_indices, probabilities, k=1)[0]

        route.append(chosen_index)
        visited.add(chosen_index)
        weight += instance["demand"][group[chosen_index]]

        # local update
        pheromones[route[-2]][route[-1]] = local_pheromone_update(route[-2], route[-1], pheromones, params, t_0)

    # add depot to route
    route.append(depot)

    # update local pheromone on route to depot
    pheromones[route[-2]][route[-1]] = \
            local_pheromone_update(route[-2], route[-1], pheromones, params, t_0)

    return route, pheromones

def global_update(pheromones, params, route, distance):
    for i in range(1, len(route)):
        pheromones[route[i - 1]][route[i]] = \
                float(pheromones[route[i - 1]][route[i]] * (1 - params["alpha"]) + params["alpha"] / distance)

    return pheromones


def aco(instance, group, params):
    group_copy = group.copy()
    group_copy.insert(0, int(instance["depot"][0]))

    t_0 = count_initial_pheromone(instance, group_copy)

    pheromones = [[t_0 for _ in range(len(group_copy))] for _ in range(len(group_copy))]

    best_distance = float("inf")
    prev_best_distance = best_distance

    number_ants = 10 ## maybe hyperpar

    best_route = []

    stagnation_number = 500
    accumulated_number = 0
    number_iterations = 0

    while accumulated_number <= stagnation_number and number_iterations < 3000:
        for _ in range(number_ants):
            # make routes for ant
            route, pheromones = ant_run(group_copy, instance, pheromones, params, t_0)

            distance = 0
            for j in range(1, len(route)):
                distance += instance["edge_weight"][group_copy[route[j - 1]]][group_copy[route[j]]]

            if distance < best_distance:
                best_distance = distance
                best_route = route

        # update global pheromones
        pheromones = global_update(pheromones, params, best_route, best_distance)

        # update acumulated number
        if prev_best_distance == best_distance:
            accumulated_number += 1
        else:
            accumulated_number = 0
    
        prev_best_distance = best_distance

        number_iterations += 1

    best_route.pop(0)
    best_route.pop()

    for i in range(len(best_route)):
        best_route[i] = group_copy[best_route[i]]

    
    return best_route, best_distance