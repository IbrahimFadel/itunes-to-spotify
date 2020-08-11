import xml.etree.ElementTree as ET
import spotify

# xml_path = 'LoFi.xml'
# playlist_name = 'testing'

xml_path = 'LoFi.xml'
playlist_name = 'test'

def parse_itunes_playlist_xml():
	track_data = []
	tree = ET.parse(xml_path)
	root = tree.getroot()
	data = root.find('dict')
	track_list = data.find('dict')
	for track in track_list.findall('dict'):
		key_value_counter = 0
		track_dict = {}
		pair = []
		for data in track:
			if key_value_counter % 2 == 0 and key_value_counter != 0:
				if pair[0] == 'Name' or pair[0] == 'Artist':
					track_dict[pair[0]] = pair[1]
					if pair[0] == 'Artist':
						track_dict["tried_everything"] = False
						track_data.append(track_dict)
				pair = []


			pair.append(data.text)
			key_value_counter += 1

	return track_data

def main():
	global playlist_name

	# spotify.test()
	tracks = parse_itunes_playlist_xml()
	print("Parsed Playlist XML")
	# print(tracks)
	spotify.add_tracks_to_playlist(tracks, playlist_name)


if __name__ == "__main__":
	main()
