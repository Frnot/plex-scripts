import plexapi
import plexapi.playlist

import plex_engine
import spotify_engine


playlists: list[plexapi.playlist.Playlist] = plex_engine.plex.playlists()

for idx, p in enumerate(playlists):
    print(f"{idx+1}: {p.title}")

print("Select number of playlist to export:")
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

errors = []
spotify_tracks = []
for track in playlist.items():
    #track.download(savepath=r"C:\Users\Frnot\Downloads", keep_original_name=True)
    if track.originalTitle:
        artist = track.originalTitle # artist
    else:
        artist = track.artist().title # album artist
    print(f"Plex track: {track.title} - {artist}")
    spotify_track = spotify_engine.find_track(track.title, artist)
    if spotify_track:
        print(f"Spotify track: {spotify_track['name']} - {spotify_track['artists'][0]['name']}")
        spotify_tracks.append(spotify_track["uri"])
    else:
        print("Error: no Spotify track found")
        errors.append(f"{track.title} - {artist}")

result = spotify_engine.find_user_playlist(playlist.title)

if not result:
    spotify_playlist = spotify_engine.spotify.user_playlist_create(user=spotify_engine.spotify.current_user()["id"],
                                                                   name=playlist.title,
                                                                   description=playlist.summary)
else:
    print("Playlist already exists on spotify")

spotify_engine.spotify.playlist_add_items(spotify_playlist["id"], spotify_tracks)