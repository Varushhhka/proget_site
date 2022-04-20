from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, TextAreaField, StringField, SelectField
from wtforms.validators import DataRequired


class PostsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст', validators=[DataRequired()])
    category = SelectField('Категория', validators=[DataRequired()], coerce=int)
    is_finished = BooleanField('Закончено?¿')
    submit = SubmitField('Готово')