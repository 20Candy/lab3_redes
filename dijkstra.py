import json

class Dijkstra():
    def __init__(self):
        self.done = False
        self.mensajes = False
        self.graph = self.select_node()
        self.tabla = self.tabla_enrutamiento()
        self.main()

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

        # Si el nodo seleccionado es el primero, se crea el primer paquete de información
        if self.graph == self.keys[0]:
            self.broadcast_table()

        while True:

            if not self.mensajes:
                # Se recibe el paquete de información
                incoming_tabla = self.convert_to_dict()

                # Dependiendo del tipo de paquete, se ejecuta una función
                type = incoming_tabla["type"]

                if type == "info":          # Se recibe la tabla de enrutamiento
                    self.dijkstra(incoming_tabla)
                
                elif type == "echo":        # Se recibe un echo
                    self.echo(incoming_tabla)

                elif type == "message":     # Se recibe un mensaje
                    print("El nodo aún no está listo para recibir mensajes.")

            else:
                opt = self.customMenu(["Enviar mensaje.", "Recibir mensaje.", "Salir"], "MENSAJES")

                if opt == 1:
                    nodo = input("A qué nodo le quieres enviar el mensaje?: ")
                    mensaje = input("Ingresa tu mensaje: ")

                    # Se crea el mensaje
                    string_array = str(self.tabla)
                    tabla = {"type":"message", 
                        "headers": {"from": f"{self.graph}", "to": f"{nodo}", "hop_count": 3},
                        "payload": mensaje}
                    
                    tabla_send = json.dumps(tabla)  # Se envía el paquete de información
                    print(f"\n{tabla_send}")

                elif opt == 2:
                    tabla = self.convert_to_dict()

                elif opt == 3:
                    exit()

    def pathfinding(self, origen, destino):
        pass

    def dijkstra(self, info):
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

        if not self.is_empty(self.tabla):
            print("---------------------------")
            print(f"\nTABLA ACTUAL:\n {self.tabla}")
            print("\nNodo listo para recibir y enviar mensajes.\n")
            print("---------------------------")

            # Crea la tabla inicial
            dijkstra_table = [[self.keys[0]],[[[9999,"-"] for i in range(len(self.keys)-1)] for j in range(len(self.keys))]]
            current_node = self.keys[0]
            visitados = dijkstra_table[0]

            # Lleva la primera fila
            for i, value in enumerate(self.tabla[0]):
                if i != 0:
                    dijkstra_table[1][0][i-1] = [value, current_node]


            valores = []
            for llave, i in enumerate(dijkstra_table[1][0]):
                if i[0] <= 0:
                    valores.append(999)
                elif i[1] in visitados and self.keys[llave+1] in visitados:
                    valores.append(999)
                else:
                    valores.append(i[0])

            minimo = min(valores)
            indice = valores.index(minimo) + 1
            current_node = self.keys[indice]
            dijkstra_table[0].append(current_node)

            while len(dijkstra_table[0]) != len(self.keys):

                # Se obtiene la fila de la tabla de enrutamiento
                numero_tabla = self.keys.index(current_node)
                info_actual = self.tabla[numero_tabla]

                # Visitados
                visitados = dijkstra_table[0]

                # Se obtiene la ultima fila llenada de dijkstra
                last_row_dijkstra = dijkstra_table[1][len(visitados)-2]

                for i, value in enumerate(info_actual):

                    if i == 0:      # Si es el primer nodo (para el cual no hay columna)
                        continue

                    valor_original = last_row_dijkstra[i-1][0]              # Revisa el valor de la última tabla
                    valor_nuevo = last_row_dijkstra[indice-1][0] + value    # Determina el valor nuevo posible

                    if value <= 0:
                        dijkstra_table[1][len(visitados)-1][i-1] = last_row_dijkstra[i-1]
                    
                    elif valor_nuevo < valor_original:
                        dijkstra_table[1][len(visitados)-1][i-1] = [valor_nuevo, current_node]

                    else:
                        dijkstra_table[1][len(visitados)-1][i-1] = last_row_dijkstra[i-1]


                tabla_actualizada = dijkstra_table[1][self.keys.index(current_node)-1]

                valores = []
                for llave, i in enumerate(tabla_actualizada):
                    if i[0] <= 0:
                        valores.append(999)
                    elif i[1] in visitados and self.keys[llave+1] in visitados:
                        valores.append(999)
                    else:
                        valores.append(i[0])

                minimo = min(valores)
                indice = valores.index(minimo) + 1
                current_node = self.keys[indice]
                dijkstra_table[0].append(current_node)

            self.mensajes = True

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
            return
        
        # Le manda a todos los vecinos un echo
        if not self.done:
            print("\n---------------------------")
            for key, value in self.topologia[self.graph].items():
                if key != self.graph and value != 0:
                    #self.send_echo(key)        # Se envía un echo a cada vecino y se espera respuesta
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


main = Dijkstra()