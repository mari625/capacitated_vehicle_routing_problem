import numpy as np

class dsu:
    def __init__(self, instance):
        number = instance["dimension"]
        self.weight = [el for el in instance["demand"]]
        self.first = [i for i in range(number)]
 
    def get(self, vertex):
        if vertex == self.first[vertex]:
            return vertex

        self.first[vertex] = self.get(self.first[vertex])
        return self.first[vertex]
    
    def get_weight(self, vertex):
        return self.weight[self.get(vertex)]
    
    def unite(self, vertex_0, vertex_1):
        vertex_0 = self.get(vertex_0)
        vertex_1 = self.get(vertex_1)

        if vertex_0 == vertex_1:
            return

        self.weight[vertex_0] += self.weight[vertex_1]

        # vertex_0 is in end of the first way
        self.first[vertex_1] = vertex_0


def solve_clarke_wright(instance, number_vehicles, depot):
    savings = []

    next_vertex = [depot for i in range(instance["dimension"])]
    prev_vertex = [depot for i in range(instance["dimension"])]

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

        if prev_vertex[begin] == depot and next_vertex[end] == depot:
            if first_in_path.get_weight(begin) + first_in_path.get_weight(end) <= instance["capacity"]:

                next_vertex[end] = begin
                prev_vertex[begin] = end

                first_in_path.unite(end, begin)

                number_routes -= 1
        
        if number_routes == number_vehicles:
            break

    roots = set()
    for i in range(instance["dimension"]):
        if i != depot:
            roots.add(first_in_path.get(i))
    
    routes = []
    cost = 0

    for begin in roots:
        if begin == depot:
            continue

        route = [int(begin)]
        
        cost += instance["edge_weight"][depot][route[-1]]

        while next_vertex[route[-1]] != depot:
            route.append(next_vertex[route[-1]])
            cost += instance["edge_weight"][route[-2]][route[-1]]

        cost += instance["edge_weight"][route[-1]][depot]

        routes.append(route)


    return {"cost": cost, "routes": routes}