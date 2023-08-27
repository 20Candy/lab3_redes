import json

class FloodingSimulation():
    def __init__(self):
        self.graph = self.select_node()
        self.main()

    def main(self):
        while True:
            option = self.customMenu(["Enviar mensaje.", "Recibir mensaje.", "Salir"], "FLOODING")

            if option == 1:
                message = input("Ingrese su mensaje: ")
                self.flood_message(message)

            elif option == 2:
                received_message = self.receive_message()
                if received_message:
                    print(f"Mensaje recibido: {received_message}")

            elif option == 3:
                exit()

    def flood_message(self, message):
        packet = {
            "type": "message",
            "source": self.graph,
            "message": message
        }

        packet_json = json.dumps(packet)
        print(f"Enviando mensaje: {packet_json}")

    def receive_message(self):
        packet = self.convert_to_dict()

        if packet and packet["type"] == "message":
            return packet["message"]

        return None

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
