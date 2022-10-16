# Initialization
import spotipy
from mutagen.flac      import FLAC
from mutagen.mp3       import MP3
from mutagen.mp3       import EasyMP3 as Eas
from mutagen.oggvorbis import OggVorbis
import os
import Stagger

# Setup variable(s)
clientID    = "2531ad4b5e3c497ca0a9fce18d1280ab"
redirectURI = "http://127.0.0.1:8000/spotify/callback/"
cache = spotipy.CacheFileHandler(".cache_sp")
secret = spotipy.oauth2.SpotifyPKCE(clientID, redirectURI, cache_handler=cache, scope=["user-library-read"])

# Change cwd to the folder where this script is located
workDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(workDir)

# Check if folder `Audio` found - otherwise make one and exit
try:
    fileList = os.listdir(".//Audio")
except FileNotFoundError:
    os.mkdir(".//Audio")
    print("\nPut audio files the folder \"Audio\" to scan them\n")
    exit()

# Check each file in folder `Audio`
count, success, fail = 1, 0, 0
for filename in fileList:
    print("< ========================================\n")

    # Find track and type
    print(f"Item {count}\n--------------\nFile name: {filename}")
    file = Stagger.findTypeFunc(".//Audio//"+filename)

    # If file is supported
    if file != "UNSUPPORTED":
        # Assign variables in relation to file type
        if   type(file) == FLAC or type(file) == OggVorbis:
            tag = Stagger.tag.vorbis
        elif type(file) == Eas:
            tag = Stagger.tag.vorbis

        titleTag       = tag[0]
        albumTag       = tag[3]
        albumArtistTag = tag[6]

        # Build Query

        ## Check if title is already present - if not, ask for input
        try:
            trackTitleSearch  = file[titleTag][0]
            print(f"Track title: {trackTitleSearch}")
        except KeyError:
            trackTitleSearch = input("Track title not found - enter manually: ")

        ## Check if album name is already present - if not, ask for input
        try:
            trackAlbumSearch = file[albumTag][0]
            print(f"Album: {trackAlbumSearch}")
        except KeyError:
            trackAlbumSearch = input("Album name not found - enter manually: ")

        ## Check if album artist is already present - if not, ask for input
        try:
            trackArtistSearch = file[albumArtistTag][0]
            print(f"Album artist: {trackArtistSearch}")
        except KeyError:
            trackArtistSearch = input("Album artist not found - enter manually: ")

        # Retrieve and write data
        print("\n")
        try:
            x = 0
            while True:
                ## Accumulate data
                trackData = Stagger.trackMeta(trackTitleSearch+" "+trackArtistSearch,secret, x, tag)

                ## Verify data
                if (
                    trackTitleSearch  == trackData[titleTag][0] and
                    trackAlbumSearch  == trackData[albumTag][0] and
                    trackArtistSearch == trackData[albumArtistTag][0]
                ):
                    ### Output data to STDOUT and overwrite file's tags
                    indexCount = 0
                    for x, y in list(trackData.items()):
                        print(str(x) + ": " + str(y))
                        temp = y
                        Stagger.addTag(x, y, file)
                        indexCount += 1

                    ### Save data to file and exit while loop
                    file.save()
                    print(f"\nSaved file {filename}")
                    success += 1
                    break

                else: ### If current search item didn't match existing, report
                    print(f"Search item {str(x+1).zfill(2)} doesn't match")
                    x += 1
        except (IndexError, TypeError): ### If data was not found on Spotify, report
            print(f"\nMetadata for file {filename} not found on Spotify - maybe check its title, album and album artist tags?")
            fail += 1

    print("\n======================================== >\n\n\n")
    count += 1

# A small detail thing
def countPrint(count: int): return f'{count} files' if count != 1 else f'{count} file'

# Print summary
print(f"Summary:\n{countPrint(success)} updated, {countPrint(fail)} failed, {countPrint(count - (success + fail))} ignored")
