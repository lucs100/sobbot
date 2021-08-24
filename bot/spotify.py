import spotipy, os, discord, json, dill
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

guildPlaylists = {}

url = "https://api.spotify.com"

class Artist:
    def __init__(self, data):
        self = None
        pass

class Album:
    def __init__(self, data):
        self.artists = []
        for artist in data["artists"]:
            self.artists.append(Artist(artist))
        self.id = data["id"]
        self.image = data["images"][0]["url"]
        self.name = data["name"]

class Song:
    def __init__(self, data, addedBy=None):
        self.name = data["name"]
        self.images = []
        self.album = Album(data["album"])
        self.artists = []
        for artist in data["artists"]:
            self.artists.append(Artist(artist))
        self.id = data["id"]
        self.popularity = data["popularity"]
        self.preview = data["preview_url"]
        self.addedBy = addedBy

class PlaylistHeader:
    def __init__(self, data):
        if isinstance(data, dict):
            self.id = data["id"]
            self.link = data["external_urls"]["spotify"]
        if isinstance(data, PlaylistHeader):
            self.id = data.id
            self.link = data.link

class GuildPlaylistHeader:
    def __init__(self, name, playlistHeader, creatorID, guildID, songs=[]):
        if isinstance(playlistHeader, dict):
            headerID = playlistHeader["id"]
            headerLink = playlistHeader["link"]
        else:
            headerID = playlistHeader.id
            headerLink = playlistHeader.link
        self.name = name
        self.id = headerID # can't nest PlaylistHeader bc of conversion to dict
        self.link = headerLink # mayve inherit this later?
        self.createdBy = str(creatorID)
        self.guildID = guildID
        self.songs = songs

with open('bot/resources/data/private/guildPlaylists.pkl', "rb") as f:
    try:
        guildPlaylists = dill.load(f)
    except EOFError:
        guildPlaylists = []
    f.close()

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
    with open('bot/resources/data/private/guildPlaylists.pkl', 'wb') as f:
        dill.dump(guildPlaylists, f, recurse=True)
    return True

def getGuildPlaylist(guildID):
    guildID = str(guildID)
    try:
        if "playlists" in guildPlaylists[guildID]:
            return guildPlaylists[guildID]["playlists"][0]
    except:
        pass
    return None

def saveGuildPlaylist(gph):
    if not isinstance(gph, GuildPlaylistHeader):
        return False
    if gph.guildID not in guildPlaylists.keys():
        guildPlaylists[gph.guildID] = {}
    if "playlists" in guildPlaylists[gph.guildID]:
        guildPlaylists[gph.guildID]["playlists"].append(gph)
    else:
        guildPlaylists[gph.guildID]["playlists"] = []
        guildPlaylists[gph.guildID]["playlists"].append(gph)
    updateGuildData()
    return True

def addSong(playlist, song, addedBy):
    if isinstance(song, str):
        song = getFirstSongResult(song, addedBy)
    if song == None:
        return False
    song.addedBy = addedBy
    sp.playlist_add_items(playlist["id"], song.id)
    playlist["songs"].append(song)
    updateGuildData()
    return True

def getFirstSongResult(query, addedBy):
    try:
        data = sp.search(query, type="track")["tracks"]["items"][0]
        return(Song(data, addedBy))
    except IndexError:
        return None

async def createGuildPlaylistGuildSide(message):
    creatorID = str(message.author.id)
    guildName = message.guild.name
    guildID = str(message.guild.id)
    currentPlaylist = getGuildPlaylist(guildID)
    if currentPlaylist != None:
        await message.channel.send(f"**{guildName}** already has a playlist!")
        await message.channel.send(f"<{currentPlaylist.link}>")
        return currentPlaylist
    playlistName = f"{guildName}'s Server Playlist"
    playlisth = createPlaylist(playlistName, guildMode=True)
    if playlisth != None:
        gph = GuildPlaylistHeader(playlistName, playlisth, creatorID, guildID)
        if gph != None:
            saveGuildPlaylist(gph)
            await message.channel.send("Success!")
            await message.channel.send(f"<{gph.link}>")
            return True
    await message.channel.send("Failed.")
    return False