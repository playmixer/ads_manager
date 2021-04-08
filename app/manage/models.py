from src.database import db
from sqlalchemy import and_, or_
import datetime
import enum
from typing import List
from app.auth.models import User

__all__ = ['User', 'GroupAdvertise', 'Advertise', 'AdvertiseViewed']


class DateMixin:
    time_created = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)
    time_updated = db.Column(db.DATETIME, onupdate=datetime.datetime.utcnow)


def gen_token():
    from src.utils import generate_string
    return generate_string(50)


class GroupAdvertise(DateMixin, db.Model):
    class StatusType(enum.Enum):
        disabled = (0, "Не активно")
        enabled = (1, "Активно")

        def __init__(self, id, title):
            self.id = id
            self.title = title

        @classmethod
        def get(cls, id):
            return cls.enabled if id == 1 else cls.disabled

    class Filters:
        actual = 0

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    token = db.Column(db.String(200), unique=True, nullable=False, default=gen_token)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    status = db.Column(db.Enum(StatusType), default=StatusType.disabled, nullable=False)
    time_delete = db.Column(db.DATETIME)
    who_update = db.Column(db.Integer, db.ForeignKey(User.id))

    @classmethod
    def create(cls, title: str, user: User):
        group = GroupAdvertise(title=title, user_id=user.id)
        db.session.add(group)
        db.session.commit()
        return group

    @classmethod
    def delete(cls, id, user):
        group = GroupAdvertise.query.get(id)
        if group:
            group.time_delete = datetime.datetime.utcnow()
            group.who_update = user.id
            db.session.commit()
        return group

    @classmethod
    def update(cls, *, id, title, status, user):
        group = GroupAdvertise.query.get(id)
        if group:
            group.title = title
            group.who_update = user.id
            group.status = cls.StatusType.get(int(status))
            db.session.commit()
        return group

    @classmethod
    def get_group_list(cls, filters: List[int] = []):
        group_list = GroupAdvertise.query
        if cls.Filters.actual in filters:
            group_list = group_list.filter_by(time_delete=None)
        return group_list

    @classmethod
    def get_group(cls, group_id: int):
        return GroupAdvertise.query.get(group_id)

    @classmethod
    def get_group_by_token(cls, token: str):
        return cls.get_group_list().filter_by(token=token).first()


class Advertise(DateMixin, db.Model):
    class Filters:
        actual = 0

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    filename = db.Column(db.String(200), unique=True, nullable=False)
    file_extension = db.Column(db.String(20))
    group_id = db.Column(db.Integer, db.ForeignKey(GroupAdvertise.id), nullable=False)
    path = db.Column(db.String(200), unique=True, nullable=False)
    time_start = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)
    time_end = db.Column(db.DATETIME)
    time_delete = db.Column(db.DATETIME)
    who_create = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    who_update = db.Column(db.Integer, db.ForeignKey(User.id))

    @classmethod
    def get_ads_by_filename(cls, filename):
        return Advertise.query.filter_by(filename=filename).first()

    @classmethod
    def get_ads_list_by_group(cls, group_id: int, filters: List[int] = []):
        ads_list = Advertise.query.filter_by(group_id=group_id)
        if cls.Filters.actual in filters:
            ads_list = ads_list.filter_by(time_delete=None)

        return ads_list

    @classmethod
    def get_adss_by_group(cls, ads_id, filters: List[int] = []):
        ads = cls.query.filter_by(group_id=ads_id)
        if cls.Filters.actual in filters:
            date_now = datetime.datetime.utcnow()

            ads = ads.filter_by(time_delete=None).filter(
                or_(cls.time_end >= date_now, cls.time_end == None))
        return ads

    @classmethod
    def get_ads_by_group(cls, group_id, ads_id):
        return cls.get_ads_list_by_group(group_id).filter_by(id=ads_id).first()

    @classmethod
    def get_ads_by_group_token(cls, token: str, filters: List[int] = []):
        group = GroupAdvertise.get_group_list()
        if cls.Filters.actual in filters:
            group = group.filter_by(time_delete=None)
        group = group.filter_by(token=token).first()
        if group:
            return cls.get_adss_by_group(group.id, [cls.Filters.actual])
        return False

    @classmethod
    def create(cls, *, title, group_id, path, filename, ext, time_start, time_end, user):
        advertise = cls(
            title=title,
            group_id=group_id,
            path=path,
            filename=filename,
            file_extension=ext,
            time_start=time_start,
            time_end=time_end or None,
            who_create=user.id)
        db.session.add(advertise)
        db.session.commit()
        return advertise

    @classmethod
    def update(cls, *, id, title, time_start, time_end, user):
        ads = Advertise.query.get(id)
        if ads:
            ads.title = title
            ads.time_start = time_start
            ads.time_end = time_end or None
            ads.who_update = user.id
            db.session.commit()
        return ads

    @classmethod
    def delete(cls, *, id, user):
        ads = Advertise.query.get(id)
        if ads:
            ads.time_delete = datetime.datetime.utcnow()
            ads.who_update = user.id
            db.session.commit()
        return ads


class AdvertiseViewed(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    advertise_id = db.Column(db.Integer, db.ForeignKey(Advertise.id))
    date_viewed = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    device_id = db.Column(db.String(200))

    @classmethod
    def viewed(cls, filename, device_id=''):
        ads = Advertise.get_ads_by_filename(filename)
        if ads:
            view = cls(advertise_id=ads.id, device_id=device_id, date_viewed=datetime.datetime.utcnow())
            db.session.add(view)
            db.session.commit()
            return view
        return False

    @classmethod
    def get_between_date(cls, d1, d2):
        return cls.query.filter(and_(cls.date_viewed >= d1, cls.date_viewed <= d2))

    @classmethod
    def get_viewed_24h(cls):
        d2 = datetime.datetime.utcnow()
        d1 = d2 - datetime.timedelta(days=1)

        return cls.get_between_date(d1, d2)

    @classmethod
    def get_viewed_7d(cls):
        d2 = datetime.datetime.utcnow()
        d1 = d2 - datetime.timedelta(days=7)

        return cls.get_between_date(d1, d2)