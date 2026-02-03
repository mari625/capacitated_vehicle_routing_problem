import numpy as np

class dsu:
    def __init__(self, instance):
        number = instance["dimension"]
        self.weight = [el for el in instance["demand"]]
        self.first = [i for i in range(number)]
 
    def get(self, vertice):
        if vertice == self.first[vertice]:
            return vertice

        self.first[vertice] = self.get(self.first[vertice])
        return self.first[vertice]
    
    def get_weight(self, vertice):
        return self.weight[self.get(vertice)]
    
    def unite(self, vertice_0, vertice_1):
        vertice_0 = self.get(vertice_0)
        vertice_1 = self.get(vertice_1)

        if vertice_0 == vertice_1:
            return

        self.weight[vertice_0] += self.weight[vertice_1]

        # vertice_0 is in end of the first way
        self.first[vertice_1] = vertice_0


def solve_clarke_wright(instance, number_vehicles, depot):
    savings = []

    next_vertice = [depot for i in range(instance["dimension"])]
    prev_vertice = [depot for i in range(instance["dimension"])]

    first_in_path = dsu(instance)

    for i in range(instance["dimension"]):
        for j in range(instance["dimension"]):
            if i == depot or j == depot:
                continue

            saving_dict = {"begin": i, "end": j}
            saving_dict["cost"] = instance["edge_weight"][depot][i] + \
                instance["edge_weight"][j][depot] - instance["edge_weight"][i][j]

            savings.append(saving_dict)
    
    savings.sort(key = lambda saving: saving["cost"], reverse=True)

    number_routes = instance["dimension"] - 1

    for saving in savings:
        begin = saving["begin"]
        end = saving["end"]

        if first_in_path.get(begin) == first_in_path.get(end):
            continue

        if prev_vertice[begin] == depot and next_vertice[end] == depot:
            if first_in_path.get_weight(begin) + first_in_path.get_weight(end) < instance["capacity"]:
                next_vertice[end] = begin
                prev_vertice[begin] = end

                first_in_path.unite(end, begin)

                number_routes -= 1
        
        if number_routes == number_vehicles:
            break
    
    routes = []
    cost = 0

    for begin in np.unique([first_in_path.get(el) for el in first_in_path.first]):
        if begin == 0:
            continue

        route = [int(begin)]
        
        cost += instance["edge_weight"][depot][route[-1]]

        while next_vertice[route[-1]] != depot:
            route.append(next_vertice[route[-1]])
            cost += instance["edge_weight"][route[-2]][route[-1]]

        cost += instance["edge_weight"][route[-1]][depot]

        routes.append(route)


    return {"cost": cost, "routes": routes}