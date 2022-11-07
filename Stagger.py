"""This moduler contains all methods and data for Stagger. Feel free to reuse it :3"""

# Initialization
import spotipy
import mutagen
from mutagen.flac      import FLAC
from mutagen.mp3       import MP3
from mutagen.mp3       import EasyMP3 as EMP3
from mutagen.oggvorbis import OggVorbis
import sys

# Map extra EasyID3 tags
for x in [
        ("year"        ,  "TDRC"),
        ("track"       ,  "TRCK"),
        ("initialkey"  ,  "TKEY"),
        ("origdate"    ,  "TDOR")
]:
    EMP3.ID3.RegisterTextKey(x[0], x[1])

for x in [
        "spotifyTrackID",
        "spotifyAlbumID",
        "itunesadvisory",
        "tracktotal",
        "disctotal"
]:
    EMP3.ID3.RegisterTXXXKey(x, x)

# For reference
"""
Predefined text mappings in EasyID3 / EMP3
    "album"                       :   "TALB"
    "bpm"                         :   "TBPM"
    "title"                       :   "TIT2"
    "artist"                      :   "TPE1"
    "albumartist"                 :   "TPE2"
    "discnumber"                  :   "TPOS"
    "tracknumber"                 :   "TRCK"
    "isrc"                        :   "TSRC"
    "barcode"                     :   "TXXX:BARCODE"

Predefined function mappings in EasyID3 / EMP3
    "Genre"                       : genre_*
    "Date"                        : date_*
"""

# Define class containing tag list
class tag:
    """Data values (list): `vorbis`, `id3`"""

    vorbis = [
        "title",
        "track",
        "tracktotal",
        "album",
        "year",
        "origdate",
        "albumartist",
        "discnumber",
        "disctotal",
        "bpm",
        "isrc",
        "barcode",
        "spotifyTrackID",
        "spotifyAlbumID",
        "artist",
        "musicbrainz_albumtype",
        "initialkey",
        "itunesadvisory"
    ]

    id3 = [
        "TIT2",
        "TRCK",
        "TRCK",
        "TALB",
        "TDRC",
        "TDAT",
        "TPE2",
        "TPOS",
        "TXXX:TOTALDISCS",
        "TBPM",
        "TSRC",
        "TXXX:BARCODE",
        "TXXX:SPOTIFYTRACKID",
        "TXXX:SPOTIFYALBUMID",
        "TPE1",
        "TXXX:MusicBrainz Album Type",
        "TKEY"
    ]

# Find metadata in Spotify
def trackMeta(query: str, auth_mgr: spotipy.SpotifyOAuth, index: int = 0, nameList: list = None) -> dict:
    """## Find metadata of `{query}` from spotify

    ### Args:
    - query (str): String to search on Spotify
    - auth_mgr (spotipy.SpotifyOAuth): Spotipy OAuthManager object
    - index (int, optional): Check search item `{index}`. Defaults to 0.
    - nameList (list):  Contains a list of tag names orgainzed in a specific order.
                        See `idList` in this function to see format.
                        Defaults to a set meant for vorbis tags (inside function).

    ### Returns:
    - dict: Contains search result of `{query}`
    """

    # Initialize
    spotify = spotipy.Spotify(auth_manager=auth_mgr)
    idList  = tag.vorbis if nameList == None else nameList

    # Build query
    try:
        result            = spotify.search(q=query,type="track")
    except KeyboardInterrupt:
        print("\Operation terminated by user")
        print("\n======================================== >")
        sys.exit()
    except:
        print("Network error - try again when you have a working internet connection")
        print("\n======================================== >")
        sys.exit()
    resultTrack       = spotify.track(track_id=result["tracks"]["items"][index]["id"])
    resultAlbum       = spotify.album(album_id=resultTrack["album"]["id"])
    resultFeatures    = spotify.audio_features(resultTrack["id"])[0]

    # Build dict
    trackMeta = {}
    def trackAdd(key: str ,data: list): trackMeta.update({key : data})


    # Add simple ones
    trackAdd(idList[0] ,[resultTrack["name"]])
    trackAdd(idList[1] ,[str(resultTrack["track_number"])])
    trackAdd(idList[2] ,[str(resultTrack["album"]["total_tracks"])])
    trackAdd(idList[3] ,[resultTrack["album"]["name"]])
    trackAdd(idList[4] ,[resultAlbum["release_date"][0:4]])
    trackAdd(idList[5] ,[resultAlbum["release_date"]])
    trackAdd(idList[6] ,[resultTrack["album"]["artists"][0]["name"]])
    trackAdd(idList[7] ,[str(resultTrack["disc_number"])])
    trackAdd(idList[8] ,[str(resultAlbum["tracks"]["items"][-1]["disc_number"])])
    trackAdd(idList[9] ,[str(round(resultFeatures["tempo"]))])
    trackAdd(idList[10],[resultTrack["external_ids"]["isrc"]])
    trackAdd(idList[11],[resultAlbum["external_ids"]["upc"]])
    trackAdd(idList[12],[resultTrack["id"]])
    trackAdd(idList[13],[resultTrack["album"]["id"]])

    # Do some manupilation to add a bit more complicated ones

    ## Artist
    artist  = [str(resultTrack["artists"][0]["name"])]
    length = len(resultTrack["artists"])
    if length > 1:
        for x in range(1, length):
            artist = artist + [resultTrack["artists"][x]["name"]]
    trackAdd(idList[14],artist)

    ## Release type
    trackType = str(resultTrack["album"]["album_type"])
    if trackType == "single":
        trackType = ["Single or EP"]
    else:
        trackType = [trackType.capitalize()]
    trackAdd(idList[15],trackType)

    ## Key

    ### Map numbers to classical key
    keyMap = {
        "-1" : "",
        "0"  : "C",
        "1"  : "Db",
        "2"  : "D",
        "3"  : "Eb",
        "4"  : "E",
        "5"  : "F",
        "6"  : "Gb",
        "7"  : "G",
        "8"  : "Gb",
        "9"  : "A",
        "10" : "Ab",
        "11" : "B"
    }

    ### Account for musical mode (Minor or Major)
    modeMap = ["m",""]

    ### Find classical key
    key = str(resultFeatures["key"])
    trackKey = keyMap[key]+modeMap[resultFeatures["mode"]]

    ### Map classical key to camelot
    camelotMap = {
        "C"   : "8B",
        "Db"  : "3B",
        "D"   : "10B",
        "Eb"  : "5B",
        "E"   : "12B",
        "F"   : "7B",
        "Gb"  : "2B",
        "G"  : "9B",
        "Ab"  : "4B",
        "A"   : "11B",
        "Bb"  : "6B",
        "B"  : "1B",
        "Cm"  : "5A",
        "Dbm" : "12A",
        "Dm"  : "7A",
        "Ebm" : "2A",
        "Em"  : "9A",
        "Fm"  : "4A",
        "Gbm" : "11A",
        "Gm"  : "6A",
        "Abm" : "1A",
        "Am"  : "8A",
        "Bbm" : "3A",
        "Bm"  : "10A"
    }

    # Append to dictionary
    trackAdd(idList[16],[str(trackKey)]+[str(camelotMap[trackKey])])

    ## Explicitness
    if resultTrack["explicit"]:
        trackAdd(idList[17] ,['1'])
    elif not resultTrack["explicit"]:
        trackAdd(idList[17] ,['0'])


    # Return Dictionary
    return trackMeta


# Remove existing tags
def initTags(trackData: dict, nameList: list = None) -> None:
    """## Clears all tags (as provided in `{nameList}`) from file

    ### Args:
    - trackData (dict): Contains the data of the file 
    - nameList (list): Contains a list of tags to clear. Defaults to `None`, which loads `tag.vorbis`
    """
    idList  = tag.vorbis if nameList == None else nameList
    for tagName in idList:
        try:
            del trackData[tagName]
        except KeyError:
            pass

# Check audio encoding type and return it
def findTypeFunc(audioFileName: str):
    """## Returns function for filetype or literal "UNSUPPORTED" if filetype not defined

    ### Args:
    - audioFileName (str): Name of the file we need to check

    ### Returns (One Of):
    - function:      Returns function compatible with given file name
    - "UNSUPPORTED": Returns this literal only if no compatible function for `{audioFileName}` was found
    """

    try:
        try:
            filetype = type(mutagen.File(audioFileName))
        except:
            raise UnboundLocalError
        if filetype == FLAC:
            fileFunc = FLAC(audioFileName)
            print("Type: FLAC")
        elif filetype == OggVorbis:
            fileFunc = OggVorbis(audioFileName)
            print("Type: OGG Vorbis")
        elif filetype == MP3:
            fileFunc = EMP3(audioFileName)
            print("Type: MP3")
        if fileFunc != None:
            return fileFunc
        else:
            return "UNSUPPORTED"
    except UnboundLocalError:
        print("Type: Undefined / Non-audio")
        return "UNSUPPORTED"

# Define a function to make it simpler to add tags
def addTag(tagName : str, tagData : list, file: FLAC | OggVorbis | EMP3):
    try:
        file[tagName] = ""
    except KeyError:
        pass
    if   type(file) == FLAC or type(file) == OggVorbis:
        file.pop(tagName)
        file.update({tagName: tagData})
    elif type(file) == EMP3:
        if   tagName == "track":
            tagName = "tracknumber"
            file[tagName] = tagData
        elif tagName == "track":
            tagName = "tracknumber"
            file[tagName] = tagData
        else:
            file[tagName] = tagData

