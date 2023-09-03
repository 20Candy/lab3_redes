import json

class DistanceVector():
    def __init__(self):
        self.done = False
        self.mensajes = False
        self.graph = self.select_node()
        self.tabla = self.tabla_enrutamiento()
        self.main()

    '''
        Genera la tabla de enrutamiento de cada nodo. 
            - Almacena los pesos de cada relación entre nodos. 
    '''
    def tabla_enrutamiento(self):
        array_topologia = [float('inf') for _ in range(len(self.keys))]

        self.enlaces = [None for _ in range(len(self.keys))]

        for key, value in self.topologia[self.graph].items():
                array_topologia[self.keys.index(key)] = value

                if value == 0:
                    self.enlaces[self.keys.index(key)] = ""

                else:
                    self.enlaces[self.keys.index(key)] = key

        return array_topologia

    '''
        Permite comunicarrse con otros nodos.
    '''
    def main(self):
        
        # Se selecciona que nodo representa la terminal actual
        print(f"\nNodo seleccionado: {self.graph}")
        for key, value in self.topologia.items():
            if key == self.graph:
                print(f"Vecinos:")
                for key, value in value.items():
                    print(f"{key}: {value}")

        self.broadcast_table()

        while True:
                opt = self.customMenu(["Recibir distance vector.", "Enviar mensaje.", "Recibir | retransmitir mensaje.", "Salir"], "DISTANCE VECTOR ROUTING")

                if opt == 1:
                    tabla = self.convert_to_dict()

                    if tabla["type"] == "info":
                        self.bellman_ford(tabla)
                    else:
                        print("Paquete no válido. Ingrese un paquete válido.")


                elif opt == 2:
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

                    camino = self.enlaces[self.keys.index(nodo)]
                    print(f"*Enviar el siguiente paquete a {camino}...*")

                    # Se crea el mensaje a enviar
                    tabla = {"type":"message", 
                        "headers": {"from": f"{self.graph}", "to": f"{nodo}", "hop_count": self.tabla[self.keys.index(nodo)]},
                        "payload": mensaje}
                    
                    tabla_send = json.dumps(tabla)  # Se envía el paquete de información
                    print(f"\n{tabla_send}")

                elif opt == 3:
                    tabla = self.convert_to_dict()

                    header_from = tabla["headers"]["from"]
                    header_to = tabla["headers"]["to"]

                    if header_to == self.graph:
                        print(f"\nMensaje de {header_from}: {tabla['payload']}")
                        print(f"El mensaje ha llegado a su destino.")
                        
                    else:
                        print("\nMensaje recibido. Retransmitiendo...")

                        camino = self.enlaces[self.keys.index(nodo)]
                        print(f"*Enviar el siguiente paquete a {camino}...*")

                        tabla["headers"]["hop_count"] -= 1
                        if tabla["headers"]["hop_count"] == 0:
                            print(f"\nMensaje de {header_from} para {header_to}: {tabla['payload']}")
                            print(f"El mensaje no ha llegado a su destino. Se acabaron los saltos.")

                        else:
                            tabla_send = json.dumps(tabla)
                            print(f"\n{tabla_send}")

                elif opt == 4:
                    exit()

    '''
        Recibe información de los vectores de distance y las actualiza. 
            - 
    '''
    def bellman_ford(self, info):
        received_table = json.loads(info["payload"])
        origin = info["headers"]["from"]

        print(f"\n--> Vector de distancia recibido de {origin}.")

        # Costo del nodo actual al nodo origen
        cost_to_origin = self.tabla[self.keys.index(origin)]
        updates_occurred = False

        # Revisa con Bellman-Ford si el costo total es menor al costo actual
        for i, new_cost in enumerate(received_table):
            total_cost = cost_to_origin + new_cost

            if total_cost < self.tabla[i]:
                self.tabla[i] = total_cost
                self.enlaces[i] = origin
                updates_occurred = True

        # Print the updated routing table
        if updates_occurred:
            self.broadcast_table()

    '''
        Le envia a sus vecinos su tabla de enrutamiento por broadcast
    '''
    def broadcast_table(self):
        # Imprime las tablas de enrutamiento que tiene que compartir
        for key, value in self.topologia[self.graph].items():
            if key != self.graph and value != 0 and value != float('inf') and value != 9999:

                # Se crea el primer paquete de información
                string_array = str(self.tabla)
                tabla = {"type":"info", 
                    "headers": {"from": f"{self.graph}", "to": f"{key}", "hop_count": 1},
                    "payload": string_array}
                
                tabla_send = json.dumps(tabla)  # Se envía el paquete de información
                print(f"\n{tabla_send}")

# ------------ MENUS y HERRAMIENTAS

    def customMenu(self, options, menu):
        while True:
            print(f"\n----- {menu} -----")
            for i in range(len(options)):
                print(f"{i+1}) {options[i]}")

            try:
                opcion = int(input("Ingrese el número de la opción deseada: "))
                if opcion in range(1, len(options)+1):
                    return opcion
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
        with open('estructura.txt', 'r') as file:
            data = file.read().replace('\n', '')
        data = json.loads(data)

        with open('topologia.txt', 'r') as file:
            topologia = file.read().replace('\n', '')
        self.topologia = json.loads(topologia)


        while True:
            print("\n---DISTANCE VECTOR ROUTING---\nSeleccione un nodo de la lista: ")
            self.keys = list(data.keys())
            for i, key in enumerate(data):
                print(f"{i+1}. {key}")

            try:
                node = int(input("Ingrese el número del nodo: "))
                if node > 0 and node <= len(data):
                    return self.keys[node-1]
                else:
                    print("Ingrese un número válido")

            except ValueError:
                print("Ingrese un número válido")

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
            if tabla[i] == 9999:
                return True
        
        return False


main = DistanceVector()