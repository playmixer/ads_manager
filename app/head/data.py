from app.auth import Auth
from datetime import datetime, timedelta
from app.manage.models import AdvertiseViewed, GroupAdvertise, Advertise, db
from app.auth.models import User


def get_viewed_7d():
    user = Auth.get_user()
    date2 = datetime.utcnow()
    date1 = date2 - timedelta(days=6)

    views = AdvertiseViewed.get_between_date(date1, date2) \
        .join(User, User.id == GroupAdvertise.user_id == user.id)

    return views.count()


def get_viewed_30d():
    user = Auth.get_user()
    date2 = datetime.utcnow()
    date1 = date2 - timedelta(days=29)

    views = AdvertiseViewed.get_between_date(date1, date2) \
        .join(User, User.id == GroupAdvertise.user_id == user.id)

    return views.count()


def get_viewed_all():
    user = Auth.get_user()
    views = db.session.query(AdvertiseViewed).join(Advertise).join(GroupAdvertise) \
        .join(User, User.id == GroupAdvertise.user_id == user.id)

    return views.count()
