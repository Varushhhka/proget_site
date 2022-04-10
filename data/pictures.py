import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Pictures(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'pictures'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    artists_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))

    artist = orm.relation('Artists')

    def __repr__(self):
        return f'<Artist> {self.text}'