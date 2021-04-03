from src.database import db
import datetime
import enum

__all__ = ['User', 'GroupAdvertise', 'Advertise', 'AdvertiseViewed']


class DateMixin:
    time_created = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)
    time_updated = db.Column(db.DATETIME, onupdate=datetime.datetime.utcnow)


class User(DateMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), unique=True, nullable=False)


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
    token = db.Column(db.String(200))
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
    def get_group_list(cls, filters=[]):
        group_list = GroupAdvertise.query
        if cls.Filters.actual in filters:
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
            if time_end:
                ads.time_end = time_end
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


class AdvertiseViewed(DateMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    advertise_id = db.Column(db.Integer, db.ForeignKey(Advertise.id))
    count = db.Column(db.Integer, default=0)
    date_viewed = db.Column(db.DATE)
