# Artists frequently listened to
defaultArtists = {'Taylor Swift', 'Joji', 'Katy Perry', 'Miley Cyrus', 'Ariana Grande', 'Shawn Mendes'}
#defaultArtists = {'Taylor Swift'}
class MyArtists:
    longTermArtistsLimit = 50 # Only from 0-50 for now
    shortTermArtistsLimit = 30 # Only from 0-50 for now

    def __init__(self, _spotifyClient):
        self.artists = defaultArtists
        self.spotifyClient = _spotifyClient

    # Get my top artists according to spotifies calculated affinities over years of data
    def AddTopArtistsLongTerm(self):
        results = self.spotifyClient.current_user_top_artists(self.longTermArtistsLimit, 0, 'long_term')
        for artist in results['items']:
            self.artists.add(artist['name'])

    # Get my top artists according to spotifies calculated affinities over the last 4 weeks.
    # The idea is to give recognition to fresh artists that I am currently enjoying a lot, even if
    # I haven't been listening to them for a long time
    def AddTopArtistsShortTerm(self):
        results = self.spotifyClient.current_user_top_artists(self.shortTermArtistsLimit, 0, 'short_term')
        for artist in results['items']:
            self.artists.add(artist['name'])

    # maybe add a retrieval for medium term?
    # Perhaps get popular artists? or artists of popular tracks
