from flask import Blueprint, render_template, flash, request, redirect, url_for, make_response, send_file
from .forms import *
from app.auth import decorators
from app.auth.auth import Auth
from app.manage.models import GroupAdvertise, Advertise, AdvertiseViewed, db
from src import exceptions
from src.logger import logger
import os
from app.auth.utils import get_token_from_header

__all__ = ['manage_app']

manage_app = Blueprint(
    'manage',
    __name__,
    template_folder='templates'
)


@manage_app.route('/test', methods=['GET', 'POST'])
@decorators.login_required
def test():
    print(Auth.find_role(role_str='admin'))

    return '123'


@manage_app.route('/', methods=['GET', 'POST'])
@decorators.login_required
def index():
    return redirect(url_for('.ads_groups'))


@manage_app.route('/adsGroup', methods=['GET', 'POST'])
@decorators.login_required
def ads_groups():
    try:
        user = Auth.get_user()
        form = FormNewGroup()
        if form.validate_on_submit():
            group_title = request.form.get('title')
            GroupAdvertise.create(group_title, user)

        adv_group_list = GroupAdvertise.get_group_list(filters=[GroupAdvertise.Filters.actual]).filter_by(
            user_id=user.id)
        return render_template('manage/ads_group_list.html', form=form, group_list=adv_group_list,
                               ads_viewed=AdvertiseViewed)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>', methods=['GET', 'POST'])
@decorators.login_required
def ads_group(group_id):
    try:
        user = Auth.get_user()
        group = GroupAdvertise.get_group(group_id).filter_by(user_id=user.id).first()

        if not group:
            raise Exception('Advertise group not found')
        ads_list = Advertise.get_ads_list_by_group(group_id, [Advertise.Filters.actual])

        return render_template('manage/ads_group.html', ads_list=ads_list, ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>/edit', methods=['GET', 'POST'])
@decorators.login_required
def ads_group_edit(group_id):
    try:
        group = GroupAdvertise.get_group(group_id).filter_by(user_id=Auth.get_user().id).first()
        if not group:
            raise Exception('Advertise group not found')

        form = FormEditGroup()
        form.status.choices = [(group.id, group.title) for group in GroupAdvertise.StatusType]
        if form.validate_on_submit():
            title = request.form.get('title')
            status = request.form.get('status')
            GroupAdvertise.update(
                id=group.id,
                title=title,
                status=status,
                user=Auth.get_user()
            )
            flash('Изменения сохранены', 'success')
            return redirect(request.path)

        return render_template('manage/ads_group_edit.html', form=form, ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>/delete', methods=['GET', 'POST'])
@decorators.login_required
def ads_group_delete(group_id):
    try:
        user = Auth.get_user()
        group = GroupAdvertise.get_group(group_id).filter_by(user_id=user.id).first()
        if not group:
            raise Exception('Advertise group not found')

        form_yes = FormYes()
        if form_yes.validate_on_submit():
            GroupAdvertise.delete(group.id, Auth.get_user())
            return redirect(url_for('.ads_groups'))

        return render_template('manage/ads_group_delete.html', form=form_yes, ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>/create_advertise', methods=['GET', 'POST'])
@decorators.login_required
def ads_new(group_id):
    from src.utils import save_file
    try:
        group = GroupAdvertise.get_group(group_id).first()
        if not group:
            raise Exception('Advertise group not found')

        form = FormNewAdvertise()
        if form.validate_on_submit():
            if 'file' not in request.files:
                flash('Нет файловой части', 'error')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)

            path, filename, ext = save_file(file)

            title = request.form.get('title')
            shows_per_day = request.form.get('shows_per_day')
            time_start = request.form.get('time_start')
            time_end = request.form.get('time_end')
            ads_ = Advertise.create(
                title=title,
                group_id=group_id,
                path=path,
                filename=filename,
                shows_per_day=shows_per_day,
                ext=ext,
                time_start=time_start,
                time_end=time_end,
                user=Auth.get_user()
            )
            if ads_:
                return redirect(url_for('.ads_view', group_id=group_id, ads_id=ads_.id))

        return render_template('manage/ads_new.html', form=form, ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>/advertise/<ads_id>', methods=['GET', 'POST'])
@decorators.login_required
def ads_view(group_id, ads_id):
    try:
        group = GroupAdvertise.get_group(group_id).filter_by(user_id=Auth.get_user().id).first()
        if not group:
            raise Exception('Advertise group not found')
        ads_item = Advertise.get_ads_by_group(group_id, ads_id)
        if not ads_item:
            raise Exception('Advertise not found')

        form = FormEditAdvertise()
        if form.validate_on_submit():
            Advertise.update(
                id=ads_item.id,
                title=request.form.get('title'),
                shows_per_day=request.form.get('shows_per_day'),
                time_start=request.form.get('time_start'),
                time_end=request.form.get('time_end'),
                user=Auth.get_user()
            )
            flash('Изменения сохранены', 'success')
            return redirect(request.path)

        return render_template('manage/ads.html', form=form, ads_item=ads_item, ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>/advertise/<ads_id>/delete', methods=['GET', 'POST'])
@decorators.login_required
def ads_delete(group_id, ads_id):
    try:
        group = GroupAdvertise.get_group(group_id).first()
        if not group:
            raise Exception('Advertise group not found')
        ads_item = Advertise.get_ads_by_group(group_id, ads_id)
        if not ads_item:
            raise Exception('Advertise not found')

        form_yes = FormYes()
        if form_yes.validate_on_submit():
            from src.utils import remove_file
            ads = Advertise.delete(id=ads_item.id, user=Auth.get_user())
            remove_file(ads.path)
            return redirect(url_for('.ads_group', group_id=group_id))

        return render_template('manage/ads_delete.html', form=form_yes, ads_item=ads_item, ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/getClip/<filename>')
# @decorators.authenticated_required
def get_clip(filename: str):
    from src.utils import file_exists
    from flask import current_app
    try:
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ads = Advertise.get_ads_by_filename(filename)
        if not ads:
            raise exceptions.AdvertiseNotFound('Advertise not found')

        if not file_exists(ads.get_path()):
            raise exceptions.FileNotFound('File not found')

        path = os.path.join(UPLOAD_FOLDER, ads.get_path())

        response = make_response(send_file(path, conditional=True))

        if response.status_code == 200:
            token = get_token_from_header()
            if token:
                payload = Auth.get_jwt_payload(token)
                device_id = payload['device_id']

                AdvertiseViewed.viewed(filename, device_id)

        return response

    except (exceptions.FileNotFound, exceptions.AdvertiseNotFound) as err:
        return str(err), 404
    except Exception as err:
        logger.error('get_clip filename=' + filename + '\n\t' + str(err))
        return str(err), 500
