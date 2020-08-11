class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path="spotipy_cache"))

user_id = os.environ['SPOTIFY_USER_ID']

def create_playlist(name):
	global sp, user_id
	sp.user_playlist_create(user_id, name)

def get_playlist_id(playlist_name):
	global sp, user_id

	playlists = sp.user_playlists(user_id, limit=3)

	for playlist in playlists['items']:
		if playlist['name'] == playlist_name:
			return playlist['id']

def find_correct_track_from_search_results(search_results, track):
	index = 0
	for item in search_results['tracks']['items']:
		for artist in item['artists']:
			if artist['name'] == track['Artist']:
				print(f"{bcolors.OKGREEN}Found track id for: {bcolors.ENDC}{track['Name']} -- {artist['name']}, {item['id']}")
				return item['id']
			else:
				if index == 9:
					print(f"{bcolors.FAIL}Could not find track id for: {bcolors.ENDC}{track['Name']} -- {track['Artist']}, {item['id']}")
					return False
		index += 1

def try_no_feat(track):
	feat_index = track['Name'].find('(feat')
	new_name = track['Name']
	if feat_index != -1:
		new_name = new_name[:feat_index - 1]
		print(f"{bcolors.WARNING}Trying search again: {bcolors.ENDC}{new_name}")

		search_results = sp.search(new_name, 10, 0, "track")
		track_id = find_correct_track_from_search_results(search_results, track)

		return track_id

def try_no_feat_with_artist_name_in_title(track):
	feat_index = track['Name'].find('(feat')
	new_name = track['Name']
	if feat_index != -1:
		new_name = new_name[:feat_index - 1]
	new_name = f"{new_name} {track['Artist']}"
	print(f"{bcolors.WARNING}Trying search again: {bcolors.ENDC}{new_name}")

	search_results = sp.search(new_name, 10, 0, "track")
	track_id = find_correct_track_from_search_results(search_results, track)

	return track_id

def try_artist_name_in_title(track):
	new_name = f"{track['Name']} {track['Artist']}"
	print(f"{bcolors.WARNING}Trying search again: {bcolors.ENDC}{new_name}")

	search_results = sp.search(new_name, 10, 0, "track")
	track_id = find_correct_track_from_search_results(search_results, track)

	return track_id

def try_each_individual_artist(track):
	new_name = track['Name']

	commas = track['Artist'].replace("&#38;", ",")
	commas = commas.replace("&", ",")
	commas = commas.replace(" ,", ",")
	names = commas.split(",")
	for i, s in enumerate(names):
		names[i] = s.strip()

	search_results = sp.search(new_name, 10, 0, "track")
	for name in names:
		track_id = find_correct_track_from_search_results(search_results, {
			'Name': new_name,
			'Artist': name
		})

		if track_id: return track_id

def try_each_individual_artist_no_feat(track):
	feat_index = track['Name'].find('(feat')
	name_without_feat = track['Name']
	if feat_index != -1:
		name_without_feat = track['Name'][:feat_index - 1]

	commas = track['Artist'].replace("&#38;", ",")
	commas = commas.replace("&", ",")
	commas = commas.replace(" ,", ",")
	names = commas.split(",")
	for i, s in enumerate(names):
		names[i] = s.strip()

	for name in names:
		new_name = f"{name_without_feat} {name}"
		search_results = sp.search(new_name, 10, 0, "track")
		track_id = find_correct_track_from_search_results(search_results, {
			'Name': new_name,
			'Artist': name
		})

		if track_id: return track_id

def get_track_id(track):
	search_results = sp.search(track['Name'], 10, 0, "track")
	track_id = find_correct_track_from_search_results(search_results, track)
	if track_id:
		return track_id
	else:
		track_id = try_no_feat(track)
		if track_id: return track_id
		track_id = try_no_feat_with_artist_name_in_title(track)
		if track_id: return track_id
		track_id = try_artist_name_in_title(track)
		if track_id: return track_id
		track_id = try_each_individual_artist(track)
		if track_id: return track_id
		track_id = try_each_individual_artist_no_feat(track)

		return track_id

def get_track_ids(tracks):
	global sp
	ids = []
	not_found = []
	for track in tracks:
		print(f"{bcolors.OKBLUE}Searching: {bcolors.ENDC}{track['Name']}")
		track_id = get_track_id(track)
		if track_id:
			ids.append(track_id)
		else:
			not_found.append(track)

	return ids, not_found

def chunk(lst, n):
	for i in range(0, len(lst), n):
		yield lst[i:i + n]

def add_tracks_to_playlist(tracks, playlist_name):
	global sp

	track_ids, not_found = get_track_ids(tracks)

	print(bcolors.ENDC)

	print(f"Found all track ids: {track_ids}")

	create_playlist(playlist_name)
	print(f"Created playlist: {playlist_name}")
	print(f"Getting playlist ID for {playlist_name}")
	playlist_id = get_playlist_id(playlist_name)
	print(f"Found playlist ID: {playlist_id}")

	chunked_track_ids = chunk(track_ids, 100)
	for track_id_list in chunked_track_ids:
		sp.playlist_add_items(playlist_id, track_id_list)
		print("Added track chunk")

	print(f"{bcolors.FAIL}Could not find any of these tracks:{bcolors.ENDC}")
	for track in not_found:
		print(f"{track['Name']} -- {track['Artist']}")
