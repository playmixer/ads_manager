from src.database import db
import datetime

__all__ = ['User', 'GroupAdvertise', 'Advertise', 'AdvertiseViewed']


class DateMixin:
    time_created = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)
    time_updated = db.Column(db.DATETIME, onupdate=datetime.datetime.utcnow)


class User(DateMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), unique=True, nullable=False)


class GroupAdvertise(DateMixin, db.Model):
    class Filters:
        actual = 0

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    time_delete = db.Column(db.DATETIME)

    @classmethod
    def create(cls, title: str, user: User):
        group = GroupAdvertise(title=title, user_id=user.id)
        db.session.add(group)
        db.session.commit()
        return group

    @classmethod
    def get_group_list(cls, filter=[]):
        group_list = GroupAdvertise.query
        if cls.Filters.actual in filter:
            group_list = group_list.filter_by(time_delete=None)
        return group_list.all()

    @classmethod
    def get_group(cls, group_id: int):
        return GroupAdvertise.query.get(group_id)


class Advertise(DateMixin, db.Model):
    class Filters:
        actual = 0

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200))
    filename = db.Column(db.String(200))
    file_extension = db.Column(db.String(20))
    group_id = db.Column(db.Integer, db.ForeignKey(GroupAdvertise.id), nullable=False)
    path = db.Column(db.String(200), unique=True, nullable=False)
    time_start = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)
    time_end = db.Column(db.DATETIME)
    time_delete = db.Column(db.DATETIME)
    who_create = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    who_update = db.Column(db.Integer, db.ForeignKey(User.id))

    @classmethod
    def get_ads_list_by_group(cls, group_id: int, filters=[]):
        ads_list = Advertise.query.filter_by(group_id=group_id)
        if cls.Filters.actual in filters:
            ads_list = ads_list.filter_by(time_delete=None)

        return ads_list

    @classmethod
    def get_ads(cls, ads_id):
        return Advertise.query.get(ads_id)

    @classmethod
    def get_ads_by_group(cls, group_id, ads_id):
        return cls.get_ads_list_by_group(group_id).filter_by(id=ads_id).first()

    @classmethod
    def create(cls, *, title, group_id, path, filename, ext, time_start, time_end, user):
        advertise = cls(title=title, group_id=group_id, path=path, filename=filename, file_extension=ext,
                        time_start=time_start, time_end=time_end,
                        who_create=user.id)
        db.session.add(advertise)
        db.session.commit()
        return advertise


class AdvertiseViewed(DateMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    advertise_id = db.Column(db.Integer, db.ForeignKey(Advertise.id))
    count = db.Column(db.Integer, default=0)
    date_viewed = db.Column(db.DATE)
