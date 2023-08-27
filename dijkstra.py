import json

class Dijkstra():
    def __init__(self):
        self.done = False
        self.mensajes = False
        self.graph = self.select_node()
        self.tabla = self.tabla_enrutamiento()
        self.main()

    '''
        Genera la tabla de enrutamiento de cada nodo. 
            - Almacena los pesos de cada relación entre nodos. 
            - Se va llenando por broadcast
    '''
    def tabla_enrutamiento(self):
        # Se genera la tabla de enrutamiento
        array_topologia = [[9999 for i in range(len(self.keys))] for j in range(len(self.keys))]

        for key, value in self.topologia[self.graph].items():
                array_topologia[self.keys.index(self.graph)][self.keys.index(key)] = value

        return array_topologia

    '''
        Permite comunicarrse con otros nodos.
            - Si la tabla de enrutamiento no está completa, permite hacer echo y enviar info.
            - Si la tabla ya está llena, permite comunicarse
    '''
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
                    camino = self.pathfinding(nodo)
                    print(f"\nCamino más corto: {camino}")
                    print(f"Enviar el siguiente paquete a {camino[1]} ...")

                    # Se crea el mensaje
                    tabla = {"type":"message", 
                        "headers": {"from": f"{self.graph}", "to": f"{nodo}", "hop_count": len(camino)},
                        "payload": mensaje}
                    
                    tabla_send = json.dumps(tabla)  # Se envía el paquete de información
                    print(f"\n{tabla_send}")

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
        Después de haber calculado las distancias más cortas, se genera el camino más corto
    '''
    def pathfinding(self, destino):
        camino_actual = []
        current = self.keys.index(destino)
        while current != -1:
            camino_actual.insert(0, current)
            current = self.enlaces[current]

        camino_nombres = []

        for i in camino_actual:
            camino_nombres.append(self.keys[i])

        return camino_nombres


    '''
        Recibe información de las tablas de enrutamiento y las actualiza. 
            - Si las tablas ya están llenas, con Dijkstra calcula las distancias más cortas.
    '''
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

            inicio = self.keys.index(self.graph)

            cant_nodos = len(self.tabla)
            visitado = [False for _ in range(cant_nodos)]
            costo_enlace = [float('inf') for _ in range(cant_nodos)]
            enlace = [-1 for _ in range(cant_nodos)]
            costo_enlace[inicio] = 0

            for _ in range(cant_nodos):
                min_distance = float('inf')
                min_node = -1

                for node in range(cant_nodos):
                    if not visitado[node] and costo_enlace[node] < min_distance:
                        min_distance = costo_enlace[node]
                        min_node = node

                if min_node == -1:
                    break

                visitado[min_node] = True

                for neighbor in range(cant_nodos):
                    if (not visitado[neighbor] and
                            self.tabla[min_node][neighbor] > 0 and
                            costo_enlace[min_node] + self.tabla[min_node][neighbor] < costo_enlace[neighbor]):
                        costo_enlace[neighbor] = costo_enlace[min_node] + self.tabla[min_node][neighbor]
                        enlace[neighbor] = min_node

            self.enlaces = enlace
            self.costo_enlaces = costo_enlace

            self.mensajes = True

    '''
        Si se hace echo, lo escucha y dependiendo de si son nodos, retorna algo.
            - Si el nodo que hizo echo es adyacente, le hace echo de regreso.
    '''
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

    '''
        Envia un echo y espera para que le hagan echo de regreso
    '''
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
        
    '''
        Le envia a sus vecinos su tabla de enrutamiento por broadcast
    '''
    def broadcast_table(self):
        if not self.is_empty(self.tabla):
            return
        
        # Le manda a todos los vecinos un echo
        if not self.done:
            print("\n---------------------------")
            for key, value in self.topologia[self.graph].items():
                if key != self.graph and value != 0:
                    self.send_echo(key)        # Se envía un echo a cada vecino y se espera respuesta
                    self.done = True
                    print("---------------------------")

        # Imprime las tablas de enrutamiento que tiene que compartir
        for key, value in self.topologia[self.graph].items():
            if key != self.graph and value != 0:
                    
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


main = Dijkstra()