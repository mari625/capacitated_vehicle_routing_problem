import vrplib
import numpy as np

from solution import solve_problem
from solution import solve_with_ants
from clarke_wright import solve_clarke_wright
from simulated_annealing import solve_outsiders

def find_hyperparams_ants():
    examples = [
        'instances/E/E-n13-k4.vrp',
        'instances/E/E-n23-k3.vrp',
        'instances/E/E-n33-k4.vrp',
        'instances/E/E-n76-k7.vrp',
        'instances/F/F-n135-k7.vrp',
        'instances/M/M-n200-k17.vrp',
        'instances/P/P-n19-k2.vrp',
        'instances/P/P-n40-k5.vrp',
        'instances/P/P-n76-k4.vrp',
        'instances/P/P-n101-k4.vrp'
    ]

    list_alpha = [0.1, 0.3, 0.5]
    list_beta = [1, 2, 5]
    list_q_0 = [0.7, 0.9]

    min_ratio = 2

    best_alpha = 0
    best_beta = 0
    best_q_0 = 0

    for alpha in list_alpha:
        for beta in list_beta:
            for q_0 in list_q_0:
                ratios = []
                for ex in examples:
                    print(ex)

                    _, ratio = solve_problem(ex, {"alpha": alpha, "beta": beta, "q0": q_0}, params_outsiders = dict())

                    ratios.append(ratio)

                total_ratio = sum(ratios) / len(examples)

                if total_ratio < min_ratio:
                    min_ratio = total_ratio

                    best_alpha = alpha
                    best_beta = beta
                    best_q_0 = q_0

                    print("total", total_ratio)

    return best_alpha, best_beta, best_q_0


def find_hyperparams_fire(alpha, beta, q_0):
    examples = [
        'instances/E/E-n30-k3.vrp',
        'instances/E/E-n51-k5.vrp',
        'instances/F/F-n72-k4.vrp',
        'instances/P/P-n50-k8.vrp',
        'instances/P/P-n55-k15.vrp',
        'instances/P/P-n70-k10.vrp'
    ]

    list_theta_0 = [10, 50, 100]
    list_mult = [0.8, 0.9, 0.95]

    best_inserted = 0
    best_ratio = 2

    best_theta_0 = 0
    best_mult = 0

    for theta_0 in list_theta_0:
        for mult in list_mult:
            ratios = []
            inserted = 0
            for ex in examples:
                print(ex)

                instance = vrplib.read_instance(ex)
                optimal_solution = vrplib.read_solution(ex.replace(".vrp", ".sol"))
        
                # get number vehicles
                name = instance["name"]
                number_vehicles = int(name[name.rfind('k') + 1:])

                # distances are int
                instance["edge_weight"] = np.round(instance["edge_weight"]).astype(int)

                solution = solve_clarke_wright(instance, number_vehicles, int(instance["depot"][0]))

                groups = solution["routes"]
                outsiders_before = 0 if len(groups) == number_vehicles else len(solution["routes"][-1])

                groups = solve_outsiders(instance, number_vehicles, groups, params= {"theta_0": theta_0, "mult": mult})
                outsiders_after = 0 if len(groups) == number_vehicles else len(solution["routes"][-1])

                inserted += outsiders_before - outsiders_after

                solution_ants = solve_with_ants(instance, groups, {'alpha': alpha, 'beta': beta, 'q0': q_0})
                ratio = round(solution_ants["cost"]/optimal_solution["cost"], 2)

                ratios.append(ratio)

            ratio = sum(ratios) / len(examples)

            if inserted > best_inserted:
                best_inserted = inserted
                best_ratio = ratio

                best_theta_0 = theta_0
                best_mult = mult

                print(best_theta_0, best_mult)

            elif ratio < best_ratio:

                best_ratio = ratio

                best_theta_0 = theta_0
                best_mult = mult

                print(best_theta_0, best_mult)

    return best_theta_0, best_mult



if __name__ == '__main__':
    #alpha, beta, q_0 = find_hyperparams_ants()

    #print(f'alpha: {alpha}, beta: {beta}, q_0: {q_0}')

    theta_0, mult = find_hyperparams_fire(alpha=0.1, beta=2, q_0=0.9)

    print(f'theta_0: {theta_0}, mult: {mult}')