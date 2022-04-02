from flask import Flask, render_template, request, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import abort, Api
from werkzeug.utils import redirect

# from api import user_resource, job_resource
# from blueprint import jobs_api, user_api
from data import db_session

from data.posts import Posts
from data.user import User
from forms.posts import PostsForm
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
# api = Api()
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


@app.route('/posts',  methods=['GET', 'POST'])
# @login_required
def add_posts():
    form = PostsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = Posts()
        posts.text = form.text.data
        posts.photo = form.photo.data
        posts.date = form.date.data
        posts.is_finished = form.is_finished.data
        current_user.posts.append(posts)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('posts.html', title='Adding a post', form=form)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_posts(id):
    form = PostsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
        if posts:
            form.text.data = posts.text
            form.photo.data = posts.photo
            form.date.data = posts.date
            form.is_finished.data = posts.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
        if posts:
            posts.text = form.text.data
            posts.photo = form.photo.data
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


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    db_session.global_init("db/artists.db")
    # api.add_resource(user_resource.UsersResource, '/api/v2/users')
    # api.add_resource(user_resource.UsersListResource, '/api/v2/users/<int:user_id>')
    # api.add_resource(job_resource.postsResource, '/api/v2/posts')
    # api.add_resource(job_resource.postsListResource, '/api/v2/posts/<int:job_id>')
    # app.register_blueprint(jobs_api.blueprint)
    # app.register_blueprint(user_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()