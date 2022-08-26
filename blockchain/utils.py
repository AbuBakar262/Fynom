import requests
import json


def get_eth_price(amount):
    try:
        url = "https://api.latoken.com/v2/ticker/ETH/USDT"
        payload = {}
        headers = {
            'Cookie': '__ludevid=MzE1OGFkNzItNWZlMy00NjViLThlNTYtYTAyMWI4MzhlMjI1'
        }
        usdt_response = requests.request("GET", url, headers=headers, data=payload)
        data = json.loads(usdt_response.text)
        usdt = float(data.get('lastPrice'))
        eth_dollars = amount * usdt
        return eth_dollars
    except Exception as e:
        return False


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


