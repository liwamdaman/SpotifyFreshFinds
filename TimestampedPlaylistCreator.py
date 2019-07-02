import spotipy
import spotipy.util as util
from datetime import datetime
from datetime import timedelta
from Artists import MyArtists
from Artists import ArtistAnalytics

#scope = 'user-library-read'
scope = 'playlist-modify-public user-top-read'
username = "liwam"
myUserID = "liwam"

# Constant variables
count = 1
pageLengthNR = 50 # Maximum 50
totaldepthNR = 200
dateFormat = "%Y-%m-%d" # Note that playlists are formatted as "startdate - enddate"
dateFormatLength = len("1999-11-01")
playlistTimeRange = 1 # Weeks


def main():
    token = util.prompt_for_user_token(username, scope, 'eebf955e61eb4018937a714ae38ed5fc', '64cd58041e2d42f4bb2802d5e6535507', 'http://localhost/')
    if token:
        sp = spotipy.Spotify(auth=token)
        myUserID = sp.me()['id']
        #print(myUserID)
        albumIDs = []

        # Create instance of MyArtists class and populate
        myArtists = MyArtists(sp)
        myArtists.AddTopArtistsLongTerm()
        myArtists.AddTopArtistsShortTerm()
        print(str(len(myArtists.artists)) + ' artists selected: ')
        print(myArtists.artists)

        # Parse New Releases, add to list based on artist
        for page in range(0,int(totaldepthNR/pageLengthNR)):
            results = sp.new_releases(country='CA', limit=pageLengthNR, offset=page*pageLengthNR)
            for album in results['albums']['items']:
                #print(album['name'] + '-' +album['artists'][0]['name'])
                for albumArtist in album['artists']:
                    # Include album even if the artist isn't the first listed
                    if albumArtist['name'] in myArtists.artists:
                        albumIDs.append(album['id'])
                        print('New Releases: ' + album['name'] + '-' + album['artists'][0]['name'])

        # Order the albums by release date to avoid logic errors for GetCorrespondingTimestampedPlaylist
        # Do this by zipping the list of album IDs with the list of release dates into a list of tuples, then sorting the list of tuples by release date
        releaseDates = []
        for albumID in albumIDs:
            releaseDates.append(datetime.strptime(sp.album(albumID)['release_date'], dateFormat))
        albumsWithDates = list(zip(albumIDs, releaseDates))
        albumsWithDates.sort(key=lambda tup: tup[1])

        # Add the New Releases songs to playlist
        for albumsWithDate in albumsWithDates:
            AddAlbumTracksToTimestampedPlaylist(sp, albumsWithDate[0], albumsWithDate[1])

        # Graph Analytics
        artistAnalytics = ArtistAnalytics(sp)
        artistAnalytics.QueryArtistStats()
        artistAnalytics.CreatePopularityBarGraph()
        artistAnalytics.CreateGenreGroupedBarChart()

    else:
        print('Unable to obtain token\n')

# Retrieve the track ID for each track in the album, then add them to the correct timestamped playlist based on the album release date
def AddAlbumTracksToTimestampedPlaylist(spotifyClient, albumID, releaseDate):
    playlistID = GetCorrespondingTimestampedPlaylist(spotifyClient, releaseDate)
    albumTracks = spotifyClient.album(albumID)['tracks']['items']
    albumTrackIDs = []
    for track in albumTracks:
        # ADD CHECK TO SEE IF PLAYLIST ALREADY CONTAINS TRACK
        if CheckIfPlaylistContainsTrack(spotifyClient, playlistID, track['id']):
            print(track['name'] + " is already included in a playlist!")
        else:
            albumTrackIDs.append(track['id'])
    if albumTrackIDs:
        spotifyClient.user_playlist_add_tracks(myUserID, playlistID, albumTrackIDs, position=None)

# Returns the playlist ID for the corresponding timestamped playlist, given the release date of an album
def GetCorrespondingTimestampedPlaylist(spotifyClient, releaseDate):
    playlists = spotifyClient.user_playlists(myUserID, limit=50, offset=0)
    earliestDate = datetime.max
    for playlist in playlists['items']:
        try:
            playlistStartDate = datetime.strptime(playlist['name'][:dateFormatLength], dateFormat)
            #print(playlistStartDate)
            if playlistStartDate < earliestDate:
                earliestDate = playlistStartDate
            playlistEndDate = datetime.strptime(playlist['name'][-dateFormatLength:], dateFormat)
            #print(playlistEndDate)
            if releaseDate >= playlistStartDate and releaseDate <= playlistEndDate:
                return playlist['id']
        except:
            #print("unable to parse date: " + playlist['name'])
            continue

    # No existing Corresponding playlist, need to create a new playlist
    if releaseDate < earliestDate and releaseDate >= earliestDate - timedelta(weeks = playlistTimeRange) - timedelta(days = 1):
        # Create a new playlist that starts a week (playlistTimeRange) before the earlist date and ends at the earliest date
        newPlaylistName = (earliestDate - timedelta(weeks = playlistTimeRange) - timedelta(days = 1)).strftime(dateFormat) + ' to ' +  (earliestDate - timedelta(days = 1)).strftime(dateFormat)
    else:
        # Simply create a new playlist which has a start date equal to the album's release datetime
        newPlaylistName = releaseDate.strftime(dateFormat) + ' to ' + (releaseDate + timedelta(weeks = playlistTimeRange)).strftime(dateFormat)

    newPlaylist = spotifyClient.user_playlist_create(myUserID, newPlaylistName, public=True)
    return newPlaylist['id']

def CheckIfPlaylistContainsTrack(spotifyClient, playlistID, trackID):
    playlistTracks = spotifyClient.user_playlist_tracks(myUserID, playlist_id=playlistID, fields='items(track(id))', limit=100, offset=0, market=None)
    for playlistTrack in playlistTracks['items']:
        if playlistTrack['track']['id'] == trackID:
            return True
    return False


if __name__ == '__main__':
    main()



'''
if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("Can't get token for" + username)
'''
