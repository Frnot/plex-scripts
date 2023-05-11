import os
import pickle

from dotenv import dotenv_values
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

youtube_token_filename = "youtube_token.pkl"

def login(): # Todo: add better verif to this
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    creds = None
    env = dotenv_values(".env")

    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists(youtube_token_filename):
        with open(youtube_token_filename, "rb") as token:
            creds = pickle.load(token)

    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            
            try:
                client_id=env["youtube_client_id"]
                client_secret=env["youtube_client_secret"]
            except KeyError:
                client_id = client_secret = None

            while not client_id:
                client_id = input("Enter youtube app client_id: ")
            while not client_secret:
                client_secret = input("Enter youtube app client_secret: ")
            

            client_config = {}
            client_config['installed'] = {}
            client_config['installed']['client_id'] = client_id
            client_config['installed']['client_secret'] = client_secret
            client_config['installed']['auth_uri'] = 'https://accounts.google.com/o/oauth2/auth'
            client_config['installed']['token_uri'] = 'https://oauth2.googleapis.com/token'

            flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open(youtube_token_filename, "wb") as token:
            pickle.dump(creds, token)

        with open(".env", "a+") as env_file: # TODO: update else add if not exist
            env_file.write(f"youtube_client_id={client_id}\n")
            env_file.write(f"youtube_client_secret={client_secret}\n")

    return build(api_service_name, api_version, credentials=creds)


def find_user_playlist(name):
    playlists = youtube.playlists.list(mine=True)

    for playlist in playlists.items:
        if playlist.snippet.title.lower() == name.lower():
            return playlist


def create_playlist(playlist_name, playlist_items):
    existing_playlists = youtube.playlists().list(part="snippet",mine=True).execute()['items']
    for playlist in existing_playlists:
        if playlist['snippet']['title'] == playlist_name:
            test = youtube.playlistItems()
            break
    else:
        pass # make new playlist
        data = {}
        data['title'] = playlist_name
        data['description'] = "test description"
        #youtube.playlists().insert(part="snippet", body=data)
    items = youtube.playlistItems().list(part="snippet,id",
                                       playlistId="PLrxL_Y8KUceoVSN8Sp_ZYWJu6mZIzJIU8",
                                       maxResults=50, #TODO: use pageToken to retrieve mroe than 50 items https://developers.google.com/youtube/v3/docs/playlistItems/list
                                       ).execute()
    
    request = youtube.playlistItems().update(
        part="snippet",
        body={
            "id": "UExyeExfWThLVWNlb1ZTTjhTcF9aWVdKdTZtWkl6SklVOC4wOTA3OTZBNzVEMTUzOTMy", #item.id
            "snippet": {
                "playlistId": "PLrxL_Y8KUceoVSN8Sp_ZYWJu6mZIzJIU8", # item.snipped.playlistId
                "position": 4,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": "2xWkATdMQms" # item.snippet.resourceId.videoId
                }
            }
        }
    )
    response = request.execute()

    print()


def add_video_to_playlist(playlist_id, video_id, position=None):
    body={
        "snippet": {
            "playlistId": playlist_id, 
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }
    if position:
        body["snippet"]["position"] = position

    request = youtube.playlistItem().insert(
        part="snippet",
        body=body)

    request.execute()


def playlist_url(playlist_id) -> str:
    return f"https://www.youtube.com/playlist?list={playlist_id}"

def video_url(video_id) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def search(search, maxResults=1):
    results = youtube.search().list(
        part="snippet",
        q=search,
        maxResults=maxResults
    ).execute()
    return [video_url(i['id']['videoId']) for i in results['items']]


# "Singleton" module init
youtube = login()

test = search(search="mo guns", maxResults=2)

create_playlist('AAAAAAAAAAAA', test)

print(test)