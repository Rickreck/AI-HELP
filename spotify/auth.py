import requests
import base64
import time

CLIENT_ID = "xxx"
CLIENT_SECRET = "yyy"

_token = None
_token_expire = 0


def get_token():
    global _token, _token_expire

    # Se o token ainda for válido, reutiliza
    if _token and time.time() < _token_expire:
        return _token

    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception(f"Erro Spotify: {response.status_code} - {response.text}")

    json_result = response.json()

    _token = json_result["access_token"]
    _token_expire = time.time() + json_result["expires_in"]

    return _token

