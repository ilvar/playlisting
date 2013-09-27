#!/usr/bin/python
import json


class Track:
    title = ''
    album = ''
    artist = ''

    def __init__(self, title, album, artist):
        self.title, self.album, self.artist = title, album, artist

    def get_data(self):
        return {
            'title': self.title,
            'album': self.album,
            'artist': self.artist,
        }

class Playlist:
    name = ''
    url = 'http://'
    tracks = None

    def __init__(self, playlist_name, url):
        self.name = playlist_name
        self.url = url
        self.tracks = []

    def add_track(self, track):
        self.tracks.append(track)

    def to_json(self):
        return json.dumps({
            'name': self.name,
            'url': self.url,
            'tracks': [t.get_data() for t in self.tracks],
        })

    @classmethod
    def from_json(self, json_data):
        data = json.loads(json_data)
        pl = Playlist(data['name'], data['url'])
        pl.tracks = [Track(**td) for td in data['tracks']]
        return pl
