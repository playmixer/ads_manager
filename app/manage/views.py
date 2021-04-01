from flask import Blueprint, render_template, flash, request, redirect, url_for
from .forms import *
from app.auth import Auth, decorators
from src.models import GroupAdvertise, Advertise

__all__ = ['manage_app']

manage_app = Blueprint(
    'manage',
    __name__,
    template_folder='templates'
)


@manage_app.route('/', methods=['GET', 'POST'])
@decorators.login_required
def index():
    return redirect(url_for('.ads_groups'))


@manage_app.route('/adsGroup', methods=['GET', 'POST'])
@decorators.login_required
def ads_groups():
    try:
        form = FormNewGroup()
        if form.validate_on_submit():
            auth = Auth()
            user = auth.get_user()
            group_title = request.form.get('title')
            GroupAdvertise.create(group_title, user)

        adv_group_list = GroupAdvertise.get_group_list(filter=[GroupAdvertise.Filters.actual])
        return render_template('manage/ads_group_list.html', form=form, group_list=adv_group_list)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>/edit', methods=['GET', 'POST'])
@decorators.login_required
def ads_group_edit(group_id):
    group = GroupAdvertise.get_group(group_id)
    try:
        return render_template('manage/ads_group_edit.html', ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>', methods=['GET', 'POST'])
@decorators.login_required
def ads_group(group_id):
    try:
        group = GroupAdvertise.get_group(group_id)
        if not group:
            raise Exception('Advertise group not found')
        ads_list = Advertise.get_ads_list_by_group(group_id, [Advertise.Filters.actual])

        return render_template('manage/ads_group.html', ads_list=ads_list, ads_group=group)
    except Exception as err:
        return str(err)


@manage_app.route('/adsGroup/<group_id>/create_advertise', methods=['GET', 'POST'])
@decorators.login_required
def ads_new(group_id):
    from src.utils import save_file
    try:
        group = GroupAdvertise.get_group(group_id)
        if not group:
            raise Exception('Advertise group not found')

        form = FormNewAdvertise()
        if form.validate_on_submit():
            if 'file' not in request.files:
                flash('Нет файловой части')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            path, filename, ext = save_file(file)

            title = request.form.get('title')
            time_start = request.form.get('time_start')
            time_end = request.form.get('time_end')
            ads_ = Advertise.create(
                title=title,
                group_id=group_id,
                path=path,
                filename=filename,
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
        group = GroupAdvertise.get_group(group_id)
        if not group:
            raise Exception('Advertise group not found')
        ads_item = Advertise.get_ads_by_group(group_id, ads_id)
        if not ads_item:
            raise Exception('Advertise not found')

        return render_template('manage/ads.html', ads_item=ads_item, ads_group=group)
    except Exception as err:
        return str(err)
