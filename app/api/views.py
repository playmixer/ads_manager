from flask import Blueprint, request, redirect, url_for, make_response, send_file, jsonify
from app.manage.models import GroupAdvertise, Advertise, AdvertiseViewed
from app.promo.models import Outlet, db
from . import types
from app.auth import decorators
from src.logger import logger
from app.auth.auth import Auth
from app.auth.utils import get_token_from_header

__all__ = ['api_app', 'render_json']

api_app = Blueprint(
    'api',
    __name__,
    template_folder='templates'
)


def render_json(*, result=True, data=None, message=None, status=200):
    res = {
        'Result': 'Ok' if result else 'Fail'
    }
    if data is not None:
        res['Data'] = data
    if message:
        res['Message'] = message

    return jsonify(res), status


@api_app.route('/')
def test():
    return render_json(result=True)


@api_app.route('/getGroups')
@decorators.authenticated_required
def get_groups():
    try:
        payload = Auth.get_jwt_payload()
        user_id = payload.get('user_id')
        outlet_id = payload.get('outlet_id')
        outlet = Outlet.query.get(outlet_id)

        groups = GroupAdvertise.get_group_list(
            filters=[GroupAdvertise.Filters.actual, GroupAdvertise.Filters.enabled]).filter_by(user_id=user_id)
        groups_filtered = list(filter(lambda x: outlet in x.outlets, groups))
        parsed_groups = types.TypeGroupsAdvertise.parse_obj(groups_filtered)

        return render_json(result=True, data=parsed_groups.dict()["__root__"])
    except Exception as err:
        logger.error('get_group \n\t' + str(err))
        render_json(result=False)


@api_app.route('/getAdsGroup')
@decorators.authenticated_required
def get_ads_group():
    try:
        payload = Auth.get_jwt_payload()
        outlet_id = payload.get('outlet_id')
        user_id = payload.get('user_id')
        outlet = Outlet.query.filter_by(id=outlet_id, user_id=user_id).first()

        if not outlet:
            return render_json(result=False, message="Outlet not found")

        ads = outlet.get_advertise()
        if not ads:
            # raise Exception('Advertise not found')
            return render_json(result=True, data=[])

        ads_filtered = list(filter(lambda x: x.have_shows_max(), ads))
        ads_filtered = list(filter(lambda x: x.have_shows_per_day(), ads_filtered))
        parsed_ads = types.TypeAdvertiseList.from_orm(ads_filtered)
        return render_json(result=True, data=parsed_ads.dict()['__root__'])

    except Exception as err:
        logger.error('get_ads_group \n\t' + str(err))
        return render_json(result=False, message=str(err))


@api_app.route('/adsViewed/<filename>')
@decorators.authenticated_required
def clip_viewed(filename):
    token = get_token_from_header()
    if token:
        payload = Auth.get_jwt_payload(token)
        device_id = payload['device_id']

    view = AdvertiseViewed.viewed(filename, device_id)
    if view:
        return render_json(result=True)

    return render_json(result=False, message='Can`t viewed')


@api_app.route('/adsViews', methods=['POST'])
@decorators.authenticated_required
def clips_views():
    try:
        token = get_token_from_header()
        if token:
            payload = Auth.get_jwt_payload(token)
            device_id = payload['device_id']

        json = request.get_json()
        print(json)
        for item in json.items():
            filename = item[0]
            count = item[1].get('count') or 0
            for i in range(count):
                AdvertiseViewed.viewed(filename, device_id, commit=False)

        db.session.commit()
        return render_json(result=True)

    except Exception as err:
        return render_json(result=False, message='Can`t viewed')
