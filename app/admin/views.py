from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.auth import decorators
from .promo import database
from app.manage.models import *
from src.logger import logger
from app.promo.models import *
from . import forms
from src import validate

admin = Blueprint(
    'admin',
    __name__,
    template_folder='templates'
)


@admin.route('/')
@decorators.role_required(role='admin')
@decorators.login_required
def index():
    return redirect(url_for('.promo_azs_product'))


@admin.route('/promo/azs')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs():
    try:
        azs_list = session.query(Outlet)
        return render_template('admin/outlet/outlet.html', outlet_list=azs_list)
    except Exception as err:
        session.rollback()
        logger.error(f'promo_azs \n\t{str(err)}')
        return str(err)


@admin.route('/promo/azs/new', methods=['GET', 'POST'])
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs_new():
    try:
        form = forms.NewOutlet()

        if form.is_submitted():
            name = request.form.get('name')
            ip = request.form.get('ip')
            lat = request.form.get('lat')
            lon = request.form.get('lon')
            status = request.form.get('status')
            token = request.form.get('token')

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
                lat=lat,
                lon=lon,
                ip=ip,
                token=token,
                status=status
            )
            if outlet:
                return redirect(url_for('admin.promo_azs'))

        return render_template('admin/outlet/new.html', form=form)
    except Exception as err:
        session.rollback()
        logger.error(f'promo_azs \n\t{str(err)}')
        return str(err)


@admin.route('/promo/azs/<outlet_id>/edit', methods=['GET', 'POST'])
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs_edit(outlet_id):
    try:
        outlet = Outlet.query.get(outlet_id)

        form = forms.NewOutlet()

        if form.is_submitted():
            name = request.form.get('name')
            ip = request.form.get('ip')
            lat = request.form.get('lat')
            lon = request.form.get('lon')
            status = request.form.get('status')
            token = request.form.get('token')

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
                token=token,
                status=status
            )
            flash('Точка сохранены', 'success')
            return redirect(request.path)

        return render_template('admin/outlet/edit.html', outlet=outlet, form=form)
    except Exception as err:
        session.rollback()
        logger.error(f'promo_azs \n\t{str(err)}')
        return str(err)


@admin.route('/promo/azs/<outlet_id>/delete', methods=['GET', 'POST'])
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs_delete(outlet_id):
    try:
        outlet = Outlet.query.get(outlet_id)
        form = forms.FormYes()
        if form.validate_on_submit():
            outlet.remove()
            return redirect(url_for('admin.promo_azs'))

        return render_template('admin/outlet/delete.html', outlet=outlet, form=form)
    except Exception as err:
        session.rollback()
        logger.error(f'promo_azs \n\t{str(err)}')
        return str(err)


@admin.route('/promo/products')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_products():
    try:
        product_list = session.query(Product)
        return render_template('admin/products/products.html', product_list=product_list)
    except Exception as err:
        session.rollback()
        return str(err)


@admin.route('/promo/products/create', methods=['GET', 'POST'])
@decorators.login_required
@decorators.role_required(role='admin')
def promo_products_new():
    try:

        form = forms.Product()

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
            product = Product.new(
                name=name,
                code=code,
                date_begin=date_begin,
                date_end=date_end,
                max_count=max_count,
                max_count_per_outlet=max_count_per_outlet,
                bar_code=bar_code,
                enabled=enabled
            )
            if product:
                return redirect(url_for('admin.promo_products'))

        return render_template('admin/products/new.html', form=form)
    except Exception as err:
        session.rollback()
        return str(err)


@admin.route('/promo/products/<product_id>/edit', methods=['GET', 'POST'])
@decorators.login_required
@decorators.role_required(role='admin')
def promo_products_edit(product_id):
    try:
        product = session.query(Product).get(product_id)

        form = forms.Product()

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
            return redirect(url_for('admin.promo_products'))

        return render_template('admin/products/edit.html', product=product, form=form)
    except Exception as err:
        session.rollback()
        return str(err)


@admin.route('/promo/products/<product_id>/delete', methods=['GET', 'POST'])
@decorators.login_required
@decorators.role_required(role='admin')
def promo_products_delete(product_id):
    try:
        product = session.query(Product).get(product_id)
        if not product:
            return render_template('404.html'), 404

        form = forms.FormYes()
        if form.validate_on_submit():
            product.remove()
            return redirect(url_for('admin.promo_products'))

        return render_template('admin/products/delete.html', product=product, form=form)
    except Exception as err:
        session.rollback()
        return str(err)


@admin.route('/promo/azs_products')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs_product():
    azs_product_list = database.select(
        """select p.name as product_name, a.name as azs_name, a.status, ar.token, ar.ts_create, ap.ts_usage from azs_product ap
join products p on ap.product_id = p.id
left join outlet_request ar on ap.outlet_request_id = ar.id
join azs a on ar.outlet_id = a.id""")
    return render_template('admin/azs_product.html', azs_product_list=azs_product_list)


@admin.route('/promo/azs_request')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs_request():
    azs_request = database.select(
        """select ar.token, a.name, a.ip, ar.ts_create, ar.ts_usage from azs_request ar
join azs a on a.id = ar.outlet_id
order by ar.ts_create desc""")
    return render_template('admin/azs_request.html', azs_request=azs_request)


@admin.route('/promo/azs_product_statistic')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_statistic_product():
    statistic_products = database.select(
        """select a.name as azs_name, 
p.name as product_name,
count(*) as count_products
from azs as a, products p,azs_request ar, azs_product ap
where p.id = ap.product_id
and ar.outlet_id = a.id
and ap.outlet_request_id = ar.id
group by a.name, p.name""")
    return render_template('admin/promo_statistic_products.html', statistic_products=statistic_products)


@admin.route('/manage/groups')
@decorators.login_required
@decorators.role_required(role='admin')
def manage_ads_group():
    group_list = GroupAdvertise.query
    return render_template('admin/manage_group_list.html', group_list=group_list)


@admin.route('/manage/advertise')
@decorators.login_required
@decorators.role_required(role='admin')
def manage_advertise():
    advertises = Advertise.query
    group_id = request.args.get('group_id')
    if group_id:
        advertises = advertises.filter_by(group_id=group_id)
    return render_template('admin/manage_advertise_list.html', advertises=advertises)
