from flask import Blueprint, render_template, redirect, url_for, request
from app.auth import decorators
from .promo import database
from app.manage.models import *
from src.logger import logger

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
        azs_list = database.select('select name, num, lat, lon, ip, token, status, ts_create, ts_update from azs')
        return render_template('admin/azs.html', azs_list=azs_list)
    except Exception as err:
        logger.error(f'promo_azs \n\t{str(err)}')
        return str(err)


@admin.route('/promo/products')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_products():
    product_list = database.select(
        'select name, code, date_begin, date_end, max_count, max_count_per_azs, bar_code, enabled from products')
    return render_template('admin/products.html', product_list=product_list)


@admin.route('/promo/azs_products')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs_product():
    azs_product_list = database.select(
        """select p.name as product_name, a.name as azs_name, a.status, ar.token, ar.ts_create, ar.ts_usage from azs_product ap
join products p on ap.product_id = p.id
left join azs_request ar on ap.azs_request_id = ar.id
join azs a on ar.azs_id = a.id""")
    return render_template('admin/azs_product.html', azs_product_list=azs_product_list)


@admin.route('/promo/azs_request')
@decorators.login_required
@decorators.role_required(role='admin')
def promo_azs_request():
    azs_request = database.select(
        """select ar.token, a.name, a.ip, ar.ts_create, ar.ts_usage from azs_request ar
join azs a on a.id = ar.azs_id
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
and ar.azs_id = a.id
and ap.azs_request_id = ar.id
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
