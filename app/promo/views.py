from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import *
from . import forms
from src import validate
from app.auth import decorators

promo_app = Blueprint(
    'promo',
    __name__,
    template_folder='templates'
)

__all__ = ['promo_app']


@promo_app.route('/')
def index():

    # print(Azs.get_create_product(1).all())
    # print(Azs.get_usage_product(1).all())
    # session.rollback()

    return redirect(url_for('.outlet_list'))
    # return render_template('promo/index.html')


@promo_app.route('/outletList', methods=['GET'])
@decorators.login_required
def outlet_list():
    try:
        outlet_items = session.query(Azs)

        return render_template('promo/outlet/list.html', outlet_items=outlet_items)
    except Exception as err:
        session.rollback()
        return str(err)


@promo_app.route('/outletList/create', methods=['GET', 'POST'])
@decorators.login_required
def outlet_new():
    try:
        form = forms.NewOutlet()

        name = request.form.get('name')
        ip = request.form.get('ip')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        if form.is_submitted():
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

        if form.validate_on_submit():
            azs = Azs.new(
                name=name,
                num=1,
                lat=lat,
                lon=lon,
                ip=ip,
                status=1
            )
            if azs:
                flash(f'Точка добавлена')
                return redirect(url_for('promo.outlet_list'))

        return render_template('promo/outlet/new.html', form=form)
    except Exception as err:
        session.rollback()
        return str(err)


@promo_app.route('/outletList/<outlet_id>', methods=['GET', 'POST'])
@decorators.login_required
def outlet_edit(outlet_id):
    try:

        outlet = session.query(Azs).filter_by(id=outlet_id).first()
        if not outlet:
            return render_template('404.html'), 404

        form = forms.NewOutlet()

        name = request.form.get('name')
        ip = request.form.get('ip')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        status = request.form.get('status')
        if form.is_submitted():
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

        if form.validate_on_submit():
            outlet.update(
                name=name,
                lat=lat,
                lon=lon,
                ip=ip,
                status=status
            )

        return render_template('promo/outlet/edit.html', form=form, outlet=outlet)
    except Exception as err:
        session.rollback()
        return str(err)


@promo_app.route('/outletList/<outlet_id>/delete', methods=['GET', 'POST'])
@decorators.login_required
def outlet_delete(outlet_id):
    outlet: Azs = session.query(Azs).get(outlet_id)
    if not outlet:
        return render_template('404.html'), 404

    form = forms.FormYes()
    if form.is_submitted():
        outlet.remove()
        return redirect(url_for('promo.outlet_list'))

    return render_template('promo/outlet/delete.html', outlet=outlet, form=form)


@promo_app.route('/productList', methods=['GET'])
@decorators.login_required
def product_list():
    products = session.query(Product)

    return render_template('promo/product/list.html', products=products)
