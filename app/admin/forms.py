from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, SelectField, IntegerField, FloatField
from wtforms.fields.html5 import DateField, DateTimeLocalField
from wtforms.validators import DataRequired, Optional, Length, IPAddress, ValidationError
from app.manage.models import GroupAdvertise
from app.promo.models import Outlet


class Product(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=50)])
    code = StringField('Код', validators=[DataRequired(), Length(max=50)])
    date_begin = DateTimeLocalField('Дата начала', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    date_end = DateTimeLocalField('Дата окончания', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    max_count = IntegerField('Количество', validators=[Optional()])
    max_count_per_outlet = IntegerField('Количество для точки', validators=[Optional()])
    bar_code = StringField('Баркод', validators=[DataRequired()])
    enabled = IntegerField('Разрешен', validators=[Optional()])


class FormYes(FlaskForm):
    submit_yes = SubmitField('Да')


def valid_outlet_name(form, field):
    if len(field.data) > 50:
        raise ValidationError('Длина не может привышать 50 символов')


class NewOutlet(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), valid_outlet_name])
    ip = StringField('IP адрес', validators=[IPAddress()])
    lat = FloatField('Широта', validators=[DataRequired()])
    lon = FloatField('Долгота', validators=[DataRequired()])
    token = StringField('Токен', validators=[Optional(), Length(max=50)])
    status = SelectField('Статус', coerce=int, choices=Outlet.choices_status)
