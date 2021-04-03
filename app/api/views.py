from flask import Blueprint, request, redirect, url_for, make_response, send_file, jsonify
import os
from flask import current_app
from src import exceptions
from src.models import GroupAdvertise, Advertise

__all__ = ['api_app']

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
def index():
    return 'api'


@api_app.route('/getClip/<clip>')
def get_clip(clip: str):
    from src.utils import file_exists
    try:
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ads = Advertise.get_ads_by_filename(clip)
        if ads:
            if not file_exists(ads.path):
                raise exceptions.FileNotFound('File not found')
            path = os.path.join(UPLOAD_FOLDER, ads.path)

            response = make_response(send_file(path, attachment_filename="video.mp4", conditional=True))
            response.headers['Content-Type'] = 'video/mp4'
            return response

        return render_json(result=False, message='File not found')
    except exceptions.FileNotFound as err:
        return str(err), 404
    except Exception as err:
        return str(err)


@api_app.route('/getAdsGroup')
def get_ads_group():
    token = request.args.get('ads_token')
    print(token)
    return render_json(result=False, data=None)


@api_app.route('/adsViewed/<filename>')
def clip_viewed(filename):
    ...
