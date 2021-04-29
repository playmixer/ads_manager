from flask import Blueprint, jsonify, request
from app.auth import decorators, Auth
from app.promo.models import Product, Outlet
from datetime import datetime, timedelta
from src import formats

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
    res = timedelta(days=1)
    if var == '7d':
        res = timedelta(days=7)
    if var == '30d':
        res = timedelta(days=30)
    return res


@data_app.route('/chart_product_created')
@decorators.login_required
def product_created():
    user = Auth.get_user()

    period = request.args.get('period')
    date_delta = time_delta(period)

    labels = list((datetime.now() - timedelta(days=i)).strftime(formats.DATE) for i in range(date_delta.days)[::-1])

    data = {
        'labels': labels,
        'datasets': []
    }
    products = user.products
    for (product, i) in zip(products, range(len(products))):
        date_min = datetime.utcnow() - date_delta
        date_now = datetime.utcnow()
        product_period = {
            'label': product.name,
            'data': [],
            'index': i
        }
        while date_min <= date_now:
            row = Product.get_create_product(product_id=product.id, date=date_min).all()
            product_period['data'].append(row[0][2] if len(row) else 0)
            date_min += timedelta(1)
        data['datasets'].append(product_period)

    return render_json(True, {
        'type': 'bar',
        'data': data
    })


@data_app.route('/chart_product_versus')
@decorators.login_required
def product_versus():
    user = Auth.get_user()

    period = request.args.get('period')
    date_delta = time_delta(period)
    date_now = datetime.utcnow()
    date_min = date_now - date_delta

    products = user.products
    labels = list(product.name for product in products)

    products_data = list(
        product.in_the_period(date_min, date_now).count()
        for product in products
    )

    data = {
        'labels': labels,
        'datasets': [{
            'data': products_data,
            'index': list(range(len(products)))
        }]
    }

    return render_json(True, {
        'type': 'pie',
        'data': data
    })


@data_app.route('/chart_product_by_status/<product_id>')
@decorators.login_required
def product_by_status(product_id):
    user = Auth.get_user()

    period = request.args.get('period')
    date_delta = time_delta(period)

    labels = list((datetime.now() - timedelta(days=i)).strftime(formats.DATE) for i in range(date_delta.days)[::-1])

    data = {
        'labels': labels,
        'datasets': []
    }
    product = Product.query.filter_by(id=product_id, user_id=user.id).first()
    func = [
        {
            'action': Product.get_showes_poduct,
            'title': 'Показов'
        },
        {
            'action': Product.get_create_product,
            'title': 'Разыграно'
        }, {
            'action': Product.get_usage_product,
            'title': 'Активировано'
        }
    ]

    date_now = datetime.utcnow()
    for f, i in zip(func, range(len(func))):
        date_min = datetime.utcnow() - date_delta
        product_period = {
            'label': f['title'],
            'data': [],
            'index': i
        }

        while date_min <= date_now:
            row = f['action'](product_id=product.id, date=date_min).all()

            product_period['data'].append(row[0][2] if len(row) else 0)
            date_min += timedelta(1)
        data['datasets'].append(product_period)

    return render_json(True, {
        'type': 'bar',
        'data': data
    })
