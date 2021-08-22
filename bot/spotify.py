import spotipy, os, requests, discord
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

class PlaylistHeader:
    def __init__(self, data):
        self.id = data["id"]
        self.link = data["external_urls"]["spotify"]

class ServerPlaylistHeader:
    def __init__(self, name, playlistHeader, creatorID, guildID):
        self.name = name
        self.header = playlistHeader
        self.createdBy = str(creatorID)
        self.guildID = guildID

def createPlaylist(name, targetUserID=sobbotID, description=None, public=True, guildMode=False):
    if description == None:
        description = f"A playlist created by Sobbot."
        if guildMode:
            description = f"A guild playlist created by Sobbot."
    response = sp.user_playlist_create(user=targetUserID, name=name, public=public, description=description)
    try:
        rph = PlaylistHeader(response)
        return rph #success!
    except:
        return None #failed, somehow

def createServerPlaylist(message):
    creatorID = message.author.id
    guildName = message.guild.name
    guildID = message.guild.id
    playlistName = f"{guildName}'s Server Playlist"
    playlisth = createPlaylist(playlistName, guildMode=True)
    if playlisth != None:
        sp = ServerPlaylistHeader(playlistName, playlisth, creatorID, guildID)
        #update list of guild playlists!

