import plexapi
import plexapi.playlist

import engine.plex as plex_engine




def main():
    playlists: list[plexapi.playlist.Playlist] = plex_engine.plex.playlists()

    for idx, p in enumerate(playlists, start=1):
        print(f"{idx}: {p.title}")
    plex_playlist = tui_select(playlists, "playlist")

    playlist = {
        "title": plex_playlist.title,
        "description": plex_playlist.summary
    }
    playlist["items"] = [(track.title, track.originalTitle or track.artist().title) for track in plex_playlist.items()]

    print("First 10 playlist items:")
    for idx,(track,artist) in enumerate(playlist["items"][:10], start=1):
        track: plexapi.playlist.Playable
        print(f"{idx}: {track} - {artist}")

    print("\n")

    export_options = {
        "Local (download)":"test",
        "Spotify":"test",
        "Youtube":export_to_youtube,
    }

    for idx,option in enumerate(list(export_options.keys()), start=1):
        print(f"{idx}: {option}")
    location = tui_select(list(export_options.keys()), "export destination")

    export_options[location](playlist)




def download():
    pass
    #trackpaths = playlist.download(savepath="downloads", keep_original_name=True)

    #plexapi.audio.Track.download()


def export_to_youtube(playlist):
    import engine.youtube as youtube_engine
    youtube_tracks = []
    for title, artist in playlist["items"]:
        youtube_tracks.append(youtube_engine.search(f"{title} {artist}"))

    url = youtube_engine.create_playlist(playlist_name=playlist["title"], 
                                   playlist_items=youtube_tracks, 
                                   playlist_description=playlist["description"])

    print(f"Playlist '{playlist['title']}' successfully exported to youtube:\n{url}")




def export_to_spotify(playlist):
    import engine.spotify as spotify_engine
    if result := spotify_engine.find_user_playlist(playlist["title"]):
        print("Playlist already exists on spotify. Deleting")
        spotify_engine.spotify.current_user_unfollow_playlist(result["id"])

    spotify_playlist = spotify_engine.spotify.user_playlist_create(user=spotify_engine.spotify.current_user()["id"],
                                                                name=playlist["title"],
                                                                description=playlist["description"])

    errors = []
    spotify_tracks = []
    for title,artist in playlist["items"]:
        #track.download(savepath=r"C:\Users\Frnot\Downloads", keep_original_name=True)
        print(f"Plex track:    {title} - {artist}")
        spotify_track = spotify_engine.find_track(title, artist)
        if spotify_track:
            print(f"Spotify track: {spotify_track['name']} - {spotify_track['artists'][0]['name']}")
            spotify_tracks.append(spotify_track["uri"])
        else:
            print("Error: no Spotify track found")
            errors.append(f"{title} - {artist}")

    spotify_engine.spotify.playlist_add_items(spotify_playlist["id"], spotify_tracks)

    print("Errored tracks:")
    for track in errors:
        print(track)

    print(f"'{playlist.title}' exported to Spotify: https://open.spotify.com/playlist/{spotify_playlist['id']}")


def tui_select(options, option_type):
    while True:
        choice = input(f"Select index of {option_type}: ")
        try:
            return options[int(choice)-1]
        except (IndexError, ValueError):
            print(f"Error: please select a number between 1 and {len(options)}")


if __name__ == "__main__":
    main()