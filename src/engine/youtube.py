import functools
import os
import pickle
from urllib.parse import parse_qs, urlparse

import pytube
from dotenv import dotenv_values, set_key
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from util.sorting import compute_sorting_ops


SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"
youtube_token_filename = "youtube_token.pkl"

youtube = None


def login():
    env = dotenv_values(".env")

    global creds
    creds = None
    if os.path.exists(youtube_token_filename):
        with open(youtube_token_filename, "rb") as token:
            creds = pickle.load(token)

    if not creds or any([not cred.valid for cred in creds]):
        """
        if creds and all([cred.expired and cred.refresh_token for cred in creds]):
            for cred in creds:
                cred.refresh(Request())
        else:
            creds = []
            for filename in [file for file in os.listdir(os.getcwd()) if file.endswith('.json')]:
                flow = InstalledAppFlow.from_client_secrets_file(filename, scopes=SCOPES)
                creds.append(flow.run_local_server(port=0))
        """
        try:
            for cred in creds:
                cred.refresh(Request())
        except Exception:
            creds = []
            for filename in [file for file in os.listdir(os.getcwd()) if file.endswith('.json')]:
                flow = InstalledAppFlow.from_client_secrets_file(filename, scopes=SCOPES)
                creds.append(flow.run_local_server(port=0))


        with open(youtube_token_filename, "wb") as token_file:
            pickle.dump(creds, token_file)


    creds = iter(creds)

    return build(api_service_name, api_version, credentials=next(creds))

    

#TODO: when rotating tokens, rewrite pickle file with new order
def manage_api(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        global creds
        global youtube
        if not youtube:
            youtube = login()

        try:
            result = func(*args, **kwargs)
        except HttpError as e:
            if not e.code or e.code != 403:
                raise e
            print(e)
            print("\n\nRotating youtube API credentials\n\n")
            cred = next(creds)
            youtube = build(api_service_name, api_version, credentials=cred)
            result = func(*args, **kwargs)
        return result
    return wrapped



def oldlogin(): # Todo: add better verif to this
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    youtube_token_filename = "youtube_token.pkl"
    env = dotenv_values(".env")

    creds = None
    if os.path.exists(youtube_token_filename):
        with open(youtube_token_filename, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            client_id = creds.client_id
            client_secret = creds.client_secret
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

        set_key(dotenv_path=".env", key_to_set="youtube_client_id", value_to_set=client_id)
        set_key(dotenv_path=".env", key_to_set="youtube_client_secret", value_to_set=client_secret)

    return build(api_service_name, api_version, credentials=creds)


def find_user_playlist(name):
    playlists = youtube.playlists.list(mine=True)

    for playlist in playlists.items:
        if playlist.snippet.title.lower() == name.lower():
            return playlist


def create_playlist(playlist_name, playlist_items, playlist_description=None):
    existing_playlists = list_playlists()
    for playlist in existing_playlists:
        # if playlist exists:
        if playlist['snippet']['title'].lower() == playlist_name.lower():
            url = playlist_url(playlist["id"])

            #TODO: if description is specified and existing description doesnt match
            results = list_playlist_items(playlist)
            existing_items = results["items"]
            existing_ids = [i["snippet"]["resourceId"]["videoId"] for i in existing_items] # video id
            video_playlist_id_map = dict()
            for i in existing_items:
                video_playlist_id_map[i["snippet"]["resourceId"]["videoId"]] = i["id"]

            updated_ids, ops = compute_sorting_ops(existing_ids, playlist_items) # op instructions are zero indexed

            print("Updating playlist",end="")
            for op in ops:
                print(".",end="")
                match op[0]:
                    case "del":
                        remove_video_from_playlist(video_playlist_id_map[op[1]])
                    case "mov":
                        update_playlist_item_position(playlist["id"], video_playlist_id_map[op[1]], op[1], op[2]-1)
                    case "add":
                        add_video_to_playlist(playlist["id"], op[1], op[2]+1)


            break
    else: # playlist doesn't exist
        print("Creating playlist...",end="")
        response = create_empty_playlist(playlist_name, description=playlist_description)
        print("Done.")
        url = playlist_url(response["id"])

        print("Adding items to playlist",end="")
        for item_id in playlist_items:
            add_video_to_playlist(playlist_id=response['id'], video_id=item_id)
            print(".",end="")
        print("Done.")

    return url


@manage_api
def list_playlists():
    return youtube.playlists().list(part="snippet",mine=True).execute()['items']


@manage_api
def list_playlist_items(playlist):
    results = youtube.playlistItems().list(
        part="snippet,id",
        playlistId=playlist["id"],
        maxResults=50, #TODO: use pageToken to retrieve more than 50 items https://developers.google.com/youtube/v3/docs/playlistItems/list
    ).execute()
    return results


# 50 units
@manage_api
def create_empty_playlist(title, description=None):
    body = {
        "snippet": {
            "title": title,
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
    if description:
        body["snippet"]["description"] = description
    
    request = youtube.playlists().insert(
        part="snippet,status",
        body=body)
    
    return request.execute()


# 50 units
@manage_api
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

    request = youtube.playlistItems().insert(
        part="snippet",
        body=body)

    return request.execute()


# 50 units
@manage_api
def remove_video_from_playlist(playlist_item_id):
    request = youtube.playlistItems().delete(
        id=playlist_item_id
    )
    return request.execute()


#TODO: use item dictionary as argument
# 50 units
@manage_api
def update_playlist_item_position(playlist_id, playlist_item_id, video_id, position):
    request = youtube.playlistItems().update(
        part="snippet",
        body={
            "id": playlist_item_id, #item.id
            "snippet": {
                "playlistId": playlist_id, # item.snipped.playlistId
                "position": position,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id # item.snippet.resourceId.videoId
                }
            }
        }
    )

    response = request.execute()


def noapi_search(search):
    results = pytube.Search(search).results
    return results[0].video_id


# 100 units
@manage_api
def search(search, maxResults=1):
    results = youtube.search().list(
        part="snippet",
        q=search,
        maxResults=maxResults
    ).execute()
    return [i['id']['videoId'] for i in results['items']]


def playlist_url(playlist_id) -> str:
    return f"https://www.youtube.com/playlist?list={playlist_id}"

def video_url(video_id) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"

def video_id(video_url) -> str:
    url_data = urlparse(video_url)
    query = parse_qs(url_data.query)
    return query["v"][0]


# "Singleton" module init
youtube = login()
