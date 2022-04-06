import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("category.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    user = orm.relation('User')
    category = orm.relation('Category')

    def __repr__(self):
        return f'<Post> {self.text}'