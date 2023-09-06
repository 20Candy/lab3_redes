import json
import slixmpp
import asyncio
import aioconsole 
import sys

class Server(slixmpp.ClientXMPP):

    '''
    init: Constructor de la clase Server. Inicializa los handlers de eventos y el estado de logged_in.
    '''

    def __init__(self, jid, password):
        self.email = jid
        self.old = True
        self.enlaces = [] 

        super().__init__(jid, password)
        #-----> Plugins generados por GitHub Copilot
        self.register_plugin('xep_0030')                                   # Registrar plugin: Service Discovery
        self.register_plugin('xep_0045')                                   # Registrar plugin: Multi-User Chat
        self.register_plugin('xep_0085')                                   # Registrar plugin: Chat State Notifications
        self.register_plugin('xep_0199')                                   # Registrar plugin: XMPP Ping
        self.register_plugin('xep_0353')                                   # Registrar plugin: Chat Markers
        #-------------------------------

        #-----> Handlers de eventos
        self.add_event_handler("session_start", self.start)                 # Handler para cuando se inicia sesión
        self.add_event_handler("message", self.message)                     # Handler para cuando se recibe un mensaje

        self.logged_in = False
        self.topologia = None

        self.echo_send = []
        self.echoed = []

        self.traza_mensajes = []
        

    #-------------------------------------------------------------------------------------------------------------------
    '''
    start: Función que se ejecuta al iniciar sesión en el servidor de forma asincrónica.
    '''

    async def start(self, event):
        try:
            self.send_presence()                                            # Enviar presencia  
            self.get_roster()                                               # Obtener roster   

            await asyncio.sleep(2)
            self.old = False
            self.tabla = await self.tabla_enrutamiento()             # Generar tabla de enrutamiento

            print("\n\n----- NOTIFICACION: ECHO -----")

            #-----> Enviar a vecinos echo
            for key in self.topologia[self.graph]:

                if key != self.graph:
                    tabla = {"type":"echo", 
                    "headers": {"from": f"{self.graph}", "to": f"{key}", "hop_count": 1},
                    "payload": "ping"}
                    
                    tabla_send = json.dumps(tabla)
                    email_destino = self.keys[key]

                    print(f"\n--> Enviando echo a {email_destino}...")

                    self.echo_send.append(email_destino)
                    self.send_message(mto=email_destino, mbody=tabla_send, mtype='chat')         # Enviar mensaje con librería slixmpp
            
            print("--------------------------------")

            #-----> Generado por ChatGPT
            xmpp_menu_task = asyncio.create_task(self.xmpp_menu())          # Creación de hilo para manejar el menú de comunicación
            #---------------------------
            
            await xmpp_menu_task            

        except Exception as e:
            print(f"Error: {e}")


    #-------------------------------------------------------------------------------------------------------------------
    '''
    xmpp_menu: Función que muestra el menú de comunicación y ejecuta las funciones correspondientes a cada opción.
    '''

    async def xmpp_menu(self):
        self.logged_in = True

        print("\n---------- MENSAJES / NOTIFICACIONES ----------")
        await asyncio.sleep(5)

        opcion_comunicacion = 0
        while opcion_comunicacion != 4:

            opcion_comunicacion = await self.mostrar_menu_comunicacion()

            if opcion_comunicacion == 1:
                # Mostrar tabla de enrutamiento
                print("\n----- TABLA DE ENRUTAMIENTO -----")
                print(self.tabla)
                await asyncio.sleep(1)

            elif opcion_comunicacion == 2:
                await self.bellman_ford()
                await asyncio.sleep(1)

            elif opcion_comunicacion == 3:
                # Enviar mensaje a un usuario
                await self.send_msg_to_user()
                await asyncio.sleep(1)

            elif opcion_comunicacion == 4:
                # Cerrar sesión con una cuenta
                print("\n--> Sesión cerrada. Hasta luego.")
                self.disconnect()
                exit()

    #-------------------------------------------------------------------------------------------------------------------
    '''
    send_msg_to_user: Función que envía un mensaje a un usuario.
    '''

    async def send_msg_to_user(self):
        print("\n----- ENVIAR MENSAJE A USUARIO -----")

        node_name = None
        while True:
            print("Seleccione un nodo de la lista: ")
            keys = list(value for key, value in self.keys.items())
            keys_nodes = list(key for key, value in self.keys.items())

            for i, key in enumerate(keys):
                print(f"{i+1}. {key}")

            try:
                node = await aioconsole.ainput("Ingrese el número del nodo: ")
                node = int(node)
                if node > 0 and node <= len(self.keys):
                    if self.graph == keys_nodes[node-1]:
                        print("--> No puede enviar un mensaje a sí mismo.\n")
                        continue
                    else:
                        node_name = keys_nodes[node-1]
                        break
                else:
                    print("Ingrese un número válido")

            except ValueError:
                print("Ingrese un número válido")

        user_input = await aioconsole.ainput("Mensaje: ")                            # Obtener el mensaje a enviar

        tabla = {"type":"message",
                "headers": {"from": f"{self.graph}", "to": f"{node_name}", "hop_count": 1},
                "payload": user_input}
        
        tabla_send = json.dumps(tabla)  # Se envía el paquete de información
        
        camino = await self.pathfinding(node_name)
        print(f"\n--> Camino más corto: {camino}")
        next_node = camino[1]

        recipient_jid = self.keys[next_node]                                        # Obtener el JID del destinatario

        self.send_message(mto=recipient_jid, mbody=tabla_send, mtype='chat')         # Enviar mensaje con librería slixmpp
        print(f"--> Mensaje enviado a {next_node}, con destino a {node_name}.")
        print("----------------------")

    #-------------------------------------------------------------------------------------------------------------------
    '''
    message: Función que se ejecuta de forma asincrónica al recibir un mensaje.
    '''

    async def message(self, msg):

        if self.old:
            return
        
        if msg['type'] == 'chat' and "echo" in msg['body']:
            person = msg['from'].bare                                               # Si se recibe un echo, se obtiene el nombre de usuario

            mensaje_recibido = await self.convert_to_dict(msg['body'].replace("'", '"'))
            hop_count = mensaje_recibido["headers"]["hop_count"]

            if hop_count == 1:

                self.echoed.append(person)
                node_name = ""
                for key, value in self.keys.items():
                    if value == person:
                        node_name = key

                tabla = {"type":"echo", 
                    "headers": {"from": f"{self.graph}", "to": f"{node_name}", "hop_count": 2},
                    "payload": "ping"}
                
                tabla_send = json.dumps(tabla)                    
                self.send_message(mto=person, mbody=tabla_send, mtype='chat')         # Enviar mensaje con librería slixmpp

                self.echo_send.append(person)
                self.echoed.append(person)

                self.echo_send = list(set(self.echo_send))
                self.echoed = list(set(self.echoed))

                print(f"\n--> {person} ha hecho echo. Haciendo echo de vuelta.")
                await self.broadcast_table(person)

            elif hop_count == 2:
                self.echoed.append(person)
                self.echoed = list(set(self.echoed))

                print(f"\n--> {person} ha hecho echo de vuelta.")
                await self.broadcast_table(person)

        elif msg['type'] == 'chat' and "info" in msg['body']:
            
            person = msg['from'].bare                                               # Si se recibe un mensaje, se obtiene el nombre de usuario
            info = await self.convert_to_dict(msg['body'])

            mensaje = info["payload"].replace("'", '"')
            tabla_recibida = json.loads(mensaje)
            original_tabla = self.tabla

            equal = await self.are_nested_arrays_equal(self.tabla, tabla_recibida)

            if not equal:
                print(f"\n--> {person} ha enviado una tabla de enrutamiento. Actualizando...")

                # Actualizar original_tabla con los valores de tabla
                for i in range(len(tabla_recibida)):
                    for j in range(len(tabla_recibida[i])):
                        if original_tabla[i][j] == 9999:
                            original_tabla[i][j] = tabla_recibida[i][j]

                self.tabla = original_tabla
                for nodo in self.echoed:
                    await self.broadcast_table(nodo)
                    await asyncio.sleep(1)

            else:
                print(f"\n--> {person} ha enviado una tabla de enrutamiento. No hay cambios.")

        elif msg['type'] == 'chat' and "message" in msg['body']:
            person = msg['from'].bare                                               # Si se recibe un mensaje, se obtiene el nombre de usuario
            info = await self.convert_to_dict(msg['body'])

            mensaje = info["payload"].replace("'", '"')
            origen = info["headers"]["from"]
            destino = info["headers"]["to"]

            if destino == self.graph:
                email_origen = self.keys[origen]

                print("\n\n----------- MENSAJE -----------")
                print(f"--> {email_origen} ha enviado un mensaje: {mensaje}")
                print("--------------------------------")
                return
            
            else:
                camino = await self.pathfinding(destino)
                next_node = camino[1]

                recipient_jid = self.keys[next_node]                                        # Obtener el JID del destinatario
                tabla = {"type":"message",
                        "headers": {"from": f"{origen}", "to": f"{destino}", "hop_count": 1},
                        "payload": mensaje}
                
                tabla_send = json.dumps(tabla)

                self.send_message(mto=recipient_jid, mbody=tabla_send, mtype='chat')         # Enviar mensaje con librería slixmpp

                print("\n\n----------- MENSAJE -----------")
                print(f"--> {person} ha enviado un mensaje para retransmitir a {next_node}, con destino a {destino}.")
                print("--------------------------------")

        self.traza_mensajes.append(msg)

    #-------------------------------------------------------------------------------------------------------------------
    async def mostrar_menu_comunicacion(self):
        print("\n----- MENÚ DE COMUNICACIÓN -----")
        print("1) Revisar tabla enrutamiento")
        print("2) Calcular rutas más cortas (Distance Vector)")
        print("3) Enviar mensaje")
        print("4) Salir")

        while True:
            try:
                opcion = int(await aioconsole.ainput("Ingrese el número de la opción deseada: "))
                if opcion in range(1, 10):
                    return opcion
                else:
                    print("\n--> Opción no válida. Por favor, ingrese un número del 1 al 9.\n")
            except ValueError:
                print("\n--> Entrada inválida. Por favor, ingrese un número entero.\n")


    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------

    '''
        Genera la tabla de enrutamiento de cada nodo. 
            - Almacena los pesos de cada relación entre nodos. 
            - Se va llenando por broadcast
    '''
    async def tabla_enrutamiento(self):
        with open('topo.txt', 'r') as file:
            topologia = file.read().replace('\n', '').replace("'", '"')
        self.topologia = json.loads(topologia)["config"]

        with open('names.txt', 'r') as file:
            data = file.read().replace('\n', '').replace("'", '"')
        data = json.loads(data)
        self.keys = data["config"]

        # Se genera la tabla de enrutamiento
        array_topologia = [[9999 for i in range(len(self.keys))] for j in range(len(self.keys))]

        # Buscar llave de correo actual
        for key, value in self.keys.items():
            if value == self.email:
                self.graph = key

        keys_temp = list(self.keys.keys())

        # Llenar tabla de enrutamiento inicial
        for key in self.topologia[self.graph]:
            array_topologia[keys_temp.index(self.graph)][keys_temp.index(key)] = 1

        if array_topologia[keys_temp.index(self.graph)][keys_temp.index(self.graph)] == 9999:
            array_topologia[keys_temp.index(self.graph)][keys_temp.index(self.graph)] = 0

        print(f"\nTABLA DE ENRUTAMIENTO INICIAL:\n {array_topologia}")

        return array_topologia

    '''
        Le envia a sus vecinos su tabla de enrutamiento por broadcast
    '''
    async def broadcast_table(self, element=None):

        # Imprime las tablas de enrutamiento que tiene que compartir   

        # Nodo seleccionado
        nodo_name = ""
        for key, value in self.keys.items():
            if value == nodo_name:
                nodo_name = key

        # Se crea el primer paquete de información
        string_array = str(self.tabla)
        tabla = {"type":"info", 
            "headers": {"from": f"{self.graph}", "to": f"{nodo_name}", "hop_count": 1},
            "payload": string_array}
        
        tabla_send = json.dumps(tabla)  # Se envía el paquete de información
    
        print(f"--> Enviando tabla a {element}...")

        self.send_message(mto=element, mbody=tabla_send, mtype='chat')         # Enviar mensaje con librería slixmpp

    '''
        Después de haber calculado las distancias más cortas, se genera el camino más corto
    '''
    async def pathfinding(self, destino):
        camino_actual = []
        keys = list(self.keys.keys())
        
        current = 0
        for i in range(len(keys)):
            if keys[i] == destino:
                current = i

        while current != -1:
            camino_actual.insert(0, current)
            current = self.enlaces[current]

        camino_nombres = []

        for i in camino_actual:
            camino_nombres.append(keys[i])

        return camino_nombres

    '''
        Recibe información de las tablas de enrutamiento y las actualiza. 
            - Si las tablas ya están llenas, con Dijkstra calcula las distancias más cortas.
    '''
    async def bellman_ford(self):
        print("\n----------- BELLMAN-FORD -----------")
        print(f"TABLA ACTUAL: {self.tabla}")

        # Initialize distances and predecessor
        distances = [float('inf') for _ in range(len(self.tabla))]
        predecessor = [-1 for _ in range(len(self.tabla))]
        distances[self.graph] = 0

        for _ in range(len(self.tabla) - 1):
            for u in range(len(self.tabla)):
                for v in range(len(self.tabla)):
                    if self.tabla[u][v] > 0 and distances[u] + self.tabla[u][v] < distances[v]:
                        distances[v] = distances[u] + self.tabla[u][v]
                        predecessor[v] = u

        # Check for negative-weight cycles
        for u in range(len(self.tabla)):
            for v in range(len(self.tabla)):
                if self.tabla[u][v] > 0 and distances[u] + self.tabla[u][v] < distances[v]:
                    print("Negative-weight cycle detected. Bellman-Ford cannot proceed.")
                    sys.exit(1)

        self.enlaces = predecessor
        self.costo_enlaces = distances

        print(f"COSTO ENLACES: {self.costo_enlaces}")
        print("------------------------------------")

# ------------ MENUS y HERRAMIENTAS ------------
    async def convert_to_dict(self, paquete):
        try:
            input_str = paquete.replace("'", '"')
            data = json.loads(input_str)
            return data
        except json.JSONDecodeError as err:
            print(err)
            return None

    async def are_nested_arrays_equal(self, arr1, arr2):
        if len(arr1) != len(arr2):
            return False
        
        for i in range(len(arr1)):
            if isinstance(arr1[i], list) and isinstance(arr2[i], list):
                if not await self.are_nested_arrays_equal(arr1[i], arr2[i]):
                    return False
            else:
                if arr1[i] != arr2[i]:
                    return False
        
        return True

def select_node():
    with open('names.txt', 'r') as file:
        data = file.read().replace('\n', '').replace("'", '"')
    data = json.loads(data)
    data = data["config"]

    while True:
        print("\n---DISTANCE VECTOR---\nSeleccione un nodo de la lista: ")
        keys = list(value for key, value in data.items())
        for i, key in enumerate(keys):
            print(f"{i+1}. {key}")

        try:
            node = int(input("Ingrese el número del nodo: "))
            if node > 0 and node <= len(data):
                return keys[node-1]
            else:
                print("Ingrese un número válido")

        except ValueError:
            print("Ingrese un número válido")


# Para evitar el error de que el evento no se puede ejecutar en Windows
#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  #COMENTAR PARA MAC

usuario = select_node()
server = Server(usuario, "123")            # Crear instancia del servidor con usuario y contraseña
server.connect(disable_starttls=True)      # Conexión al servidor
server.process(forever=False)              # Programa corre hasta que se cierra la conexión
