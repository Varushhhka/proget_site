import flask
from flask import jsonify, request

from data import db_session
from data.user import User

blueprint = flask.Blueprint('user_api', __name__, template_folder='templates')


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify({
        'users': [item.to_dict() for item in users]
    })


@blueprint.route('/api/users/<int:users_id>', methods=['GET'])
def get_one_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': users.to_dict()
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['surname', 'name', 'age', 'position', 'speciality',
                                                 'address', 'email', 'hashed_password']):
        return jsonify({'error': 'Bad request'})
    user = User(
        surname=request.json['surname'],
        name=request.json['name'],
        age=request.json['age'],
        position=request.json['position'],
        speciality=request.json['speciality'],
        address=request.json['address'],
        email=request.json['email'],
        hashed_password=request.json['hashed_password']
    )
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:users_id>', methods=['DELETE'])
def delete_user(users_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:users_id>', methods=['PUT'])
def edit_users(users_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(users_id)
    if not user:
        return jsonify({'error': 'Not found'})
    elif not request.json:
        return jsonify({'error': 'Empty request'})
    user.surname = request.json.get('surname', user.surname)
    user.name = request.json.get('name', user.name)
    user.age = request.json.get('age', user.age)
    user.position = request.json.get('position', user.position)
    user.speciality = request.json.get('speciality', user.speciality)
    user.address = request.json.get('address', user.address)
    user.email = request.json.get('email', user.email)
    user.hashed_password = request.json.get('hashed_password', user.hashed_password)
    db_sess.commit()
    return jsonify({'success': 'OK'})