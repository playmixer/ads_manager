from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, SelectField, IntegerField, FloatField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional, IPAddress, Length, ValidationError
from .models import Azs


def valid_outlet_name(form, field):
    if len(field.data) > 50:
        flash('Название не может превышать длину 50 символов', 'error')
        raise ValidationError('Длина не может привышать 50 символов')


class NewOutlet(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), valid_outlet_name])
    ip = StringField('IP адрес', validators=[IPAddress()])
    lat = FloatField('Широта', validators=[DataRequired()])
    lon = FloatField('Долгота', validators=[DataRequired()])
    status = SelectField('Статус', coerce=int, choices=Azs.choices_status)


class FormYes(FlaskForm):
    submit_yes = SubmitField('Да')