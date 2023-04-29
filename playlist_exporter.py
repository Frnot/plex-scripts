import plexapi
import plexapi.playlist

import plex_engine


print(plex_engine.plex.getWebURL)

playlists: list[plexapi.playlist.Playlist] = plex_engine.plex.playlists()

for idx, p in enumerate(playlists):
    print(f"{idx+1}: {p.title}")

print("Select a playlist to export:")
while True:
    choice = input()
    try:
        playlist = playlists[int(choice)-1]
        break
    except (IndexError, ValueError):
        print(f"Error: please select a number between 1 and {len(playlists)}")

test = playlist.items()

#trackpaths = playlist.download(savepath="downloads", keep_original_name=True)

import plexapi.audio
#plexapi.audio.Track.download()

for track in playlist.items():
    track.download(savepath="downloads", keep_original_name=True, videoResolution="")

print(f"Downloaded playlist '{playlist.title}'")