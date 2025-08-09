import os
from dotenv import load_dotenv
from requests import post, get
import base64
import json
from playsound import playsound

## Load .env files
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
#print(f"CLIENT ID: {SPOTIFY_CLIENT_ID}")
##

def duration_length(time_ms):
    seconds = time_ms / 1000
    minutes = int(seconds / 60)
    remaining_seconds = int(seconds % 60)
    
    time = f"{minutes}m {remaining_seconds}s"
    return time

def get_token():
    auth_str = SPOTIFY_CLIENT_ID + ":" + SPOTIFY_CLIENT_SECRET;
    auth_bytes = auth_str.encode("utf-8")
    auth_b64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_b64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data) # Will return JSON data
    #Convert to Python Dictionary
    json_result = json.loads(result.content)
    
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token} #Useful

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artists with this name...")
        return None
    
    return json_result[0]
# Returns: Artist ID
def get_artist_id(json_string):
    return json_string["id"]
    
def get_artist_name(json_string):
    return json_string["name"]

# Returns: json_result that can be filtered
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    
    json_result = json.loads(result.content)["tracks"]
    return json_result


def artist_top_10(token, artist_id):
    songs = get_songs_by_artist(token, artist_id)  
    
    # Print out the top 10 songs from the artist
    print(f"Top 10 songs: \n")
    for idx, song in enumerate(songs):
        print(f"{idx+1} {song['name']}")

def artist_albums(token, artist_id):
    # Searching for the all of the artist's albums
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    
    albums = json.loads(result.content)["items"]
    
    print("\nAlbums:")
    for idx, album in enumerate(albums):
        print(f"{idx+1}. {album['name']}")

def find_song(token, artist_id, artist_name):
    while 1:
        song_name = input(f"Give a valid song name from {artist_name}: ")

        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        query = f"?q=artist:{artist_name} track:{song_name}&type=track&limit=1"
        result = get(url + query, headers=headers)
        json_result = json.loads(result.content)["tracks"]["items"]

        if len(json_result) == 0:
            print("No tracks/songs with this name...")
        else:
            # Print out details of the song
            song = json_result
            print(f"Track Name: {song[0]['name']}")
            print(f"Track Length: {duration_length(song[0]['duration_ms'])}")
            print(f"Track Image: {song[0]['url']}")
            break

    

#Function: Name
def main():
    token = get_token() # Needs to be used
    
    # Ask the user for an artist via search
    # The search may not work, so catch that scenario
    while True:
        user_artist = input("Search for an artist: ")
        print('\n')
        # Obtain the user's artist
        
        if (not(search_for_artist(token, user_artist) == None)):
            break # Exit if the searched artist does not exist
    artist_name = get_artist_name(search_for_artist(token, user_artist))
    print(artist_name)
    artist_id = get_artist_id(search_for_artist(token, user_artist))
    # Prompt the user to either
    # 1: Get top 10 songs
    # 2: Search for Album (using name)
    # 3: Search for specific song 
    
    print(f"Now looking at {artist_name}'s discography...")
    print(f"1: Get {artist_name}'s 10 songs")
    print(f"2: Get {artist_name}'s albums")
    print(f"3: Search for {user_artist}'s specific song")
    choice = int(input("Choice: "))
    
    if choice == 1:
        artist_top_10(token, artist_id)
    elif choice == 2:
        artist_albums(token, artist_id)
    elif choice == 3:
        find_song(token, artist_id, artist_name)
        
    


# main call
main()
