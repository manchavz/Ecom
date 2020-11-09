import requests

"""
    Archivo que tiene como objetivo Encapsular el POST request
    al API externa de AdamsPay. Asi proveer una interfaz limpia
    en Views.py
"""
# Add @params: Nombre del Item(s), Monto Total, Slug:Ecom850, ID de la transaccion
def post_debt():
    url = "https://staging.adamspay.com/api/v1/debts"

    # apikey BEFORE COMMITTING to REPO, save it in an environment var
    headers = {
      'apikey': 'adams-dc27cfd1803141',
      'Content-Type': 'application/json'
    }

    payload = {
                "debt": {
                    "docId": "abc0001",
                    "amount": {
                        "currency": "PYG",
                        "value": "250000.0"
                    },
                    "label": "Pelota de Basketball",
                    "slug": "Ecom850",
                    "validPeriod": {
                        "start": "2020-11-08T18:38:03+00:00",
                        "end": "2020-11-09T06:38:03+00:00"
                    }
                }
              }

    response = requests.request("POST", url, headers=headers, data=payload)

    # Debug: Check the Body of the request in terminal/console
    print(response.text)

    return response

