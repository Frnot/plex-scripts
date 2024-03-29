import spotipy
from dotenv import dotenv_values, set_key
from spotipy.oauth2 import SpotifyOAuth


def login():
    
    scope = [
        "user-library-read",
        "playlist-modify-public",
        "playlist-modify-private",
    ]

    try:
        env = dotenv_values(".env")
        oauth = SpotifyOAuth(scope=scope, 
                             client_id=env["spotify_client_id"], 
                             client_secret=env["spotify_client_secret"], 
                             redirect_uri=env["spotify_redirect_uri"])
        return spotipy.Spotify(auth_manager=oauth)
    except KeyError:
        pass


    while True:
        client_id = client_secret = redirect_uri = None
        while not client_id:
            client_id = input("Enter spotify client_id: ")
        while not client_secret:
            client_secret = input("Enter spotify client_secret: ")
            
        redirect_uri_input = input("Enter spotify redirect_uri (or enter for default): ")
        redirect_uri = redirect_uri_input or "http://localhost:8080"
        
        try:
            oauth = SpotifyOAuth(scope=scope, 
                                client_id=client_id, 
                                client_secret=client_secret, 
                                redirect_uri=redirect_uri)
            spotify = spotipy.Spotify(auth_manager=oauth)
            spotify.current_user() # make an api call to check if token is valid
            break
        except spotipy.SpotifyOauthError:
            print("Error: Unauthorized.")

    set_key(dotenv_path=".env", key_to_set="spotify_client_id", value_to_set=client_id)
    set_key(dotenv_path=".env", key_to_set="spotify_client_secret", value_to_set=client_secret)
    set_key(dotenv_path=".env", key_to_set="spotify_redirect_uri", value_to_set=redirect_uri)

    return spotify



def find_user_playlist(playlist_title):
    """Finds playlist with <playlist_title> belonging to current user."""

    results = spotify.search(q=playlist_title,type="playlist",limit=50)["playlists"]["items"]
    
    username = spotify.current_user()["display_name"]
    for playlist in results:
        if playlist["name"].lower() != playlist_title.lower():
            continue
        if playlist["owner"]["type"] != "user":
            continue
        if playlist["owner"]["display_name"].lower() == username.lower():
            return playlist
    else:
        return None


def find_track(trackname, artist=None):
    """Finds a track on spotify matching the given parameters"""
    search = trackname
    if artist:
        search += " artist:" + artist

    result = spotify.search(q=search, type="track")["tracks"]["items"]

    if not result:
        return find_track(trackname)

    for track in result:
        if track["name"].lower() == trackname.lower():
            if artist:
                if any(a["name"].lower() == artist.lower() for a in track["artists"]):
                    return track
            else:
                return track
    else:
        return result[0] if result else None



# "Singleton" module init
spotify = login()
