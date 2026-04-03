import requests
from spotify.auth import get_token


BASE_URL = "https://api.spotify.com/v1"


def search(query, search_type):
    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": query,
        "type": search_type,
        "limit": 1
    }

    response = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
    return response.json()

def get_top_tracks(artist_id, country="BR"):
    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "market": country
    }

    response = requests.get(
        f"{BASE_URL}/artists/{artist_id}/top-tracks",
        headers=headers,
        params=params
    )

    return response.json()