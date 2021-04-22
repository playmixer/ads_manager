from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, SelectField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional
from app.manage.models import GroupAdvertise


class FormNewGroup(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])


class FormEditGroup(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    status = SelectField('Статус', coerce=int, choices=GroupAdvertise.StatusType)


class FormNewAdvertise(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    file = FileField('Файл', validators=[DataRequired()])
    shows_per_day = IntegerField('Максимальное кол-во показов в день *', validators=[Optional()])
    shows_max = IntegerField('Максимальное кол-во показов всего *', validators=[Optional()])
    time_start = DateField('Дата начала показа', validators=[DataRequired()], format='%Y-%m-%d')
    time_end = DateField('Дата окончания показа', validators=[Optional()], format='%Y-%m-%d')


class FormEditAdvertise(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    # file = FileField('Файл', validators=[DataRequired()])
    shows_per_day = IntegerField('Максимальное кол-во показов в день *', validators=[Optional()])
    shows_max = IntegerField('Максимальное кол-во показов всего *', validators=[Optional()])
    time_start = DateField('Дата начала показа', validators=[DataRequired()], format='%Y-%m-%d')
    time_end = DateField('Дата окончания показа', validators=[Optional()], format='%Y-%m-%d')


class FormYes(FlaskForm):
    submit_yes = SubmitField('Да')
