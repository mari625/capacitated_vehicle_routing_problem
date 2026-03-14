import random
import numpy as np

class WeightedGroup:
    def __init__(self, group, weight):
        self.group = group
        self.weight = weight
    
    def __str__(self):
        return f"{self.weight}, {self.group}"
    
    def __add__(self, other):
        self.group += other.group
        self.weight += other.weight

        return self
    

def insert_outsider(instance, main_groups, outsiders, chosen_group, chosen_outsider):
    new_group = WeightedGroup(chosen_group.group, chosen_group.weight)

    new_group.group.append(chosen_outsider)
    new_group.weight += instance["demand"][chosen_outsider]

    outsiders.weight -= instance["demand"][chosen_outsider]
    outsiders.group.remove(chosen_outsider)

    outsiders.group = sorted(outsiders.group, key=lambda el: instance["demand"][el], reverse=True)
    
    main_groups.remove(chosen_group)
    main_groups.append(new_group)


def swap_outsider(instance, main_groups, outsiders, chosen_group, chosen_outsider, chosen_element):
    new_group = WeightedGroup(chosen_group.group, chosen_group.weight)

    old_outsider_weight = instance["demand"][chosen_outsider]
    new_outsider_weight = instance["demand"][chosen_element]

    old_outsider = chosen_outsider
    new_outsider = chosen_element

    outsiders.weight -= old_outsider_weight
    outsiders.group.remove(old_outsider)

    outsiders.weight += new_outsider_weight
    outsiders.group.append(new_outsider)

    outsiders.group = sorted(outsiders.group, key=lambda el: instance["demand"][el], reverse=True)

    new_group.weight -= new_outsider_weight
    new_group.group.remove(new_outsider)

    new_group.weight += old_outsider_weight
    new_group.group.append(old_outsider)


    #cur_group[i], chosen_outsider = chosen_outsider, cur_group[i]


    main_groups.remove(chosen_group)
    main_groups.append(new_group)

    #for group in main_groups:
        #print(group)

    #print(outsiders, '\n')


def solve_outsiders(instance, number_vehicles, groups, params):
    weights = [sum([instance["demand"][el] for el in group]) for group in groups]

    weighted_groups = []
    for item in zip(groups, weights):
        cur = WeightedGroup(item[0], item[1])
        weighted_groups.append(cur)

    weighted_groups = sorted(weighted_groups, key=lambda el: el.weight, reverse=True)

    #for group in weighted_groups:
        #print(group)

    #print('\n')

    main_groups = weighted_groups[:number_vehicles]
    outsiders = sum(weighted_groups[number_vehicles:], WeightedGroup([], 0))

    outsiders.group = sorted(outsiders.group, key=lambda el: instance["demand"][el], reverse=True)

    #for group in main_groups:
        #print(group)

    #print(outsiders, '\n')

    #for i in range(len(selected_groups) - 1, 0, -1):
    #    chosen_group = selected_groups[i]

    num_iterations = 0
    theta = params["theta_0"] # hyperparam!

    while outsiders.group and num_iterations < 100:
        chosen_outsider = outsiders.group[0]
        ##print(chosen_outsider)

        num_iterations += 1

        probabilities = [int(instance["capacity"]) - group.weight for group in main_groups]

        for _ in range(len(main_groups)):
            ##print(probabilities, '\n')

            if sum(probabilities) == 0:
                break

            chosen_group = random.choices(main_groups, probabilities / sum(probabilities), k=1)[0]

            found = False

            ##print(chosen_group)

            if (instance["demand"][chosen_outsider] + chosen_group.weight <= instance["capacity"]):
                insert_outsider(instance, main_groups, outsiders, chosen_group, chosen_outsider)

                theta = params["mult"]*theta

                ##print(chosen_group, '\n', chosen_outsider)

                ##print('inserted!!!!!!!!!!!!!!!!!!!!!!!!')

                found = True
            
            else:
                cur_group = chosen_group.group

                for i in range(0, len(cur_group)):
                    if chosen_group.weight - instance["demand"][cur_group[i]] + instance["demand"][chosen_outsider] <= instance["capacity"]:
                        if (instance["demand"][cur_group[i]] < instance["demand"][chosen_outsider]):
                            #print(chosen_group, '\n', chosen_outsider)

                            #print("el:", cur_group[i])

                            prev, next = 0, 0
                            if (i != 0):
                                prev = cur_group[i - 1]
                            if (i != len(cur_group) - 1):
                                next = cur_group[i + 1]

                            len_with_el = instance["edge_weight"][prev][cur_group[i]] + instance["edge_weight"][cur_group[i]][next]
                            len_with_outsider = instance["edge_weight"][prev][chosen_outsider] + instance["edge_weight"][chosen_outsider][next]

                            theta = params["mult"]*theta

                            if len_with_el > len_with_outsider:
                                #print("new outsider: ", cur_group[i])

                                swap_outsider(instance, main_groups, outsiders, chosen_group, chosen_outsider, cur_group[i])

                                found = True
                            
                                break

                            else:
                                #print("else!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                #delta_f = len_with_outsider - len_with_el
                                proba = np.exp(-(len_with_outsider - len_with_el) / theta)

                                #print(proba)
                                if np.random.rand() < proba:
                                    #print("worse solution chosen")
                                    swap_outsider(instance, main_groups, outsiders, chosen_group, chosen_outsider, cur_group[i])

                                    found = True

                                    break


            if found:
                #print("--------------------------------------------------------------")
                break

            probabilities[main_groups.index(chosen_group)] = 0

    groups = [weighted_group.group for weighted_group in main_groups]

    if outsiders.group:
        groups.append(outsiders.group)

    return groups
