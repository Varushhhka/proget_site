import flask
from flask import redirect, render_template, request
from flask_login import login_required, current_user
from flask_restful import abort

from data import db_session
from data.category import Category
from data.posts import Posts
from forms.posts import PostsForm

blueprint = flask.Blueprint('posts_blueprint', __name__, template_folder='templates')


@blueprint.route('/posts', methods=['GET', 'POST'])
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


@blueprint.route('/posts/<int:id>', methods=['GET', 'POST'])
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


@blueprint.route('/posts_delete/<int:id>', methods=['GET', 'POST'])
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