from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, TextAreaField
from wtforms import StringField
from wtforms.validators import DataRequired


class PostsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    date = StringField('Date')
    is_finished = BooleanField('Is finished')
    submit = SubmitField('Submit')