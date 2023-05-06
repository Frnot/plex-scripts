import pyyoutube
from pyyoutube import Client, AccessToken
from dotenv import dotenv_values
import oauthlib

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
            youtube = Client(client_id=client_id, client_secret=client_secret)
            auth_url = youtube.get_authorize_url()
            print(f"Go to '{auth_url}' and give access to app\n")
            print("When you are redirected to localhost, copy complete URL.")
            auth_response = input("Enter the compelte url that you were redirected to: ")
            youtube.generate_access_token(authorization_response=auth_response)
            break
        except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
            print("Error: Unauthorized.")
            #client_id = client_secret = None  TODO: fix this mess

    with open(".env", "a+") as env_file:
        env_file.write(f"youtube_client_id=\"{client_id}\"\n")
        env_file.write(f"youtube_client_secret=\"{client_secret}\"\n")
        env_file.write(f"youtube_access_token=\"{youtube.access_token}\"\n")



# "Singleton" module init
try:
    env = dotenv_values(".env")
    youtube = Client(access_token=env["youtube_access_token"])
except KeyError:
    login()


print("")

playlists = youtube.playlists.list(mine=True)

for playlist in playlists.items:
    print(playlist.snippet.title)