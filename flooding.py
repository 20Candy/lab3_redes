import json

class FloodingSimulation():
    def __init__(self):
        self.graph = self.select_node()
        self.sent_messages = set()  # Historial de mensajes enviados
        self.received_from = None  # Nodo que le envió el último mensaje
        self.available_nodes = self.getAvailableNodes()
        self.main()

    def getAvailableNodes(self):
        with open('topologia.txt', 'r') as file:
            data = json.load(file)

        nodes = list(data.keys())

    def getNeighbors(self, node):
        with open('topologia.txt', 'r') as file:
            data = json.load(file)

        neighbors = list(data[node].keys())
        return neighbors

    def main(self):
        while True:
            option = self.customMenu(["Enviar mensaje.", "Recibir mensaje.", "Salir"], "FLOODING")

            if option == 1:
                while True:
                    nodo = input("A qué nodo le quieres enviar el mensaje?: ")
                    
                    if nodo in self.getNeighbors(self.graph):
                        if nodo == self.graph:
                            print("No puedes enviarte un mensaje a ti mismo.")
                        else:
                            break
                    else:
                        print("Nodo no es tu vecino / no encontrado. Ingrese un nodo válido.")

                message = input("Ingrese su mensaje: ")
                self.flood_message(message, nodo)

            elif option == 2:
                received_message, new_json = self.receive_message()
                if received_message:
                    print(f"\nMensaje recibido: {received_message}")

                if new_json:
                    print(f"\nNuevo paquete JSON: {new_json}")

            elif option == 3:
                exit()

    def flood_message(self, message, node):
        if self.received_from != self.graph or message not in self.sent_messages:
            # Reiniciar la lista de nodos visitados para un nuevo mensaje
            visited_nodes = [self.graph]

            visiting = self.getNeighbors(self.graph)
            visiting.remove(self.graph)

            print(f"\n*copiar y pegar en terminales: {visiting}*")

            packet = {
                "type": "message",
                "headers": {
                    "from": self.graph,
                    "to": node,
                    "visited": visited_nodes
                },
                "payload": message
            }
            self.sent_messages.add(message)
            self.received_from = self.graph

            packet_json = json.dumps(packet)
            print(f"Enviando mensaje: {packet_json}")
        else:
            print("Mensaje no enviado. Ya se envió un mensaje desde este nodo con contenido similar.")


    def receive_message(self):
        packet = self.convert_to_dict()

        if packet and packet["type"] == "message":
            source = packet["headers"]["from"]
            destination = packet["headers"]["to"]

            if destination == self.graph:
                message = "\n\nEmisor: " + source + "\nMensaje: " + packet["payload"]
                return message, None

            if self.graph not in packet["headers"]["visited"]:
                self.received_from = source

                # Agregar el nodo actual a la lista de nodos visitados
                packet["headers"]["visited"].append(self.graph)

                visiting = self.getNeighbors(self.graph)
                visiting.remove(self.graph)

                send_to = [node for node in visiting if node not in packet["headers"]["visited"]]

                mensaje = f"\n*retransmitir mensaje a {send_to}*"
                return mensaje, json.dumps(packet)

        return None, None

    def customMenu(self, options, menu):
        while True:
            print(f"\n----- {menu} -----")
            for i in range(len(options)):
                print(f"{i+1}) {options[i]}")

            try:
                choice = int(input("Ingrese el número de la opción deseada: "))
                if choice in range(1, len(options)+1):
                    return choice
                else:
                    print(f"\n--> Opción no válida. Por favor, ingrese un número del 1 al {len(options)}.\n")

            except ValueError:
                print("\n--> Entrada inválida. Por favor, ingrese un número entero.\n")

    def convert_to_dict(self):
        try:
            input_str = input("\nIngrese su paquete JSON: ")
            data = json.loads(input_str)
            return data
        except json.JSONDecodeError as err:
            print(err)
            return None

    def select_node(self):
        while True:
            print("\n---FLOODING SIMULATION---")
            nodes = ["A", "B", "C"]
            for i, node in enumerate(nodes):
                print(f"{i+1}. Node {node}")

            try:
                node_index = int(input("Ingrese el número del nodo: "))
                if node_index > 0 and node_index <= len(nodes):
                    return nodes[node_index - 1]
                else:
                    print("Ingrese un número válido")

            except ValueError:
                print("Ingrese un número válido")

flooding_sim = FloodingSimulation()
