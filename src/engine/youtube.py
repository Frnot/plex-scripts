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
        if creds and all([cred.expired and cred.refresh_token for cred in creds]):
            for cred in creds:
                cred.refresh(Request())
        else:
            creds = []
            for filename in [file for file in os.listdir(os.getcwd()) if file.endswith('.json')]:
                flow = InstalledAppFlow.from_client_secrets_file(filename, scopes=SCOPES)
                creds.append(flow.run_local_server(port=0))

        with open(youtube_token_filename, "wb") as token_file:
            pickle.dump(creds, token_file)

    return build(api_service_name, api_version, credentials=creds[0])

    


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
            if e.code != 403:
                raise e
            print(e)
            cred = next(creds)
            youtube = build(api_service_name, api_version, credentials=cred)
            result = func(*args, **kwargs)
        return result
    return wrapped



def create_playlist(playlist_name, playlist_items, playlist_description=None):
    existing_playlists = list_playlists()
    for playlist in existing_playlists:
        # if playlist exists:
        if playlist['snippet']['title'].lower() == playlist_name.lower():
            print("Existing playlist found.")

            url = playlist_url(playlist["id"])

            #TODO: if description is specified and existing description doesnt match
            # update playlist description

            results = api_list_playlist_items(playlist)
            existing_items = results["items"]

            existing_ids = []
            existing_id_pairs = {}
            for i in existing_items:
                existing_ids.append(i["snippet"]["resourceId"]["videoId"])
                existing_id_pairs[i["snippet"]["resourceId"]["videoId"]] = i["id"] # video id -> playlist id

            print("Computing operations to update existing playlist",end="")
            ops = reconcile_playlists(existing_ids, playlist_items)
            print(" done.")

            print("Updating playlist",end="")
            for op in ops:
                print(".",end="")
                match op[0]:
                    case "del":
                        remove_video_from_playlist(existing_id_pairs[op[1]])
                    case "mov":
                        update_playlist_item_position(playlist["id"],
                                                      op[1],
                                                      existing_id_pairs[op[1]],
                                                      op[2])
                    case "add":
                        add_video_to_playlist(playlist["id"],
                                              op[1],
                                              op[2])
            print("Done.")
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



def reconcile_playlists(exisiting_id: list, input_id: list):
    """Returns a list of operations to perform on youtube
    playlist to synchronize it with the new playlist."""

    # TODO: may need to uniquify playlists, check for duplicates in video_id
    # TODO: add an assertion

    api_ops = []

    # delete tracks in youtube playlist that don't exist in new playlist
    for id in exisiting_id:
        if id not in input_id:
            api_ops.append(("del", id))
            exisiting_id.remove(id)

    # sort existing playlist to match order of new playlist
    # !this sort does not minimize api operations!
    vinput = [id for id in input_id if id in exisiting_id]

    idx = 1
    while idx < len(vinput):
        l = vinput[idx-1]
        p = vinput[idx]
        f = vinput[idx+1] if idx+1 < len(vinput) else None

        idxm1 = exisiting_id.index(l)
        idx0 = exisiting_id.index(p)
        idx1 = exisiting_id.index(f) if f else idx0+1

        if not idxm1 < idx0:
            api_ops.append(("mov", p, idxm1+1))
            exisiting_id.insert(idxm1+1, p)
            exisiting_id.remove(p)
        elif not idx0 < idx1 and idxm1 < idx1:
            api_ops.append(("mov", p, idxm1+1))
            exisiting_id.insert(idxm1+1, p)
            exisiting_id.pop(idx0+1)

        idx += 1

    # add missing tracks to correct index
    for idx,id in enumerate(input_id):
        if id not in exisiting_id:
            api_ops.append(("add", id, idx))
            exisiting_id.insert(idx, id)

    assert(exisiting_id == input_id)
    return api_ops


@manage_api
def find_user_playlist(name):
    playlists = youtube.playlists.list(mine=True)

    for playlist in playlists.items:
        if playlist.snippet.title.lower() == name.lower():
            return playlist
        

@manage_api
def list_playlists():
    return youtube.playlists().list(part="snippet",mine=True).execute()['items']


def list_playlist_items(playlist_url):
    """Lists videos in a youtube playlist without counting against the api quota.\n
    This method is much slower than the api method."""

    item_urls = pytube.Playlist(playlist_url).video_urls

    return item_urls

    video_titles = []
    for link in video_links:
        video_titles.append(pytube.YouTube(link).title)


@manage_api
def api_list_playlist_items(playlist):
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


# 50 units
@manage_api
def update_playlist_item_position(playlist_id, video_id, playlist_item_id, position):
    request = youtube.playlistItems().update(
        part="snippet",
        body={
            "id": playlist_item_id, #item.id
            "snippet": {
                "playlistId": playlist_id, # item.snipped.playlistId
                "position": position,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )

    response = request.execute()


def search(search):
    """Searches for youtube video without consuming quota"""
    results = pytube.Search(search).results
    return results[0].video_id


# 100 units
@manage_api
def api_search(search, maxResults=1):
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
