import networkx as nx
import json

class DistanceVectorRouting():
    '''Distance Vector Routing'''

    def __init__(self, graph_dict, source, names):
        self.graph_dict = graph_dict
        self.source = source
        self.distance, self.predecessor = self.bellman_ford(graph_dict, source)
        self.names = names
        self.neighbors = self.get_neighbors(graph_dict, source)

    def initialize(self, graph_dict, source):
        '''For each node prepare the destination and predecessor'''
        d = {} # Stands for destination
        p = {} # Stands for predecessor
        for node in graph_dict:
            d[node] = float('Inf') # We start admitting that the rest of nodes are very very far
            p[node] = None
        d[source] = 0 # For the source, we know how to reach
        return d, p

    def relax(self, node, neighbor, graph_dict, d, p):
        '''If the distance between the node and the neighbor is lower than the one I have now'''
        if d[neighbor] > d[node] + graph_dict[node][neighbor]:
            # Record this lower distance
            d[neighbor] = d[node] + graph_dict[node][neighbor]
            p[neighbor] = node

    def bellman_ford(self, graph_dict, source):
        '''Bellman Ford Alg'''

        d, p = self.initialize(graph_dict, source)
        for i in range(len(graph_dict) - 1): # Run this until it converges
            for u in graph_dict:
                for v in graph_dict[u]: # For each neighbor of u
                    self.relax(u, v, graph_dict, d, p) # Let's relax it

        # Step 3: check for negative-weight cycles
        for u in graph_dict:
            for v in graph_dict[u]:
                assert d[v] <= d[u] + graph_dict[u][v]

        return d, p

    def get_neighbors(self, graph_dict, source):
        '''List of neighbors'''
        return list(graph_dict[source].keys())

    def update_graph(self, graph_dict):
        '''Update graph_dict'''
        self.graph_dict = graph_dict
        self.distance, self.predecessor = self.bellman_ford(graph_dict, self.source)
        self.neighbors = self.get_neighbors(graph_dict, self.source)

    def shortest_path(self, target):
        '''Find shortest path'''
        for key in self.names:
            if self.names[key] == target:
                path = []
                node = key
                while node is not None:
                    path.insert(0, node)
                    node = self.predecessor[node]
                return path
        return None
    
    def send_distance_vector(self):
        # Crear el paquete JSON
        distance_vector = self.calculate_distance_vector()
        packet = {
            "type": "info",
            "headers": {
                "from": self.source,
                "to": None,  # Define el destinatario apropiado aquí
                "hop_count": 0,  # Define el hop_count adecuado aquí
            },
            "payload": distance_vector  # Envía el vector de distancia como payload
        }

        # Convierte el paquete en una cadena JSON
        packet_json = json.dumps(packet)

        # Imprime el paquete JSON antes de enviarlo
        print(f"Enviando vector de distancia a {packet['headers']['to']}: {packet_json}")



# Define your graph structure in the format you provided
graph_dict = {
    "Node A": {"Node A": 0, "Node B": 4, "Node C": 1},
    "Node B": {"Node A": 4, "Node B": 0, "Node C": 2},
    "Node C": {"Node A": 1, "Node B": 2, "Node C": 0}
}


# Define the names mapping (node names to labels)
names = {
    "Node A": "Node A",
    "Node B": "Node B",
    "Node C": "Node C"
}

# Create an instance of DistanceVectorRouting with the provided graph and names
# Create an instance of DistanceVectorRouting with the provided graph and names
start_node = input("Enter the starting node: ")
dvr = DistanceVectorRouting(graph_dict, start_node, names)

target_node = input("Enter the target node: ")

# Find the shortest path
shortest_path = dvr.shortest_path(target_node)

if shortest_path:
    print(f"Shortest Path from {start_node} to {target_node}: {shortest_path}")
else:
    print(f"No path found from {start_node} to {target_node}.")

