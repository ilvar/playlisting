#!/usr/bin/python

"""
https://github.com/vietjtnguyen/export-spotify-playlist
"""

import csv
import collections
import urllib2

import re

from playlists import Playlist, Track


# http://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
import HTMLParser

html_parser = HTMLParser.HTMLParser()

# http://wwwsearch.sourceforge.net/mechanize/
import mechanize


def get_spotify_playlist(playlist):
    if playlist.startswith('http'):
        playlist_url = playlist
    else:
        playlist_url = 'http://open.spotify.com/user/{}/playlist/{}'.format(
            *re.search('spotify:user:(.+):playlist:(.+)', playlist).groups()
        )

    playlist_br = mechanize.Browser()
    playlist_br.open(playlist_url)

    playlist_name = re.search(r'<h1 itemprop="name">(.+)</h1>', playlist_br.response().read()).groups()[0]

    pl = Playlist(playlist_name.decode('utf8'), playlist)

    # http://docs.python.org/2/library/functions.html#filter
    track_links = filter(lambda x: x.url.startswith('/track/'), playlist_br.links())

    # http://docs.python.org/2/library/collections.html#ordereddict-objects
    tracks = collections.OrderedDict()
    for track_link in track_links:
        if not tracks.has_key(track_link.url):
            tracks[track_link.url] = {
                'mechanized_link': track_link,
                'track_url': 'http://open.spotify.com' + track_link.url,
                'title': track_link.text
            }

    for track in tracks.values():
        try:
            track_html = mechanize.urlopen(track['track_url']).read()
        except urllib2.HTTPError as e:
            print('{:}, HTTP Error 404, {:} not found'.format(track['title'], track['track_url']))
            track['artist_url'], track['artist'], track['album_url'], track['album'] = ('', '', '', '')
            continue

        # http://docs.python.org/2/library/re.html
        matches = re.search(
            r'<h1 itemprop="name">(.+)</h1>[ \t\n\r]*<h2> by <a href="(/artist/.+)">(.+)</a></h2>[ \t\n\r]*</div>[ \t\n\r]*<h3>Tracks in <a href="(/album/.+)">(.+)</a></h3>',
            track_html)

        track['title'], track['artist_url'], track['artist'], track['album_url'], track['album'] = matches.groups()
        title, artist, album = map(
            lambda s: html_parser.unescape(s.decode('utf-8', 'xmlcharrefreplace')),
            (track['title'], track['artist'], track['album'])
        )

        pl.add_track(
            Track(title.decode('utf8', 'ignore'), album.decode('utf8', 'ignore'), artist.decode('utf8', 'ignore'))
        )

    return pl
