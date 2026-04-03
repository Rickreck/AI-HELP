from spotify.services import search, get_top_tracks


def musica(nome):
    data = search(nome, "track")

    if not data["tracks"]["items"]:
        return "Música não encontrada."

    track = data["tracks"]["items"][0]

    return f"""
🎵 {track['name']}
👤 {track['artists'][0]['name']}
💿 {track['album']['name']}
🔥 Popularidade: {track['popularity']}
🔗 {track['external_urls']['spotify']}
"""


def album(nome):
    data = search(nome, "album")
    album = data["albums"]["items"][0]

    return f"""
💿 {album['name']}
👤 {album['artists'][0]['name']}
📅 Lançamento: {album['release_date']}
🎵 Total de faixas: {album['total_tracks']}
🔗 {album['external_urls']['spotify']}
"""


def artista(nome):
    data = search(nome, "artist")
    artist = data["artists"]["items"][0]

    top_tracks_data = get_top_tracks(artist["id"])
    top_tracks = top_tracks_data.get("tracks", [])[:5]

    top_tracks_text = "\n".join(
        [f"{i + 1}. {track['name']}" for i, track in enumerate(top_tracks)]
    )

    return f"""
🎤 {artist['name']}
🔥 Popularidade: {artist['popularity']}
👥 Seguidores: {artist['followers']['total']}
🎼 Gêneros: {', '.join(artist['genres'])}
## 🏆 Top Tracks:
{top_tracks_text}
🔗 {artist['external_urls']['spotify']}
"""
