#Universidad del Valle de Guatemala
#Laboratorio 3 de Redes
# Stefano Aragoni 20226, Priscilla Gonzalez 20689, Carol Arevalo 20461

import json

def convert_to_dict(input_str):
    try:
        data = json.loads(input_str)
        return data
    except json.JSONDecodeError:
        return None

input_str = """
{
    "type": "message|echo|info",
    "headers": {
        "from": "foo",
        "to": "bar",
        "hop_count": 3
    },
    "payload": "loremipsum{lo que sea aca}"
}
"""

result_dict = convert_to_dict(input_str)
if result_dict:
    print(result_dict)
else:
    print("Invalid input format")
