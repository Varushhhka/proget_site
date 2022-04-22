import flask
from flask import jsonify, request

from data import db_session
from data.posts import Posts

blueprint = flask.Blueprint('posts_api', __name__, template_folder='templates')


@blueprint.route('/api/posts')
def get_posts():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()
    if not posts:
        return jsonify({'error': 'Not found'})
    return jsonify({
        'posts': [item.to_dict() for item in posts]
    })


@blueprint.route('/api/posts/<int:post_id>', methods=['GET'])
def get_one_posts(post_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).get(post_id)
    if not posts:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'posts': posts.to_dict()
        }
    )


@blueprint.route('/api/posts', methods=['POST'])
def create_post():
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['id', 'author', 'category_id',
                                                 'title', 'text', 'date', 'is_finished']):
        return jsonify({'error': 'Bad request'})
    elif db_sess.query(Posts).get(request.json['id']):
        return jsonify({'error': 'Id already exists'})
    posts = Posts(
        id=request.json['id'],
        author=request.json['author'],
        category_id=request.json['category_id'],
        title=request.json['title'],
        text=request.json['text'],
        date=request.json['date'],
        is_finished=request.json['is_finished']
    )
    db_sess.add(posts)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).get(post_id)
    if not posts:
        return jsonify({'error': 'Not found'})
    db_sess.delete(posts)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/posts/<int:post_id>', methods=['PUT'])
def edit_posts(post_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).get(post_id)
    if not posts:
        return jsonify({'error': 'Not found'})
    elif not request.json:
        return jsonify({'error': 'Empty request'})
    posts.category_id = request.json.get('category_id', posts.category_id)
    posts.title = request.json.get('title', posts.title)
    posts.text = request.json.get('text', posts.text)
    posts.is_finished = request.json.get('is_finished', posts.is_finished)
    db_sess.commit()
    return jsonify({'success': 'OK'})