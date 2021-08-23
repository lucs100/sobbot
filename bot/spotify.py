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
    guildPlaylists = json.loads(f.read()) # unpacking data
    f.close()

url = "https://api.spotify.com"

class AlbumImage:
    def __init__(self, data):
        pass

class Artist:
    def __init__(self, data):
        pass

class Song:
    def __init__(self, data):
        self.name = data["name"]
        self.images = []
        for image in data["images"]:
            self.images.append(AlbumImage(image))
        self.artists = []
        for artist in data["artists"]:
            self.artists.append(Artist(artist))
        self.id = data["id"]
        self.popularity = data["popularity"]
        self.preview = data["preview_url"]

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
        self.id = playlistHeader.id
        self.link = playlistHeader.link
        self.createdBy = str(creatorID)
        self.guildID = guildID
    
    def addSong(self, song):
        if isinstance(song, Song):
            sp.playlist_add_items(self.header.id, song.id)

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

def getGuildPlaylist(guildID):
    try:
        if "playlists" in guildPlaylists[guildID]:
            return guildPlaylists[guildID]["playlists"][0]
    except:
        pass
    return None

def saveGuildPlaylist(gph):
    if not isinstance(gph, GuildPlaylistHeader):
        return False
    data = gph.__dict__
    if gph.guildID not in guildPlaylists.keys():
        guildPlaylists[gph.guildID] = {}
    if "playlists" in guildPlaylists[gph.guildID]:
        guildPlaylists[gph.guildID]["playlists"].append(data)
    else:
        guildPlaylists[gph.guildID]["playlists"] = []
        guildPlaylists[gph.guildID]["playlists"].append(data)
    updateGuildData()
    return True

def getFirstSongResult(query):
    data = sp.search(query, type="track")["tracks"]["items"][0]
    return(Song(data))

async def createGuildPlaylistGuildSide(message):
    creatorID = str(message.author.id)
    guildName = message.guild.name
    guildID = str(message.guild.id)
    currentPlaylist = getGuildPlaylist(guildID)
    if currentPlaylist != None:
        await message.channel.send(f"**{guildName}** already has a playlist!")
        return currentPlaylist
    playlistName = f"{guildName}'s Server Playlist"
    playlisth = createPlaylist(playlistName, guildMode=True)
    if playlisth != None:
        gph = GuildPlaylistHeader(playlistName, playlisth, creatorID, guildID)
        if gph != None:
            saveGuildPlaylist(gph)
            await message.channel.send("Success!")
            return True
    await message.channel.send("Failed.")
    return False
    