import plexapi
import plexapi.audio
from dotenv import dotenv_values
from plexapi import *
from plexapi.server import PlexServer


def login():
    from plexapi.myplex import MyPlexAccount
    while True:
        username = password = None
        while not username:
            username = input("Enter plex username: ")
        while not password:
            password = input("Enter plex password: ")
        try:
            account = MyPlexAccount(username, password)
            break
        except plexapi.exceptions.Unauthorized:
            print("Error: Unauthorized.")
    
    while True:
        servername = None
        while not servername:
            servername = input("Input plex server name: ")
        try:
            plex = account.resource(servername).connect()
            break
        except plexapi.exceptions.NotFound:
            print(f"Error: cannot find server with friendly name '{servername}'")

    with open(".env", "a+") as env_file:
        env_file.write(f"plexAddress={plex._baseurl}\n")
        env_file.write(f"authTokenId={plex._token}\n")


def track_artist(track: plexapi.playlist.Playable): #TODO: replace type with Track
    #if track.originalTitle:
    #    artist = track.originalTitle # artist
    #else:
    #    artist = track.artist().title # album artist
    return track.originalTitle or track.artist().title

# "Singleton" module init
try:
    env = dotenv_values(".env")
    plex = PlexServer(env["plexAddress"], env["authTokenId"])
except KeyError:
    login()
