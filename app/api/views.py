from flask import Blueprint, request, redirect, url_for, make_response, send_file, jsonify
from app.manage.models import GroupAdvertise, Advertise, AdvertiseViewed
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

    return jsonify(res), 200


@api_app.route('/')
def test():
    return render_json(result=True)


@api_app.route('/getGroups')
@decorators.authenticated_required
def get_groups():
    try:
        payload = Auth.get_jwt_payload()
        user_id = payload.get('user_id')

        groups = GroupAdvertise.get_group_list(
            [GroupAdvertise.Filters.actual, GroupAdvertise.Filters.enabled]).filter_by(user_id=user_id)
        parsed_groups = types.TypeGroupsAdvertise.parse_obj(groups.all())

        return render_json(result=True, data=parsed_groups.dict()["__root__"])
    except Exception as err:
        logger.error('get_group \n\t' + str(err))
        render_json(result=False)


@api_app.route('/getAdsGroup')
@decorators.authenticated_required
def get_ads_group():
    try:
        token = request.args.get('ads_token')
        if not token:
            raise Exception('Token is missed')

        ads = Advertise.get_ads_by_group_token(token)
        if not ads:
            # raise Exception('Advertise not found')
            return render_json(result=True, data=[])

        ads_filtered = list(filter(lambda x: x.have_shows_max(), ads.all()))
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
