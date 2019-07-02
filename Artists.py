import matplotlib.pyplot as plt
import numpy as np

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

class ArtistAnalytics:
    numDataPoints = 50 # Max 50 for now

    class ArtistStats_t:
        def __init__(self, artistName, artistPopularity, artistGenres):
            self.name = artistName
            self.popularity = artistPopularity
            self.genres = artistGenres

    def __init__(self, _spotifyClient):
        self.spotifyClient = _spotifyClient

        self.shortTermList = []
        self.mediumTermList = []
        self.longTermList = []

    def QueryArtistStats(self):
        shortTermResults = self.spotifyClient.current_user_top_artists(ArtistAnalytics.numDataPoints, 0, 'short_term')
        for artist in shortTermResults['items']:
            self.shortTermList.append(ArtistAnalytics.ArtistStats_t(artist['name'],artist['popularity'],artist['genres']))
        mediumTermResults = self.spotifyClient.current_user_top_artists(ArtistAnalytics.numDataPoints, 0, 'medium_term')
        for artist in mediumTermResults['items']:
            self.mediumTermList.append(ArtistAnalytics.ArtistStats_t(artist['name'],artist['popularity'],artist['genres']))
        longTermResults = self.spotifyClient.current_user_top_artists(ArtistAnalytics.numDataPoints, 0, 'long_term')
        for artist in longTermResults['items']:
            self.longTermList.append(ArtistAnalytics.ArtistStats_t(artist['name'],artist['popularity'],artist['genres']))

    # Average popularity of top artists from different time ranges
    def CreatePopularityBarGraph(self):
        shortTermPop, mediumTermPop, longTermPop = 0,0,0
        for artist in self.shortTermList:
            shortTermPop += artist.popularity/ArtistAnalytics.numDataPoints
        for artist in self.mediumTermList:
            mediumTermPop += artist.popularity/ArtistAnalytics.numDataPoints
        for artist in self.longTermList:
            longTermPop += artist.popularity/ArtistAnalytics.numDataPoints
        data = {'Short Term': shortTermPop, 'Medium Term': mediumTermPop, 'Long Term': longTermPop}
        names = list(data.keys())
        values = list(data.values())
        plt.bar(names, values)
        plt.title('Average Popularity of My Top Artists Over Different Time Ranges')
        plt.ylabel('Spotify Popularity')
        plt.ylim(0,100)
        plt.show()

    def CreateGenreGroupedBarChart(self):
        # Should use dictionary
        shortTermGenres = {}
        mediumTermGenres = {}
        longTermGenres = {}
        for artist in self.shortTermList:
            for genre in artist.genres:
                if genre not in shortTermGenres:
                    shortTermGenres[genre] = 1
                else:
                    shortTermGenres[genre] += 1
        for artist in self.mediumTermList:
            for genre in artist.genres:
                if genre not in mediumTermGenres:
                    mediumTermGenres[genre] = 1
                else:
                    mediumTermGenres[genre] += 1
        for artist in self.longTermList:
            for genre in artist.genres:
                if genre not in longTermGenres:
                    longTermGenres[genre] = 1
                else:
                    longTermGenres[genre] += 1
        #print(shortTermGenres)
        #print(mediumTermGenres)
        #print(longTermGenres)
        width = 0.5
        #indShort = np.arange(len(shortTermGenres))
        #indMedium = np.arange(len(shortTermGenres))
        #indLong = np.arange(len(shortTermGenres))
        p1 = plt.bar(list(shortTermGenres.keys()), list(shortTermGenres.values()), width)
        p2 = plt.bar(list(mediumTermGenres.keys()), list(mediumTermGenres.values()), width)
        p3 = plt.bar(list(longTermGenres.keys()), list(longTermGenres.values()), width)
        plt.tight_layout(1)
        plt.xticks(rotation=90)
        plt.legend((p1, p2, p3), ('Short Term', 'Medium Term', 'Long Term'))
        plt.title('Genres Associated with My Top Artists Over Different Time Ranges')
        plt.xlabel('Genre')
        plt.show()
