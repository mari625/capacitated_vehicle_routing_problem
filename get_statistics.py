import glob
import numpy as np
import time
import pandas as pd

from solution import solve_problem


params_ants = {"alpha": 0.1, "beta": 2, "q0": 0.9}
params_outsiders = {"theta_0": 50, "mult": 0.95}


def get_mean_ratio(letter, time_stats):
    files_vrp_E = glob.glob('instances/' + letter + '/*.vrp')

    ratios= []

    for file in files_vrp_E:
        start = time.time()

        if file == 'instances/E/E-n31-k7.vrp':
            continue

        print(file)
        solution, ratio = solve_problem(file, params_ants, params_outsiders)

        end = time.time()

        for items in solution.items():
            print(items[0], ": ", items[1])

        ratios.append(ratio)

        t = pd.DataFrame([{'type': letter, 'n_clients': int(file[file.rfind('n') + 1:file.rfind('-')]), 'time': end - start}])

        time_stats = pd.concat([time_stats, t], ignore_index=True)

    return np.mean(ratios), time_stats


if __name__ == '__main__':
    time_stats = pd.DataFrame(columns=['type', 'n_clients', 'time'])

    ratio_E, time_stats = get_mean_ratio('E', time_stats)
    ratio_F, time_stats = get_mean_ratio('F', time_stats)
    ratio_M, time_stats = get_mean_ratio('M', time_stats)
    ratio_P, time_stats = get_mean_ratio('P', time_stats)

    print(f"E: {ratio_E:.2f}")
    print(f"F: {ratio_F:.2f}")
    print(f"M: {ratio_M:.2f}")
    print(f"P: {ratio_P:.2f}")

    time_stats.to_csv('time_results.csv')
