import pyyoutube
from pyyoutube import Client, AccessToken, Api
from dotenv import dotenv_values
import oauthlib
from pyyoutube.error import *

def login(): # Todo: add better verif to this
    try:
        client_id=env["youtube_client_id"]
        client_secret=env["youtube_client_secret"]
    except KeyError:
        client_id = client_secret = None

    while True:
        while not client_id:
            client_id = input("Enter youtube app client_id: ")
        while not client_secret:
            client_secret = input("Enter youtube app client_secret: ")

        try:
            youtube = Api(client_id=client_id, client_secret=client_secret)
            auth_url = youtube.get_authorization_url()
            print(f"Go to '{auth_url}' and give access to app\n")
            print("When you are redirected to localhost, copy complete URL.")
            auth_response = input("Enter the compelte url that you were redirected to: ")
            youtube.generate_access_token(authorization_response=auth_response)
            #youtube.channels.list(mine=True)
            break
        except (PyYouTubeException, oauthlib.oauth2.rfc6749.errors.InvalidGrantError):
            print("Error: Unauthorized.")
            #client_id = client_secret = None  TODO: fix this mess

    with open(".env", "a+") as env_file: # TODO: update else add if not exist
        env_file.write(f"youtube_client_id={client_id}\n")
        env_file.write(f"youtube_client_secret={client_secret}\n")
        env_file.write(f"youtube_access_token={youtube._access_token}\n")


def find_user_playlist(name) -> pyyoutube.Playlist:
    playlists = youtube.playlists.list(mine=True)

    for playlist in playlists.items:
        if playlist.snippet.title.lower() == name.lower():
            return playlist


def create_playlist(name, tracks):
    youtube.playlists.insert()
    pass
    return playlist_url(playlist)


def playlist_url(playlist: pyyoutube.Playlist) -> str:
    return f"https://www.youtube.com/playlist?list={playlist.id}"


def find_track(name, artist):
    pass


# "Singleton" module init
try:
    env = dotenv_values(".env")
    youtube = Api(access_token=env["youtube_access_token"])
    #youtube.channels.list(mine=True)
except (KeyError, PyYouTubeException):
    login() #Todo: does this init youtube variable?
