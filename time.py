from argparse import ArgumentParser
from main import *

def random_problem(size):
    graph = Graph()

    graph.add_node(Node(1, 1, 0, 1, 0, 1.0))
    for id in range(2, size+1):
        current = Node(id, 1, 1, 2, 3, 5.0)
        graph.add_node(current)

        for node in graph.nodes:
            if node != current:
                graph.add_edge(node, current.id)

    return graph

if __name__ == "__main__":
    parser = ArgumentParser(description="Time tests with random graphs")
    parser.add_argument("size", type=int)

    args = parser.parse_args()
    graph = random_problem(args.size)
    solve(graph)
