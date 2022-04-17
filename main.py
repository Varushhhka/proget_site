from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import abort
from werkzeug.utils import redirect

# from blueprint import jobs_api, user_api
from data import db_session
from data.artists import Artists
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
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = Posts()
        posts.text = form.text.data
        posts.date = form.date.data
        posts.is_finished = form.is_finished.data
        current_user.posts.append(posts)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('posts.html', title='Adding a post', form=form)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_posts(id):
    form = PostsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
        if posts:
            form.text.data = posts.text
            form.date.data = posts.date
            form.is_finished.data = posts.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
        if posts:
            posts.text = form.text.data
            posts.date = form.date.data
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
    with open(f'static/info/{artist_id}.txt', encoding='utf-8') as file:
        date = file.readlines()
    sp = []
    db_sess = db_session.create_session()
    pictures = db_sess.query(Pictures).filter(Pictures.artists_id == artist_id).all()
    for elem in pictures:
        sp.append((f'imgs/artists/pictures/{elem.id}.jpg', elem.name))
    artist = db_sess.query(Artists).get(artist_id)
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


def main():
    db_session.global_init("db/artists.db")
    # app.register_blueprint(jobs_api.blueprint)
    # app.register_blueprint(user_api.blueprint)
    # post = Posts()
    # post.category_id = 1
    # post.title = 'Тема'
    # post.text = 'Найти инфу'
    # post.is_finished = True
    # db_sess = db_session.create_session()
    # db_sess.add(post)
    # db_sess.commit()
    app.run()
    # post = Posts()
    # post.category_id = 1
    # post.title = 'Русское искусство конца XIX до начала XX в.'
    # post.text = 'Для живописцев рубежа веков свойственны иные способы выражения, чем у передвижников, иные формы художественного творчества, заключающиеся в образах противоречивых и усложненных. Художники мучительно ищут гармонию и красоту в мире, который в основе своей чужд и гармонии, и красоте. ' \
    #             'Вот почему свою миссию многие видели в воспитании чувства прекрасного.'
    # post.is_finished = True
    # db_sess = db_session.create_session()
    # db_sess.add(post)
    # db_sess.commit()


if __name__ == '__main__':
    main()
