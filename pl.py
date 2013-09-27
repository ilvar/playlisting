from flask import Flask, render_template, request

from playlists import Playlist
from spotify import get_spotify_playlist
from gmusicapi.clients.mobileclient import Mobileclient
from raven.contrib.flask import Sentry


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['HEROKU_POSTGRESQL_AMBER_URL']
# db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template('index.html', pl=None)

@app.route("/spotify/import", methods=['POST'])
def spotify_import():
    pl = get_spotify_playlist(request.form['spotify_url'])
    return render_template('playlist.html', pl=pl)

@app.route("/gmaa/move", methods=['POST'])
def gmaa_move():
    pl = Playlist.from_json(request.form['pl_data'])
    username, passwd = request.form['username'], request.form['password']

    api = Mobileclient()
    api.login(username, passwd)

    playlist_id = api.create_playlist(pl.name)

    for t in pl.tracks:
        tracks = api.search_all_access(u'%s - %s' % (t.artist, t.title), 1)
        track_ids = [t['track']['nid'] for t in tracks['song_hits']]
        api.add_songs_to_playlist(playlist_id, track_ids)

    return render_template('ok.html', pl=pl)

app.debug = True

app.config['SENTRY_DSN'] = 'https://99a69ccb434443b1af6d0e313054fa27:80914e5beb8c48ec986115c691b71829@app.getsentry.com/13587'
sentry = Sentry(app)

if __name__ == '__main__':
    app.run()