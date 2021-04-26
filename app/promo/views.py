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

    # print(Product.get_showes_poduct(product_id=2).all())
    # session.rollback()

    return redirect(url_for('.outlet_list'))
    # return render_template('promo/index.html')


@promo_app.route('/outletList', methods=['GET'])
@decorators.login_required
def outlet_list():
    try:
        outlet_items = Outlet.query

        return render_template('promo/outlet/list.html', outlet_items=outlet_items)
    except Exception as err:
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
            outlet = Outlet.new(
                name=name,
                num=1,
                lat=lat,
                lon=lon,
                ip=ip,
                status=1
            )
            if outlet:
                flash(f'Точка добавлена')
                return redirect(url_for('promo.outlet_list'))

        return render_template('promo/outlet/new.html', form=form)
    except Exception as err:
        return str(err)


@promo_app.route('/outletList/<outlet_id>', methods=['GET', 'POST'])
@decorators.login_required
def outlet_edit(outlet_id):
    try:

        outlet = Outlet.query.filter_by(id=outlet_id).first()
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
        return str(err)


@promo_app.route('/outletList/<outlet_id>/delete', methods=['GET', 'POST'])
@decorators.login_required
def outlet_delete(outlet_id):
    outlet: Outlet = Outlet.query.get(outlet_id)
    if not outlet:
        return render_template('404.html'), 404

    form = forms.FormYes()
    if form.is_submitted():
        outlet.remove()
        return redirect(url_for('promo.outlet_list'))

    return render_template('promo/outlet/delete.html', outlet=outlet, form=form)


@promo_app.route('/products', methods=['GET'])
@decorators.login_required
def product_list():
    try:
        products = Product.query

        return render_template('promo/products/products.html', products=products)
    except Exception as err:
        return str(err)


@promo_app.route('/products/create', methods=['GET', 'POST'])
@decorators.login_required
def product_new():

    form = forms.NewProduct()
    if form.is_submitted():
        name = request.form.get('name')
        code = request.form.get('code')
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        max_count = request.form.get('max_count')
        max_count_per_outlet = request.form.get('max_count_per_outlet')
        bar_code = request.form.get('bar_code')
        enabled = request.form.get('enabled')

    if form.validate_on_submit():
        Product.new(
            name=name,
            code=code,
            date_begin=date_begin,
            date_end=date_end,
            max_count=max_count,
            max_count_per_outlet=max_count_per_outlet,
            bar_code=bar_code,
            enabled=enabled
        )
        flash('Добавлен', 'success')
        return redirect(url_for('.product_list'))

    return render_template('promo/products/new.html', form=form)


@promo_app.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@decorators.login_required
def product_edit(product_id):
    product = Product.query.get(product_id)

    form = forms.NewProduct()
    if form.is_submitted():
        name = request.form.get('name')
        code = request.form.get('code')
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        max_count = request.form.get('max_count')
        max_count_per_outlet = request.form.get('max_count_per_outlet')
        bar_code = request.form.get('bar_code')
        enabled = request.form.get('enabled')

    if form.validate_on_submit():
        product.update(
            name=name,
            code=code,
            date_begin=date_begin,
            date_end=date_end,
            max_count=max_count,
            max_count_per_outlet=max_count_per_outlet,
            bar_code=bar_code,
            enabled=enabled
        )
        flash('Сохранено', 'success')
        return redirect(request.path)

    return render_template('promo/products/edit.html', product=product, form=form)


@promo_app.route('/products/<product_id>/delete', methods=['GET', 'POST'])
@decorators.login_required
def product_delete(product_id):
    product = Product.query.get(product_id)

    form = forms.FormYes()
    if form.validate_on_submit():
        product.remove()
        return redirect(url_for('.product_list'))

    return render_template('promo/products/delete.html', product=product, form=form)
