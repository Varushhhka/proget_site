from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms import BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostsForm(FlaskForm):
    text = TextAreaField('Text', validators=[DataRequired()])
    date = StringField('End date')
    is_finished = BooleanField('Is finished')
    submit = SubmitField('Submit')