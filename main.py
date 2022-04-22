import requests as requests
from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import abort

from data import db_session
from data.artists import Artists
from data.category import Category
from data.pictures import Pictures
from data.posts import Posts
from data.user import User
from forms.posts import PostsForm
from forms.user import RegisterForm, LoginForm

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            photo=form.photo.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Регистрация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/posts', methods=['GET', 'POST'])
@login_required
def add_posts():
    form = PostsForm()
    db_sess = db_session.create_session()
    form.category.choices = [(c.id, c.name) for c in db_sess.query(Category).all()]
    if form.validate_on_submit():
        posts = Posts()
        posts.title = form.title.data
        posts.text = form.text.data
        posts.is_finished = form.is_finished.data
        posts.category_id = form.category.data
        current_user.posts.append(posts)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('posts.html', title='Adding a post', form=form)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_posts(id):
    form = PostsForm()
    db_sess = db_session.create_session()
    form.category.choices = [(c.id, c.name) for c in db_sess.query(Category).all()]
    if request.method == "GET":
        posts = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
        if posts:
            form.title.data = posts.title
            form.text.data = posts.text
            form.category.data = posts.category_id
            form.is_finished.data = posts.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        posts = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
        if posts:
            posts.text = form.text.data
            posts.title = form.title.data
            posts.category_id = form.category.data
            posts.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('posts.html', title='Edit a post', form=form)


@app.route('/posts_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def posts_delete(id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
    if posts:
        db_sess.delete(posts)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


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
    # app.register_blueprint(jobs_api.blueprint)
    # app.register_blueprint(user_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
