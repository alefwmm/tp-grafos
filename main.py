import argparse

from collections import namedtuple

class Node:
    def __init__(self, id, is_passenger, is_driver, passenger_amount,
                 available_seats, distance):

        # Node properties
        self.id = id
        self.is_passenger = bool(is_passenger)
        self.is_driver = bool(is_driver)
        self.passenger_amount = passenger_amount
        self.available_seats = available_seats
        self.distance = distance

        # Problem variables
        self.remaining_seats = self.available_seats - self.passenger_amount

    def __str__(self):
        return "ID %d | P? %r | D? %r | AMOUNT %d | SEATS %d/%d | DIST %d" % (
            self.id,
            self.is_passenger,
            self.is_driver,
            self.passenger_amount,
            self.remaining_seats,
            self.available_seats,
            self.distance)

    def allocate(self, edge):
        self.remaining_seats -= edge.source.passenger_amount

    def deallocate(self, edge):
        self.remaining_seats += edge.source.passenger_amount

class Edge:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.value = self.source.distance

    def __str__(self):
        return "%d -> %d (%g)" % (self.source.id, self.target.id, self.value)

    def is_elegible(self):
        return (self.source.is_passenger
                and self.target.is_driver
                and self.source.passenger_amount <= self.target.remaining_seats)

class Graph:
    def __init__(self):
        self.nodes = {}
        self.out_edges = {}
        self.in_edges = {}
        self.edges = set()

    def add_node(self, node):
        self.nodes[node.id] = node
        self.out_edges[node.id] = set()
        self.in_edges[node.id] = set()

    def add_edge(self, source_id, target_id):
        edge = Edge(self.nodes[source_id], self.nodes[target_id])
        self.out_edges[source_id].add(edge)
        self.in_edges[target_id].add(edge)
        self.edges.add(edge)

    def show(self):
        for _, node in self.nodes.items():
            print(node)
            for edge in self.out_edges[node.id]:
                print(edge)
            print("")

Solution = namedtuple("Solution", ["value", "edges"])
AglutinatedSolution = namedtuple("AglutinatedSolution", ["value", "trips"])

def load_graph(filename):
    graph = Graph()

    with open(filename, "r") as stream:
        node_amount = int(next(stream))
        for i in range(node_amount):
            data = next(stream).split(' ')
            descriptors, distance = map(int, data[:-1]), float(data[-1])
            graph.add_node(Node(*descriptors, distance=distance))

        edge_amount = int(next(stream))
        for i in range(edge_amount):
            source_id, target_id = map(int, next(stream).split(' '))
            graph.add_edge(source_id, target_id)

    return graph

def improve(solution, edges, graph):
    best_solution = solution

    for edge in edges:
        if edge.is_elegible():
            edge.target.allocate(edge)
            better_solution = Solution(solution.value + edge.value,
                                       solution.edges | set([edge]))
            remaining_edges = (edges
                               - graph.in_edges[edge.source.id]
                               - graph.out_edges[edge.source.id]
                               - graph.out_edges[edge.target.id])
            improved_solution = improve(better_solution, remaining_edges, graph)
            edge.target.deallocate(edge)
            if improved_solution.value > best_solution.value:
                best_solution = improved_solution
    return best_solution

def aglutinate_solution(solution):
    aglutinated = AglutinatedSolution(solution.value, {})

    for edge in solution.edges:
        if edge.target.id not in aglutinated.trips:
            aglutinated.trips[edge.target.id] = []
        aglutinated.trips[edge.target.id].append(edge.source.id)

    return aglutinated

def write_solution(filename, solution):
    with open(filename, "w") as stream:
        stream.write("%d %g\n" % (len(solution.trips), solution.value))

        trips = sorted(solution.trips.items())
        for driver, passengers in trips:
            passengers.sort()
            stream.write("%d %s\n" % (driver, " ".join(map(str, passengers))))

def solve(graph):
    solution = Solution(0, set())
    edges = graph.edges
    return improve(solution, edges, graph)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shared trips problem solver")
    parser.add_argument("input")
    parser.add_argument("output")

    args = parser.parse_args()
    graph = load_graph(args.input)
    solution = aglutinate_solution(solve(graph))

    write_solution(args.output, solution)
