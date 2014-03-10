NAME = 'Sweflix'

LATEST_URL = 'http://sweflix.com/api-v3/json.php?lim=200'
POPULAR_URL = 'http://sweflix.com/api-v3/json.php?lim=200&orderBy=hits'
GENRE_URL = 'http://sweflix.com/api-v3/json.php?lim=200&cat=%s'
OMDB_URL = 'http://www.omdbapi.com/?i=%s'

GENRES = ['Action', 'Adventure', 'Animation', 'Barn', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Svenskt', 'Thriller']

RE_IMDB_ID = Regex('^tt\d{7}$')
RE_DURATION = Regex('(?:(\d+)h)?(\d+)min')

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
	HTTP.Headers['Referer'] = 'http://sweflix.com/'

####################################################################################################
@handler('/video/sweflix', NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key = Callback(ListMovies, title='Latest Uploads', url=LATEST_URL), title='Latest Uploads'))
	oc.add(DirectoryObject(key = Callback(ListMovies, title='Popular', url=POPULAR_URL), title='Popular'))
	oc.add(DirectoryObject(key = Callback(ListGenres), title='Genres'))

	if Client.Product != 'PlexConnect':
		oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.sweflix', title='Search', summary='Search Movies on Sweflix', prompt='Search for...'))

	return oc

####################################################################################################
@route('/video/sweflix/listmovies')
def ListMovies(title, url):

	oc = ObjectContainer(title2=title)

	for movie in JSON.ObjectFromURL(url):

		if movie['type'] not in ('barn', 'film'):
			continue

		url = 'http://sweflix.com/#%s' % movie['id']
		title = movie['titel']
		summary = movie['plot']

		imdb_id = movie['imdb']

		if (title is None or summary is None) and (imdb_id is not None and RE_IMDB_ID.search(imdb_id)):
			omdb_movie = JSON.ObjectFromURL(OMDB_URL % imdb_id)
			title = omdb_movie['Title'] if title is None else title
			summary = omdb_movie['Plot'] if summary is None else summary

		if title is None:
			continue

		thumb = movie['poster']
		genres = movie['cat'].split(', ')
		year = int(movie['year']) if movie['year'] is not None or movie['year'] != "" else None
		try: rating = float(movie['imdbrate'])
		except: rating = None

		try:
			duration = movie['duration'].replace(' ', '')
			ms = 0
			(h, m) = RE_DURATION.search(duration).groups()
			if h:
				ms += int(h) * 60 * 60 * 1000
			ms += int(m) * 60 * 1000
		except:
			ms = None

		oc.add(MovieObject(
			url = url,
			title = String.DecodeHTMLEntities(title),
			summary = String.DecodeHTMLEntities(summary),
			thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.jpg'),
			genres = genres,
			year = year,
			rating = rating,
			duration = ms
		))

	return oc

####################################################################################################
@route('/video/sweflix/listgenres')
def ListGenres():

	oc = ObjectContainer(title2='Genres')

	for genre in GENRES:
		oc.add(DirectoryObject(key = Callback(ListMovies, title=genre, url=GENRE_URL % genre), title=genre))

	return oc
