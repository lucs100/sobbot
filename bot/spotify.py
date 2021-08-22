import spotipy, os, requests, discord, json
from spotipy import client
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# auth seems to be taken care of?
# cid = os.getenv("SPOTIFYCID")
# csecret = os.getenv("SPOTIFYSECRET")
# crduri = os.getenv("SPOTIFYRDURI")
sobbotID = os.getenv("SPOTIFYBOTID")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth( #spotipy instance
    scope="playlist-modify-public")) 

guildPlaylists = dict()

with open('bot/resources/data/private/guilds.json') as f:
    guilds = json.loads(f.read()) # unpacking data
    f.close()

url = "https://api.spotify.com"

class PlaylistHeader:
    def __init__(self, data):
        if isinstance(data, dict):
            self.id = data["id"]
            self.link = data["external_urls"]["spotify"]
        if isinstance(data, PlaylistHeader):
            self.id = data.id
            self.link = data.link

class GuildPlaylistHeader:
    def __init__(self, name, playlistHeader, creatorID, guildID):
        self.name = name
        self.header = PlaylistHeader(playlistHeader)
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

def updateGuildData():
    with open('bot/resources/data/private/guildPlaylists.json', 'w') as fp:
        json.dump(guildPlaylists, fp, indent=4)
    return True

def saveGuildPlaylist(gph):
    if not isinstance(gph, GuildPlaylistHeader):
        return False
    if gph.guildID in guilds:
        if "playlists" in guilds[gph.guildID]:
            numPlaylists = len(guilds[gph.guildID]["playlists"])
            guilds[gph.guildID]["playlists"][numPlaylists] = gph
        else:
            guilds[gph.guildID]["playlists"] = {0: gph}
    updateGuildData()
    return True

def createGuildPlaylist(message):
    creatorID = str(message.author.id)
    guildName = message.guild.name
    guildID = str(message.guild.id)
    playlistName = f"{guildName}'s Server Playlist"
    playlisth = createPlaylist(playlistName, guildMode=True)
    if playlisth != None:
        sp = GuildPlaylistHeader(playlistName, playlisth, creatorID, guildID)
        saveGuildPlaylist(sp)

