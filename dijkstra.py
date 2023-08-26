import json

class Dijkstra():

    def convert_to_dict(self):
        try:
            input_str = input("Ingrese su tabla JSON: ")
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
        self.graph = self.select_node()
        self.main()

    def main(self):
        
        print(f"\nNodo seleccionado: {self.graph}")
        for key, value in self.topologia.items():
            if key == self.graph:
                print(f"Vecinos:")
                for key, value in value.items():
                    print(f"{key}: {value}")


        tabla = {}
        if self.graph != self.keys[0]:
            print("\n---Tabla Inicial (Type: Info)---")
            tabla = self.convert_to_dict()

        else:
            topologia = self.topologia[self.graph]
            # array de len(keys) por len(keys)
            array_topologia = [[[-1,"-"] for i in range(len(self.keys)-1)] for j in range(len(self.keys))]

            topologia = self.topologia[self.graph]
            for key, value in topologia.items():
                array_topologia[0][self.keys.index(key)-1] = [value, self.graph]

            string_array = str(array_topologia)
            
            tabla = {"type":"info", 
                     "headers": {"from": f"{self.graph}", "to": f"{self.graph}", "hop_count": 1},
                     "payload": string_array}

        tabla_updated = self.dijkstra(tabla)

        print("\nEl nodo ya conoce la ruta más corta a todos los nodos vecinos.")

        while True:
            mensaje = input("\n¿Desea enviar/recibir un mensaje? (y/n): ")
            if mensaje == "n":
                print("Saliendo...")
                break



    def dijkstra(self, info):
        origin = info["headers"]["from"]
        destino = info["headers"]["to"]

        tabla = json.loads(info["payload"].replace("'", '"'))
        tabla_actualizada = tabla[self.keys.index(self.graph)]

        visited = self.visited_already(tabla)

        if len(visited) == len(self.keys) - 1:
            self.next_visit = self.graph
            self.before_visit = origin


        if origin != destino:
            tabla_origen = tabla[self.keys.index(origin)]

            topologia = self.topologia[self.graph]
            for key, value in topologia.items():

                valor_original = tabla_origen[self.keys.index(key)-1][0]
                x = self.keys.index(self.graph) -1
                y = self.keys.index(key) - 1
            
                if key == self.keys[0]:
                    continue

                if valor_original > tabla_origen[x][0] + value and value != 0:
                    tabla[x+1][y] = [tabla_origen[x][0] + value, self.graph]
                else:
                    tabla[x+1][y] = tabla_origen[y]

            tabla_actualizada = tabla[self.keys.index(self.graph)-1]

        valores = []
        for llave, i in enumerate(tabla_actualizada):
            if i[0] <= 0:
                valores.append(999)
            elif i[1] in visited and self.keys[llave+1] in visited:
                valores.append(999)
            else:
                valores.append(i[0])

        minimo = min(valores)
        indice = valores.index(minimo) + 1

        string_array = str(tabla)
        tabla_final = {"type":"info", "headers": {"from": f"{self.graph}", "to": f"{self.keys[indice]}", "hop_count": 1},"payload": string_array}
        
        tabla_json = json.dumps(tabla_final)
        print(f"\nTabla actualizada:\n {tabla_json}")
        
        self.next_visit = self.keys[indice]
        self.before_visit = origin
        return tabla_final
    
    def visited_already(self, tabla):
        visited = []
        string_tabla = str(tabla)

        tabla = string_tabla.replace("'", '').replace('[', '').replace(']', '').replace('"', '')

        for i in tabla:
            if i.isalpha():
                visited.append(i)

        unique_visited = list(set(visited))

        return unique_visited

main = Dijkstra()