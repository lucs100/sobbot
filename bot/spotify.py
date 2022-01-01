from discord import user
from discord.ext import commands
import spotipy, os, discord, dill, admin, io, requests, base64
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# auth seems to be taken care of?
# cid = os.getenv("SPOTIFYCID")
# csecret = os.getenv("SPOTIFYSECRET")
# crduri = os.getenv("SPOTIFYRDURI")
sobbotID = os.getenv("SPOTIFYBOTID")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth( #spotipy instance
    scope="playlist-modify-public ugc-image-upload")) 

guildPlaylists = {}

url = "https://api.spotify.com"

class NoGuildPlaylistError(commands.CommandError):
	pass

class Artist:
    def __init__(self, data):
        self.link = data["external_urls"]["spotify"]
        self.id = data["id"]
        self.name = data["name"]

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
        
    def getTruncatedName(self, maxLen=30):
        if len(self.name) <= maxLen:
            return self.name
        else:
            return self.name[0:30] + "..."

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
    
    def addSong(self, song, addedBy):
        class songAddObject:
            def __init__(self, songToAdd):
                if songToAdd == None:
                    self.ok = False
                    self.name = None
                    self.artist = None
                else:
                    self.ok = True
                    self.name = songToAdd.name
                    self.artist = songToAdd.artists[0].name
        
        if isinstance(song, str):
            song = getFirstSongResult(song, addedBy)
            if song == "empty":
                return "empty"
        response = songAddObject(song)
        if response.ok == False:
            return response
        song.addedBy = addedBy
        sp.playlist_add_items(self.id, [song.id])
        self.songs.append(song)
        updateGuildData()
        return response

    def setTitle(self, newTitle):
        try:
            sp.playlist_change_details(self.id, name=newTitle)
            self.name = newTitle
            updateGuildData()
            return True
        except:
            return False

    def setDescription(self, newDesc):
        try:
            sp.playlist_change_details(self.id, description=newDesc)
            updateGuildData()
            # GPH doesn't store description
            return True
        except:
            return False
    
    def delete(self, isConfirmed=False):
        if not isConfirmed:
            return False
        else:
            gphID = str(self.id)
            guildID = str(self.guildID)
            sp.user_playlist_unfollow(sobbotID, gphID)
            try:
                del guildPlaylists[guildID]["playlists"][0] # TODO - change if more gphs?
                updateGuildData()
                return True
            except KeyError:
                return False
    
    def setCover(self, imageAsB64):
        sp.playlist_upload_cover_image(self.id, imageAsB64)
        return True
    
    def songInPlaylist(self, song):
        if isinstance(song, str):
            song = getFirstSongResult(song)
        for search in self.songs:
            if song.id == search.id:
                return True
        return False
    
    def deleteSong(self, song, userRequesting, bypassAuth=False):
        if isinstance(song, str):
            song = getFirstSongResult(song)
        if not self.songInPlaylist(song):
            return "notin"
        if (str(userRequesting) == song.addedBy) or bypassAuth:
            removalList = []
            for s in range(len(self.songs)):
                if self.songs[s].id == song.id:
                    removalList.append(s)
            removalList.sort(reverse=True)
            for n in removalList:
                self.songs.pop(n)
            sp.playlist_remove_all_occurrences_of_items(self.id, [song.id])
            updateGuildData()
            return True
    
    def undoLastAdd(self, userRequesting, bypassAuth=False):
        try:
            targetSong = self.songs[len(self.songs)-1]
        except IndexError:
            return "empty"
        if (str(userRequesting) == targetSong.addedBy) or bypassAuth:
            return self.deleteSong(targetSong, userRequesting)
        else:
            return "perm" #?

with open('bot/resources/data/private/guildPlaylists.pkl', "rb") as f:
    try:
        guildPlaylists = dill.load(f)
    except:
        guildPlaylists = {}
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
    # TODO - update playlist based on data from spotipy api?
    try:
        if "playlists" in guildPlaylists[guildID]:
            return guildPlaylists[guildID]["playlists"][0]
    except:
        pass
    return None

def saveGuildPlaylist(gph):
    if not isinstance(gph, GuildPlaylistHeader):
        return False
    if gph.guildID not in guildPlaylists:
        guildPlaylists[gph.guildID] = {}
    if "playlists" in guildPlaylists[gph.guildID]:
        guildPlaylists[gph.guildID]["playlists"].append(gph)
    else:
        guildPlaylists[gph.guildID]["playlists"] = []
        guildPlaylists[gph.guildID]["playlists"].append(gph)
    updateGuildData()
    return True

def getFirstSongResult(query, addedBy=None):
    try:
        data = sp.search(query, type="track")["tracks"]["items"][0]
        return(Song(data, addedBy))
    except IndexError:
        return None
    except spotipy.exceptions.SpotifyException:
        return "empty"

async def createGuildPlaylistGuildSide(message):
    creatorID = str(message.author.id)
    guildName = message.guild.name
    guildID = str(message.guild.id)
    currentPlaylist = getGuildPlaylist(guildID)
    if currentPlaylist != None:
        await message.channel.send(f"**{guildName}** already has a playlist!")
        await message.channel.send(f"<{currentPlaylist.link}>")
        return currentPlaylist
    sentMessage = await message.channel.send("Working...")
    playlistName = f"{guildName}'s Server Playlist"
    playlisth = createPlaylist(playlistName, guildMode=True)
    if playlisth != None:
        gph = GuildPlaylistHeader(playlistName, playlisth, creatorID, guildID)
        if gph != None:
            saveGuildPlaylist(gph)
            await encodeAndSetCoverImage(message.guild.icon_url_as(format="jpeg"), gph, isAsset=True)
            await sentMessage.edit(content="Success!")
            await message.channel.send(f"<{gph.link}>")
            return True
    await sentMessage.edit(content="Failed.")
    return False

async def addToGuildPlaylistGuildSide(message, c):
    guildID = str(message.guild.id)
    senderID = str(message.author.id)
    gph = getGuildPlaylist(guildID)
    if gph != None:
        response = gph.addSong(c, senderID)
        if response == "empty":
            await message.channel.send(f"Add a query after that command to add it to the playlist!")
        elif response.ok:
            await message.channel.send(f"Successfully added *{response.name}* " +
            f"by **{response.artist}**!")
        else:
            await message.channel.send("That song doesn't seem to exist.")
    else:
        raise NoGuildPlaylistError

async def createGuildPlaylistOverview(guildID, members):

    def getMemberNick(memberID):
        def getMember(localMemberID):
            for member in members:
                if member.id == int(localMemberID):
                    return member
            return None

        member = getMember(memberID)
        if member == None:
            return "*Unknown*"
        if member.nick != None:
            return member.nick
        return member.name

    target = getGuildPlaylist(guildID)
    embed = discord.Embed()
    if target == None:
        embed.title = "No server playlist found."
        embed.description = f"Use `{admin.getGuildPrefix(guildID)}spcreate` to make one."
        return embed
    title = f"{target.name} - Overview"
    # description = ""
    tracks = ""
    artists = ""
    addUser = ""

    for song in target.songs:
        tracks += song.getTruncatedName() + "\n"
        artists += song.artists[0].name + "\n"
        user = getMemberNick(song.addedBy)
        addUser += f"{user}\n"
    
    if tracks == "":
        embed.description = "No tracks yet!"
    else:
        embed.add_field(name="Song", value=tracks, inline=True)
        embed.add_field(name="Artist", value=artists, inline=True)
        embed.add_field(name="Contributor", value=addUser, inline=True)

    embed.title = title
    songCount = len(target.songs)
    embed.set_footer(text=f"Playlist has {songCount} tracks.")
    embed.color = 0x1DB954
    # embed.description = description
    return embed

async def fetchGuildPlaylistOverviewGuildSide(message, members):
    guildID = str(message.guild.id)
    overviewEmbed = await createGuildPlaylistOverview(guildID, members)
    await message.channel.send(embed=overviewEmbed)
    return True

async def setGuildPlaylistTitleGuildSide(message, c):
    target = getGuildPlaylist(message.guild.id)
    if target == None:
        raise NoGuildPlaylistError
    else:
        ok = target.setTitle(c)
        return ok

async def setGuildPlaylistDescGuildSide(message, c):
    target = getGuildPlaylist(message.guild.id)
    if target == None:
        raise NoGuildPlaylistError
    else:
        ok = target.setDescription(c)
        return ok

async def encodeAndSetCoverImage(image, gph, isAsset=False):

    def downloadImage(imageURL):
        image = Image.open(requests.get(imageURL, stream=True).raw)
        return image

    def getMaxSize(image):
        try:
            h = image.height
            w = image.width
        except AttributeError:
            return None
        minSize = min([h, w])
        left = (w - minSize)/2
        top = (h - minSize)/2
        right = (w + minSize)/2
        bottom = (h + minSize)/2
        return (left, top, right, bottom)

    try:
        if not isAsset:
            imageToSet = downloadImage(image.url)
        else:
            imageToSet = downloadImage(image)
        cropParams = getMaxSize(image)
        if cropParams != None:
            imageToSet = imageToSet.crop(cropParams)
        imageToSet = imageToSet.resize((300, 300), Image.LANCZOS)
        arr = io.BytesIO()
        imageToSet.save(arr, format="JPEG", quality=95)
        arr.seek(0)
        finalImageData = arr.getvalue()
        finalImage = base64.b64encode(finalImageData)
        gph.setCover(finalImage)
        return True
    except:
        return False

async def undoAdditionGuildSide(message, gph):
    response = gph.undoLastAdd(message.author.id)
    return response

async def deleteSongGuildSide(message, gph, song):
    song = getFirstSongResult(song)
    response = gph.deleteSong(song, message.author.id)
    return response