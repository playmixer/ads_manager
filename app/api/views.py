from flask import Blueprint, request, redirect, url_for, make_response, send_file, jsonify
from app.manage.models import GroupAdvertise, Advertise, AdvertiseViewed
from . import types

__all__ = ['api_app', 'render_json']

api_app = Blueprint(
    'api',
    __name__,
    template_folder='templates'
)


def render_json(*, result=True, data=None, message=None):
    res = {
        'Result': 'Ok' if result else 'Fail'
    }
    if data:
        res['Data'] = data
    if message:
        res['Message'] = message

    return jsonify(res)


@api_app.route('/')
def test():
    return render_json(result=True)


@api_app.route('/getGroups')
def get_groups():
    groups = GroupAdvertise.get_group_list([GroupAdvertise.Filters.actual])
    parsed_groups = types.TypeGroupsAdvertise.parse_obj(groups.all())

    return render_json(result=True, data=parsed_groups.dict()["__root__"])


@api_app.route('/getAdsGroup')
def get_ads_group():
    try:
        token = request.args.get('ads_token')
        if not token:
            raise Exception('Token is missed')

        ads = Advertise.get_ads_by_group_token(token)
        if not ads:
            raise Exception('Advertise not found')

        parsed_ads = types.TypeAdvertiseList.from_orm(ads.all())
        return render_json(result=True, data=parsed_ads.dict()['__root__'])

    except Exception as err:
        return render_json(result=False, message=str(err))


@api_app.route('/adsViewed/<filename>')
def clip_viewed(filename):
    view = AdvertiseViewed.viewed(filename)
    if view:
        return render_json(result=True)

    return render_json(result=False, message='Can`t viewed')
