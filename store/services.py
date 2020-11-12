import os
import requests
import datetime
import sys
import fileinput
from dotenv import load_dotenv


# Encapsular el POST request al API externo de AdamsPay
def factura():
    temp_int = os.environ.get("facturaNum")
    # Typecast de string -> int
    numero_de_factura_int = int(temp_int)
    # Actualiza el nuevo numero de la factura
    numero_de_factura_int += 1
    # Typecast de int -> string
    numero_de_factura = str(numero_de_factura_int)
    # Actualiza el numero de la factura en el archivo correspondiente
    actualizar_factura(numero_de_factura)
    # Consolidar el nuevo nombre de la factura
    factura_completa = "Ecom" + numero_de_factura
    return factura_completa


# Actualizar numero de factura de manera dinamica
def actualizar_factura(numero_de_factura):
    # abrir archivo y autorizar poder sobre escribir en mismo
    for line in fileinput.input('store/.env', inplace=True):
        # Elimina la linea de texto que contenga 'facturaNum=', mas los espacios
        if line.strip().startswith('facturaNum='):
            # sobre escribe la variable 'line' con el texto deseado
            line = "facturaNum="+numero_de_factura+"\n"
        # escribe el contenido de 'line' en el archivo abierto
        sys.stdout.write(line)


def post_debt(item_name, costo_total):
    # Usar 'environment variables' por motivos de seguridad
    load_dotenv()
    apikey = os.environ.get("apikey")
    nueva_factura = factura()
    url = "https://staging.adamspay.com/api/v1/debts"
    headers = {
        'apikey': apikey,
        'Content-Type': 'application/json'
    }
    # Hora en UTC zona horaria
    inicio_validez = datetime.datetime.utcnow().replace()
    fin_validez = inicio_validez + datetime.timedelta(days=2)
    payload = {
        "debt": {
            'docId': nueva_factura,
            "amount": {
                "currency": "PYG",
                "value": costo_total
            },
            "label": item_name,
            "slug": nueva_factura,
            "validPeriod": {
                "start": inicio_validez.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": fin_validez.strftime("%Y-%m-%dT%H:%M:%S")
            }
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    r_json = r.json()
    return r_json

