from flask import Blueprint, jsonify, request
from app.auth import decorators, Auth
from app.promo.models import Product, Outlet, OutletProduct, OutletRequest, db
from sqlalchemy import and_, func
from app.manage.models import GroupAdvertise, Advertise
from app.auth.models import User
from datetime import datetime, timedelta
from src import formats
from .chart import Chart

data_app = Blueprint(
    'data',
    __name__
)


def render_json(result=True, data=None, status=200):
    return jsonify({
        'Result': result,
        'Data': data
    }), status


@data_app.route('/')
@decorators.login_required
def index():
    print(Auth.get_user())
    return 'data index'


def time_delta(var):
    res = timedelta(days=0)
    if var == '7d':
        res = timedelta(days=6)
    if var == '30d':
        res = timedelta(days=29)
    return res


def time_delta_period(date1: str, date2: str):
    d1 = datetime.strptime(date1, formats.DATE_JS)
    d2 = datetime.strptime(date2, formats.DATE_JS)
    day_list = []
    while d1 <= d2:
        day_list.append(d1)
        d1 = d1 + timedelta(days=1)
    return day_list


@data_app.route('/chart_product_created')
@decorators.login_required
def product_created():
    user = Auth.get_user()

    date1 = request.args.get('date1')
    date2 = request.args.get('date2')
    diapason = time_delta_period(date1, date2)
    labels = list(d.strftime(formats.DATE) for d in diapason)

    data = {
        'labels': labels,
        'datasets': []
    }
    products = user.products
    for (product, i) in zip(products, range(len(products))):
        product_period = {
            'label': product.name,
            'data': [],
            'index': i
        }
        for date in diapason:
            row = Product.get_create_product(product_id=product.id, date=date).all()
            product_period['data'].append(row[0][2] if len(row) else 0)
        data['datasets'].append(product_period)

    return render_json(True, {
        'type': 'stackedBar',
        'data': data
    })


@data_app.route('/chart_product_versus')
@decorators.login_required
def product_versus():
    user = Auth.get_user()

    chart = Chart()
    diapason = time_delta_period(chart.args.date1, chart.args.date2)

    products = user.products
    labels = list(product.name for product in products)

    products_data = list(
        product.in_the_period(chart.args.date1, chart.args.date2).count()
        for product in products
    )

    chart.labels = labels
    chart.add_data({
            'data': products_data,
            'index': list(range(len(products)))
        })

    data = chart.get_data()

    return render_json(True, {
        'type': 'pie',
        'data': data
    })


@data_app.route('/chart_product_by_status/<product_id>')
@decorators.login_required
def product_by_status(product_id):
    user = Auth.get_user()

    chart = Chart()
    diapason = time_delta_period(chart.args.date1, chart.args.date2)
    chart.labels = list(d.strftime(formats.DATE) for d in diapason)

    product = Product.query.filter_by(id=product_id, user_id=user.id).first()
    func = [
        {
            'action': lambda x: Product.get_create_product(product_id=product.id, date=x). \
                filter(OutletProduct.ts_usage == None).all(),
            'title': 'Показан QR-код'
        }, {
            'action': lambda x: Product.get_usage_product(product_id=product.id, date=x).all(),
            'title': 'Показан подарок'
        }
    ]

    for f, i in zip(func, range(len(func))):
        product_period = {
            'label': f['title'],
            'data': [],
            'index': i
        }

        for date in diapason:
            row = f['action'](date)

            product_period['data'].append(row[0][2] if len(row) else 0)
        chart.add_data(product_period)

    return render_json(True, {
        'type': 'stackedBar',
        'data': chart.get_data()
    })


@data_app.route('/product_by_status_all_period/<product_id>')
@decorators.login_required
def product_by_status_all_period(product_id):
    user = Auth.get_user()

    chart = Chart()
    diapason = time_delta_period(chart.args.date1, chart.args.date2)

    product = Product.query.filter_by(id=product_id, user_id=user.id).first()
    func = [
        {
            'action': lambda x: Product.get_create_product(product_id=product.id, date=x). \
                filter(OutletProduct.ts_usage == None).all(),
            'title': 'Показан QR-код'
        }, {
            'action': lambda x: Product.get_usage_product(product_id=product.id, date=x).all(),
            'title': 'Показан подарок'
        }
    ]
    chart.labels = list(f['title'] for f in func)
    product_period = {
        'label': chart.labels,
        'data': [],
        'index': list(range(len(func)))
    }

    for f, i in zip(func, range(len(func))):

        sum = 0
        for date in diapason:
            row = f['action'](date)
            sum += row[0][2] if len(row) else 0

        product_period['data'].append(sum)
    chart.add_data(product_period)

    return render_json(True, {
        'type': 'pie',
        'data': chart.get_data()
    })


@data_app.route('/advertise_clip_views_by_groups/')
@decorators.login_required
def advertise_clip_views_by_groups():
    user = Auth.get_user()

    date1 = request.args.get('date1')
    date2 = request.args.get('date2')
    diapason = time_delta_period(date1, date2)

    labels = list(d.strftime(formats.DATE) for d in diapason)

    data = {
        'labels': labels,
        'datasets': []
    }
    groups = GroupAdvertise.get_group_list(filters=[GroupAdvertise.Filters.actual]).filter_by(user_id=user.id)

    for group, i in zip(groups, range(groups.count())):
        product_period = {
            'label': group.title,
            'data': [],
            'index': i
        }

        for date in diapason:
            row = group.get_count_shows_per_day(day=date)

            product_period['data'].append(row)
        data['datasets'].append(product_period)

    return render_json(True, {
        'type': 'line',
        'data': data
    })


@data_app.route('/advertise_clip_views/<group_id>')
@decorators.login_required
def advertise_clip_views(group_id):
    chart = Chart()

    diapason = time_delta_period(chart.args.date1, chart.args.date2)

    chart.labels = list(d.strftime(formats.DATE) for d in diapason)

    advertise_list = Advertise.get_ads_list_by_group(group_id, [Advertise.Filters.actual])

    for ads, i in zip(advertise_list, range(advertise_list.count())):
        product_period = {
            'label': ads.title,
            'data': [],
            'index': i
        }

        for date in diapason:
            row = ads.get_count_shows_per_day(day=date).all()

            product_period['data'].append(len(row))
        chart.add_data(product_period)

    return render_json(True, {
        'type': 'line',
        'data': chart.get_data()
    })


@data_app.route('/outlet_promo_qr_views')
@decorators.login_required
def outlet_promo_qr_views():
    user = Auth.get_user()

    chart = Chart()

    diapason = time_delta_period(chart.args.date1, chart.args.date2)

    chart.labels = list(d.strftime(formats.DATE) for d in diapason)

    outlet_items = Outlet.query.filter_by(user_id=user.id)

    for outlet, i in zip(outlet_items, range(outlet_items.count())):
        product_period = {
            'label': outlet.name,
            'data': [],
            'index': i
        }

        for date in diapason:
            row = outlet.get_create_product(outlet_id=outlet.id, date=date).first()

            product_period['data'].append(row[1] if row else 0)
        chart.add_data(product_period)

    return render_json(True, {
        'type': 'stackedBar',
        'data': chart.get_data()
    })


@data_app.route('/outlet_promo_qr_views_by_outlet/<outlet_id>')
@decorators.login_required
def outlet_promo_qr_views_by_outlet(outlet_id):
    user = Auth.get_user()

    chart = Chart()

    diapason = time_delta_period(chart.args.date1, chart.args.date2)

    chart.labels = list(d.strftime(formats.DATE) for d in diapason)

    outlet = Outlet.query.filter_by(id=outlet_id, user_id=user.id).first()

    func = [
        {
            'action': lambda x: outlet.get_create_product(outlet_id=outlet.id, date=x). \
                filter(OutletProduct.ts_usage == None).first(),
            'label': 'Показ QR-кода (без подарка)'
        },
        {
            'action': lambda x: outlet.get_usage_product(outlet_id=outlet.id, date=x).first(),
            'label': 'Показ подарка'
        }
    ]

    for f, i in zip(func, range(len(func))):
        product_period = {
            'label': f['label'],
            'data': [],
            'index': i
        }

        for date in diapason:
            row = f['action'](date)

            product_period['data'].append(row[1] if row else 0)
        chart.add_data(product_period)

    return render_json(True, {
        'type': 'stackedBar',
        'data': chart.get_data()
    })


@data_app.route('/outlet_promo_qr_views_by_outlet_all/<outlet_id>')
@decorators.login_required
def outlet_promo_qr_views_by_outlet_all(outlet_id):
    user = Auth.get_user()

    chart = Chart()

    diapason = time_delta_period(chart.args.date1, chart.args.date2)

    chart.labels = list(d.strftime(formats.DATE) for d in diapason)

    outlet = Outlet.query.filter_by(id=outlet_id, user_id=user.id).first()

    func = [
        {
            'action': lambda x: outlet.get_create_product(outlet_id=outlet.id, date=x). \
                filter(OutletProduct.ts_usage == None).first(),
            'label': 'Показ QR-кода (без перехода к показу подарка)'
        },
        {
            'action': lambda x: outlet.get_usage_product(outlet_id=outlet.id, date=x).first(),
            'label': 'Показ подарка'
        }
    ]
    chart.labels = list(f['label'] for f in func)
    product_period = {
        'label': chart.labels,
        'data': [],
        'index': list(range(len(func)))
    }

    for f, i in zip(func, range(len(func))):
        sum = 0
        for date in diapason:
            row = f['action'](date)
            sum += row[1] if row else 0
        product_period['data'].append(sum)

    chart.add_data(product_period)

    return render_json(True, {
        'type': 'pie',
        'data': chart.get_data()
    })


@data_app.route('/promo_all/')
@decorators.login_required
def promo_all():
    user = Auth.get_user()

    chart = Chart()

    diapason = time_delta_period(chart.args.date1, chart.args.date2)

    chart.labels = list(d.strftime(formats.DATE) for d in diapason)

    chart.labels = ['Показан промо-ролик', 'Показан QR-код', 'Показан подарок', 'Получение подарка']
    product_period = {
        'label': [],
        'data': [],
        'index': [0, 1, 2, 3]
    }

    req_count = db.session.query(OutletRequest).join(Outlet, OutletRequest.outlet_id == Outlet.id) \
        .join(User, User.id == Outlet.user_id) \
        .filter(
        and_(User.id == user.id, OutletRequest.ts_usage != None, func.date(OutletRequest.ts_create) >= chart.args.date1,
             func.date(OutletRequest.ts_create) <= chart.args.date2))

    product_period['data'].append(req_count.count())

    req_code = req_count.join(OutletProduct, OutletProduct.outlet_request_id == OutletRequest.id)
    product_period['data'].append(req_code.count())

    req_shows = req_code.filter(OutletProduct.ts_usage != None)
    product_period['data'].append(req_shows.count())
    chart.add_data(product_period)

    product_period['data'].append(0)
    chart.add_data(product_period)

    data = chart.get_data()

    return render_json(True, {
        'type': 'funnel',
        'data': data,
        'options': {
            'title': {
                'display': True,
                'text': 'Воронка активности промо'
            },
            'sort': 'desc',
            'keep': 'auto'
        }
    })
