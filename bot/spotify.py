import spotipy, os, requests
from spotipy import client
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# auth seems to be taken care of?
# cid = os.getenv("SPOTIFYCID")
# csecret = os.getenv("SPOTIFYSECRET")
# crduri = os.getenv("SPOTIFYRDURI")
sobbotID = os.getenv("SPOTIFYBOTID")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="playlist-modify-public"))

url = "https://api.spotify.com"

def createPlaylist(name, userID, description=None):
    if description == None:
        description = "Default description. Posted by Sobbot"
    sp.user_playlist_create(user=userID, name=name, public=True, description=description)
    #response = requests.get(url=f"{url}/v1/users/{userID}/playlists", data=data)

createPlaylist("Test Playlist", sobbotID)