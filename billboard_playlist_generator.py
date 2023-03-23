"""Billboard top 40 pop playlist generator"""

# TODO: make sure tidal-dl retries on error

import aigpy
import billboard
import plexapi
import plexapi.audio
from dotenv import dotenv_values
from plexapi import *
from plexapi.server import PlexServer

from billboard_scraper import top_40_no_country, group_by_artist

env = dotenv_values(".env")
plex = PlexServer(env["plexAddress"], env["authTokenId"])

playlist_name = "testplaylist"
library : plexapi.audio.Audio = plex.library.section("Music")

top40_tracklist = top_40_no_country()

plex_top40_tracklist = []

for track, artist in top40_tracklist:
    try:
        plextrack = library.search(artist)[0].track(track)
    except IndexError:
        print(aigpy.cmd.red("Error") + " searching for artist " + artist)
    except plexapi.exceptions.NotFound:
        print(aigpy.cmd.red("Error") + f" searching for track {track} by {artist}")
    plex_top40_tracklist.append(plextrack)


try:
    playlist = plex.playlist(playlist_name)
    playlist.removeItems(playlist.items())
    playlist.addItems(plex_top40_tracklist)

except plexapi.exceptions.NotFound:
    playlist = plex.createPlaylist(title=playlist_name, section="Music",items=plex_top40_tracklist)

print()