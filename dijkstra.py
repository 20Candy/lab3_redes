import json

class Dijkstra():

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
            print("\n---DIJKSTRA---\nSeleccione un nodo de la lista: ")
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

    def __init__(self):
        self.done = False
        self.graph = self.select_node()
        self.tabla = self.tabla_enrutamiento()
        self.main()

    def tabla_enrutamiento(self):
        # Se genera la tabla de enrutamiento
        array_topologia = [[9999 for i in range(len(self.keys))] for j in range(len(self.keys))]

        for key, value in self.topologia[self.graph].items():
                array_topologia[self.keys.index(self.graph)][self.keys.index(key)] = value

        return array_topologia

    def main(self):
        
        # Se selecciona que nodo representa la terminal actual
        print(f"\nNodo seleccionado: {self.graph}")
        for key, value in self.topologia.items():
            if key == self.graph:
                print(f"Vecinos:")
                for key, value in value.items():
                    print(f"{key}: {value}")

        tabla = {}
        # Si el nodo seleccionado es el primero, se crea el primer paquete de información
        if self.graph == self.keys[0]:
            self.broadcast_table()

        while True:

            incoming_tabla = self.convert_to_dict()

            type = incoming_tabla["type"]

            if type == "info":
                self.dijkstra(incoming_tabla)
            
            elif type == "echo":
                self.echo(incoming_tabla)

            elif type == "message":
                pass

    def dijkstra(self, info):
        origin = info["headers"]["from"]
        destino = info["headers"]["to"]

        # Si la tabla está incompleta, se actualiza si hay un cambio
        if self.is_empty(self.tabla):

            tabla = json.loads(info["payload"].replace("'", '"'))
            original_tabla = self.tabla

            if not self.are_nested_arrays_equal(tabla, original_tabla):
                # Actualizar original_tabla con los valores de tabla
                for i in range(len(tabla)):
                    for j in range(len(tabla[i])):
                        if original_tabla[i][j] == 9999:
                            original_tabla[i][j] = tabla[i][j]

                self.tabla = original_tabla

                print("Tabla actualizada.\n")

                self.broadcast_table()

        else:
            print("---------------------------")
            print(f"\nTABLA ACTUAL:\n {self.tabla}")
            print("\nNodo listo para recibir y enviar mensajes.\n")
            print("---------------------------")

    def echo(self, info):
        origin = info["headers"]["from"]
        destino = info["headers"]["to"]

        if origin in self.topologia[destino]:
            tabla = {"type":"echo", 
                    "headers": {"from": f"{self.graph}", "to": f"{origin}", "hop_count": 2},
                    "payload": "ping"}
        
            tabla_json = json.dumps(tabla)
            print(f"ECHO: {tabla_json}")

        else:
            tabla = {"type":"None"}

            tabla_json = json.dumps(tabla)
            print(f"ECHO: {tabla_json}")

    def send_echo(self, destino):
        tabla = {"type":"echo", 
                    "headers": {"from": f"{self.graph}", "to": f"{destino}", "hop_count": 1},
                    "payload": "ping"}
        
        tabla_json = json.dumps(tabla)
        print(f"\nECHO:  {tabla_json}")
        print("ECHO enviado exitosamente. Esperando respuesta...")
        echo_regreso = self.convert_to_dict()

        if echo_regreso != None and echo_regreso["type"] == "echo":
            print("ECHO recibido exitosamente")
            return True
        
        else:
            print("ECHO no recibido")
            return False
        
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
                if tabla[i][j] == 9999:
                    return True
        
        return False

    def broadcast_table(self):
        if not self.is_empty(self.tabla):
            print("---------------------------")
            print(f"\nTABLA ACTUAL:\n {self.tabla}")
            print("\nNodo listo para recibir y enviar mensajes.")
            print("---------------------------")
            return
        
        # Le manda a todos los vecinos un echo
        if not self.done:
            print("\n---------------------------")
            for key, value in self.topologia[self.graph].items():
                if key != self.graph and value != 0:
                    self.send_echo(key)        # Se envía un echo a cada vecino y se espera respuesta
                    self.done = True
                    print("---------------------------")

        # Le manda a todos los vecinos un echo
        for key, value in self.topologia[self.graph].items():
            if key != self.graph and value != 0:
                    
                    # Se crea el primer paquete de información
                    string_array = str(self.tabla)
                    tabla = {"type":"info", 
                        "headers": {"from": f"{self.graph}", "to": f"{key}", "hop_count": 1},
                        "payload": string_array}
                    
                    tabla_send = json.dumps(tabla)  # Se envía el paquete de información
                    print(f"\n{tabla_send}")
        return



        
        self.broadcast_table()

main = Dijkstra()