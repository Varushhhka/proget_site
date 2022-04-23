import os

import requests as requests
from flask import Flask, render_template
from flask_login import LoginManager
from flask_restful import abort

from api import posts_api, user_api
from blueprint import posts_blueprint, user_blueprint
from data import db_session
from data.artists import Artists
from data.pictures import Pictures
from data.posts import Posts
from data.user import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()
    return render_template("index.html", posts=posts)


@app.route('/ost')
def ost():
    with open(f'static/info/ost.txt', encoding='utf-8') as file:
        date = file.readlines()
    context = {
        'pro': date[0].split('*'),
        'con': date[1],
        'group': date[2],
        'axrr': date[3].split('*'),
        'omaxrr': date[4].split('*'),
        'osx': date[5].split('*'),
        'rapx': date[6].split('*'),
        'fosx': date[7],
        'lef': date[8].split('*'),
        'oct': date[9].split('*')
    }
    return render_template('ost.html', **context)


@app.route('/artists')
def cards():
    list_info = []
    db_sess = db_session.create_session()
    artists = db_sess.query(Artists).all()
    for artist in artists:
        list_info.append({
            'image': f'imgs/artists/photo/{artist.id}.jpg',
            'full_name': f'{artist.name} {artist.surname}',
            'info': artist.initial_text,
            'id': artist.id
        })
    return render_template('all_artists.html', artists=list_info)


@app.route('/artist/<int:artist_id>')
def artist_view(artist_id):
    db_sess = db_session.create_session()
    artist = db_sess.query(Artists).get(artist_id)
    if not artist:
        abort(404)
    with open(f'static/info/{artist_id}.txt', encoding='utf-8') as file:
        date = file.readlines()
    sp = []
    pictures = db_sess.query(Pictures).filter(Pictures.artists_id == artist_id).all()
    for elem in pictures:
        sp.append((f'imgs/artists/pictures/{elem.id}.jpg', elem.name))
    artist_info = {
        'name': f'{artist.name} {artist.patronymic} {artist.surname}',
        'photo': f'imgs/artists/photo/{artist.id}.jpg',
        'initial_text': artist.initial_text
    }
    context = {
        'artist': artist_info,
        'biography': date[0],
        'facts': date[1].split('*'),
        'family': date[2],
        'awards': date[3].split('*'),
        'list_of_images': sp
    }
    return render_template('artist.html', **context)


@app.route('/translate/<int:post_id>')
def translate(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).get(post_id)
    if not post:
        abort(404)

    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    data = {
        'yandexPassportOauthToken': 'AQAAAABbFfJRAATuwZ7L2UW9e0B3qlbQuv8wXRo'
    }
    headers = {
        'ContentType': 'Application/json'
    }
    token = requests.request("POST", url, json=data, headers=headers).json()['iamToken']

    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    folder_id = 'b1g9us6433g8mth0q7m4'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token)
    }
    body = {
        "targetLanguageCode": 'en',
        "texts": [post.title, post.text],
        "folderId": folder_id,
    }
    data = requests.request("POST", url, headers=headers, json=body).json()['translations']

    context = {
        'post': post,
        'translate': {
            'title': data[0]['text'],
            'text': data[1]['text']
        }
    }
    return render_template('translate.html', **context)


def main():
    db_session.global_init("./db/artists.db")
    app.register_blueprint(posts_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(posts_blueprint.blueprint)
    app.register_blueprint(user_blueprint.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
