from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, TextAreaField
from wtforms import StringField
from wtforms.validators import DataRequired


class PostsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст', validators=[DataRequired()])
    date = StringField('Вреня создания')
    is_finished = BooleanField('Закончено?¿')
    submit = SubmitField('Готово')