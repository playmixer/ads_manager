from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class FormNewGroup(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])


class FormNewAdvertise(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    file = FileField('Файл', validators=[DataRequired()])
    time_start = DateField('Дата начала показа', validators=[DataRequired()], format='%Y-%m-%d')
    time_end = DateField('Дата окончания показа', validators=[DataRequired()], format='%Y-%m-%d')
