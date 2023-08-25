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
            array_topologia = [[-1 for i in range(len(self.keys))] for j in range(len(self.keys))]
            for key, value in topologia.items():
                x = self.keys.index(self.graph)
                y = self.keys.index(key)
                array_topologia[x][y] = value
                array_topologia[x][x] = 0

            string_array = str(array_topologia)
            
            tabla = {"type":"info", 
                     "headers": {"from": f"{self.graph}", "to": f"{self.graph}", "hop_count": 1},
                     "payload": string_array}
            
            print("\n---Tabla Inicial (Type: Topology)---")
            json_output = json.dumps(tabla)
            print(json_output)

        tabla_updated = self.dijkstra(tabla)

    def dijkstra(self, tabla):
        print("\n---Tabla Final---")

main = Dijkstra()