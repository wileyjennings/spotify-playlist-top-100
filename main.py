from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env

DATE_TOP100 = '1978-02-23'

# Check that date is valid

# Scrape Billboard Top 100
response = requests.get(f'https://www.billboard.com/charts/hot-100/{DATE_TOP100}')
top100_webpage = response.text
soup = BeautifulSoup(top100_webpage, "html.parser")

# Parse song and artist names from Billboard
songs = soup.find_all(
    name="span",
    class_="chart-element__information__song text--truncate color--primary"
)
artists = soup.find_all(
    name="span",
    class_="chart-element__information__artist text--truncate color--secondary"
)

song_names = [elm.get_text() for elm in songs]
artist_names = [elm.get_text() for elm in artists]
# [print(song) for song in song_names]
# [print(artist) for artist in artist_names]

# Authenticate Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope='playlist-modify-private playlist-read-private'))

# Get track IDs
song_results = [
    sp.search(q=f'artist:{artist} track:{name}', limit=1, type='track')
    for artist, name in zip(artist_names, song_names)
]
# [print(song) for song in song_results]
# # [print(result) for result in song_results]
song_ids = [elm['tracks']['items'][0]['id'] for elm in song_results if len(elm['tracks']['items']) > 0]

# [print(elm) for elm in song_ids]

# Check if playlist already exists; only create if does not exist

# Create playlist
sp.user_playlist_create(user='wiley.jennings', name=f'PyTop100-{DATE_TOP100}', public=False)

# Get playlist ID
playlists = sp.current_user_playlists()['items']
playlist_index = next(
    (index for (index, elm) in enumerate(playlists) if elm['name'] == f'PyTop100-{DATE_TOP100}'),
    None
)
playlist_id = playlists[playlist_index]['id']
sp.playlist_add_items(playlist_id=playlist_id, items=song_ids)
