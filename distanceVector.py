import json

class BellmanFord():
    def __init__(self):
        self.done = False  # Add the 'done' attribute
        self.graph = self.select_node()
        self.tabla = self.tabla_enrutamiento()
        self.mensajes = False  # Add the 'mensajes' attribute
        self.main()

    '''
        Generate the routing table for each node. 
            - Store the weights of each relationship between nodes. 
            - Fills it through broadcasting.
    '''
    def tabla_enrutamiento(self):
        # Generate the routing table
        array_topologia = [[float('inf') for _ in range(len(self.keys))] for _ in range(len(self.keys))]

        for key, value in self.topologia[self.graph].items():
            array_topologia[self.keys.index(self.graph)][self.keys.index(key)] = value

        return array_topologia

    '''
        Communicate with other nodes.
            - If the routing table is not complete, it allows echo and sending information.
            - If the table is already full, it allows communication.
    '''
    def main(self):
        # Select the current terminal node
        print(f"\nSelected Node: {self.graph}")
        for key, value in self.topologia.items():
            if key == self.graph:
                print(f"Neighbors:")
                for key, value in value.items():
                    print(f"{key}: {value}")

        # If the selected node is the first one, create the first information packet
        if self.graph == self.keys[0]:
            self.broadcast_table()

        while True:
            if not self.mensajes:
                # Receive the information packet
                incoming_tabla = self.convert_to_dict()

                # Depending on the packet type, execute a function
                type = incoming_tabla["type"]

                if type == "info":          # Receive the routing table
                    self.bellman_ford(incoming_tabla)
                
                elif type == "echo":        # Receive an echo
                    self.echo(incoming_tabla)

                elif type == "message":     # Receive a message
                    print("The node is not yet ready to receive messages.")
            
            else:
                opt = self.customMenu(["Enviar mensaje.", "Recibir | retransmitir mensaje.", "Salir"], "MENSAJES")

                if opt == 1:
                    while True:
                        nodo = input("A qué nodo le quieres enviar el mensaje?: ")

                        if nodo in self.keys:
                            if nodo == self.graph:
                                print("No puedes enviarte un mensaje a ti mismo.")
                            else:
                                break
                        else:
                            print("Nodo no encontrado. Ingrese un nodo válido.")
                    
                    mensaje = input("Ingresa tu mensaje: ")

                    print("\nMensaje recibido. Enviando...")
                    # No need to use 'enlaces' in Bellman-Ford, so remove the next line
                    # camino = self.pathfinding(nodo)
                    
                    # Send the message directly to the destination 'nodo'
                    mensaje_json = json.dumps({
                        "type": "message",
                        "headers": {"from": self.graph, "to": nodo, "hop_count": 0},  # Hop count can be set to 0
                        "payload": mensaje
                    })
                    
                    print(f"\n{mensaje_json}")

                elif opt == 2:
                    tabla = self.convert_to_dict()

                    header_from = tabla["headers"]["from"]
                    header_to = tabla["headers"]["to"]

                    if header_to == self.graph:
                        print(f"\nMensaje de {header_from}: {tabla['payload']}")
                        print(f"El mensaje ha llegado a su destino.")

                    else:
                        
                        print("\nMensaje recibido. Retransmitiendo...")
                        camino = self.pathfinding(header_to)
                        print(f"\nCamino más corto: {camino}")
                        print(f"Enviar el siguiente paquete a {camino[1]} ...")

                        tabla["headers"]["hop_count"] -= 1
                        
                        if tabla["headers"]["hop_count"] == 0:
                            print(f"\nMensaje de {header_from} para {header_to}: {tabla['payload']}")
                            print(f"El mensaje no ha llegado a su destino. Se acabaron los saltos.")

                        else:
                            tabla_send = json.dumps(tabla)
                            print(f"\n{tabla_send}")

                elif opt == 3:
                    exit()

    '''
        After calculating the shortest distances, generate the shortest path
    '''
    def pathfinding(self, destination):
        current = self.keys.index(destination)
        path = []

        while current != -1:
            path.insert(0, current)
            # You can directly use self.tabla to find the next node.
            current = self.find_next_node(current)

        path_names = [self.keys[i] for i in path]

        return path_names
    
    def find_next_node(self, current):
        # Find the next node in the shortest path based on the current node's distance.
        # You should iterate through self.tabla to find the minimum distance neighbor.
        min_distance = float('inf')
        next_node = -1

        for i, distance in enumerate(self.tabla[current]):
            if 0 < distance < min_distance:
                min_distance = distance
                next_node = i

        return next_node

    '''
        Receive routing information and update it. 
            - If the tables are already full, calculate the shortest distances using Bellman-Ford.
    '''
    def bellman_ford(self, info):
        # If the table is incomplete, update it if there is a change
        if self.is_empty(self.tabla):
            tabla = info["payload"]
            original_tabla = self.tabla

            # Check if dimensions match before updating
            if len(tabla) != len(original_tabla) or len(tabla[0]) != len(original_tabla[0]):
                print("Received table dimensions do not match the current table.")
            else:
                if not self.are_nested_arrays_equal(tabla, original_tabla):
                    # Update original_tabla with the values from tabla
                    for i in range(len(tabla)):
                        for j in range(len(tabla[i])):
                            if original_tabla[i][j] == float('inf'):
                                original_tabla[i][j] = tabla[i][j]

                    self.tabla = original_tabla

                    print("Table updated.\n")

                    self.broadcast_table()



        if not self.is_empty(self.tabla):
            print("---------------------------")
            print(f"\nCURRENT TABLE:\n {self.tabla}")
            print("\nNode ready to receive and send messages.\n")
            print("---------------------------")

            start = self.keys.index(self.graph)
            num_nodes = len(self.tabla)
            visited = [False for _ in range(num_nodes)]
            distance = [float('inf') for _ in range(num_nodes)]
            distance[start] = 0

            for _ in range(num_nodes - 1):
                for u in range(num_nodes):
                    for v in range(num_nodes):
                        if self.tabla[u][v] != float('inf'):
                            if distance[u] + self.tabla[u][v] < distance[v]:
                                distance[v] = distance[u] + self.tabla[u][v]

            # self.enlaces = self.reconstruct_path(start, distance)

            self.mensajes = True

    '''
        If an echo is received, listen to it and return something depending on whether they are nodes.
            - If the node that echoed is adjacent, echo it back.
    '''
    def echo(self, info):
        origin = info["headers"]["from"]
        destination = info["headers"]["to"]

        if origin in self.topologia[destination]:
            echo_table = {"type": "echo",
                          "headers": {"from": self.graph, "to": origin, "hop_count": 2},
                          "payload": "ping"}
        
            echo_json = json.dumps(echo_table)
            print(f"ECHO: {echo_json}")

        else:
            echo_table = {"type": "None"}

            echo_json = json.dumps(echo_table)
            print(f"ECHO: {echo_json}")

    '''
        Send an echo and wait for an echo back
    '''
    def send_echo(self, destination):
        echo_table = {"type": "echo",
                      "headers": {"from": self.graph, "to": destination, "hop_count": 1},
                      "payload": "ping"}
        
        echo_json = json.dumps(echo_table)
        print(f"\nECHO: {echo_json}")
        print("ECHO sent successfully. Waiting for a response...")
        echo_response = self.convert_to_dict()

        if echo_response != None and echo_response["type"] == "echo":
            print("ECHO received successfully")
            return True
        
        else:
            print("ECHO not received")
            return False
        
    '''
        Send the routing table to its neighbors via broadcast
    '''
    def broadcast_table(self):
        if not self.is_empty(self.tabla):
            return
        
        # Send an echo to all neighbors
        if not self.done:
            print("\n---------------------------")
            for key, value in self.topologia[self.graph].items():
                if key != self.graph and value != 0:
                    self.send_echo(key)        # Send an echo to each neighbor and wait for a response
                    self.done = True
                    print("---------------------------")

        # Print the routing tables to be shared
        for key, value in self.topologia[self.graph].items():
            if key != self.graph and value != 0:
                    
                    # Create the first information packet
                    string_array = str(self.tabla)
                    tabla = {"type": "info", 
                            "headers": {"from": self.graph, "to": key, "hop_count": 1},
                            "payload": self.tabla}
                    
                    tabla_send = json.dumps(tabla)  # Send the information packet
                    print(f"\n{tabla_send}")

    # ------------ MENUS and TOOLS

    def customMenu(self, options, menu):
        while True:
            print(f"\n----- {menu} -----")
            for i in range(len(options)):
                print(f"{i+1}) {options[i]}")

            try:
                opcion = int(input("Enter the number of the desired option: "))
                if opcion in range(1, len(options) + 1):
                    return opcion
                else:
                    print(f"\n--> Invalid option. Please enter a number from 1 to {len(options)}.\n")

            except ValueError:
                print("\n--> Invalid input. Please enter an integer.\n")

    def convert_to_dict(self):
        try:
            input_str = input("\nEnter your JSON packet: ")
            data = json.loads(input_str)
            return data
        except json.JSONDecodeError as err:
            print(err)
            return None
        
    def select_node(self):
        with open('estructura.txt', 'r') as file:
            data = file.read().replace('\n', '')
        data = json.loads(data)

        with open('topologia.txt', 'r') as file:
            topologia = file.read().replace('\n', '')
        self.topologia = json.loads(topologia)

        while True:
            print("\n---BELLMAN-FORD---\nSelect a node from the list: ")
            self.keys = list(data.keys())
            for i, key in enumerate(data):
                print(f"{i+1}. {key}")

            try:
                node = int(input("Enter the number of the node: "))
                if node > 0 and node <= len(data):
                    return self.keys[node - 1]
                else:
                    print("Enter a valid number")

            except ValueError:
                print("Enter a valid number")

    def are_nested_arrays_equal(self, arr1, arr2):
        if len(arr1) != len(arr2):
            return False
        
        for i in range(len(arr1)):
            if isinstance(arr1[i], list) and isinstance(arr2[i], list):
                if not self.are_nested_arrays_equal(arr1[i], arr2[i]):
                    return False
            else:
                if arr1[i] != arr2[i]:
                    return False
        
        return True

    def is_empty(self, tabla):
        for i in range(len(tabla)):
            for j in range(len(tabla[i])):
                if tabla[i][j] == float('inf'):
                    return True
        
        return False
    
    def convert_to_dict(self):
        try:
            input_str = input("\nEnter your JSON packet: ")
            data = json.loads(input_str)
            return data
        except json.JSONDecodeError as err:
            print(f"JSON decoding error: {err}")
            return None



bellman_ford_instance = BellmanFord()
