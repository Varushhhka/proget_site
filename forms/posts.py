from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class PostsForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired()])
    photo = FileField('Photo')
    date = StringField('End date')
    is_finished = BooleanField('Is finished')
    submit = SubmitField('Submit')