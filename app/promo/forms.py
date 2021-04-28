from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, SelectField, IntegerField, FloatField, \
    HiddenField, SelectMultipleField
from wtforms.fields.html5 import DateField, DateTimeLocalField
from wtforms.validators import DataRequired, Optional, IPAddress, Length, ValidationError
from .models import Outlet, Product, db
from app.manage.models import GroupAdvertise
from src import validate
from typing import List


def valid_outlet_name(form, field):
    if len(field.data) > 50:
        flash('Название не может превышать длину 50 символов', 'error')
        raise ValidationError('Длина не может привышать 50 символов')


class NewForm(FlaskForm):
    __form_name__ = None

    def is_form(self, name):
        return self.__form_name__ == name


class NewOutlet(NewForm):
    __form_name__ = 'form_outlet'

    form_name = HiddenField('form_name', validators=[DataRequired()], default=__form_name__)
    name = StringField('Название', validators=[DataRequired(), valid_outlet_name])
    ip = StringField('IP адрес', validators=[IPAddress()])
    lat = FloatField('Широта', validators=[DataRequired()])
    lon = FloatField('Долгота', validators=[DataRequired()])
    status = SelectField('Статус', coerce=int, choices=Outlet.choices_status)

    def new(self, name, lat, lon, ip, user):
        if self.is_submitted():
            if not validate.ip_address(ip):
                flash('Не корректный ip адрес', 'error')
            try:
                float(lat)
            except ValueError:
                flash('Не корректная широта', 'error')
            try:
                float(lon)
            except ValueError:
                flash('Не корректная долгота', 'error')

        if self.validate_on_submit():
            outlet = Outlet.new(
                name=name,
                num=1,
                lat=lat,
                lon=lon,
                ip=ip,
                status=1,
                user=user
            )
            if outlet:
                return True
        return False

    def update(self, outlet, name, lat, lon, ip, status):

        if self.is_submitted():
            if not validate.ip_address(ip):
                flash('Не корректный ip адрес', 'error')
            try:
                float(lat)
            except ValueError:
                flash('Не корректная широта', 'error')
            try:
                float(lon)
            except ValueError:
                flash('Не корректная долгота', 'error')

        if self.validate_on_submit():
            outlet.update(
                name=name,
                lat=lat,
                lon=lon,
                ip=ip,
                status=status
            )
            if outlet:
                return True
        return False


class NewProduct(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=50)])
    code = StringField('Код', validators=[DataRequired(), Length(max=50)])
    date_begin = DateTimeLocalField('Дата начала', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    date_end = DateTimeLocalField('Дата окончания', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    max_count = IntegerField('Количество', validators=[Optional()])
    max_count_per_outlet = IntegerField('Количество для точки', validators=[Optional()])
    bar_code = StringField('Баркод', validators=[DataRequired()])
    enabled = SelectField('Статус', validators=[Optional()], coerce=int, choices=Product.choices_enabled)


class FormYes(FlaskForm):
    submit_yes = SubmitField('Да')


class OutletAdsGroup(NewForm):
    __form_name__ = 'form_outlet_ads_group'

    form_name = HiddenField('form_name', validators=[DataRequired()], default=__form_name__)
    ads_groups = SelectMultipleField('Рекламные группы', coerce=int)

    def set_ads_group_choices(self, choices):
        self.ads_groups.choices = choices

    def set(self, outlet: Outlet, group_list: List[str]):
        if self.validate_on_submit():
            for g in outlet.groups:
                if g.id not in [int(id) for id in group_list]:
                    group = GroupAdvertise.query.get(g.id)
                    outlet.delete_from_group(group, False)

            for g_id in group_list:
                group = GroupAdvertise.query.get(g_id)
                if not outlet.is_in(group):
                    outlet.append_group(group, False)

            db.session.commit()
            return True
        return False


class AdsGroupToken(NewForm):
    __form_name__ = 'ads_group_token'

    form_name = HiddenField('form_name', validators=[DataRequired()], default=__form_name__)
    token = StringField('Токен', validators=[Optional()])
    # submit_refresh = SubmitField('Изменить токен на новый')

    def token_create(self, outlet: Outlet):
        if self.validate_on_submit():
            outlet.token_create()
            return True
        return False
