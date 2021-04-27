from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, SmallInteger, func, and_
from sqlalchemy.orm import relationship, backref
from src.database import db
from datetime import datetime
from app.auth.models import User
from app.manage.models import GroupAdvertise


class Outlet(db.Model):
    __tablename__ = 'outlet'
    choices_status = [(1, 'Активный'), (0, 'Отключен')]

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    num = Column(Integer)
    lat = Column(Float)
    lon = Column(Float)
    ip = Column(String(20))
    token = Column(String(50), unique=True)
    status = Column(Integer)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, backref='outlet')
    ts_create = Column(TIMESTAMP, default=datetime.now)
    ts_update = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def new(cls, *, name, num=1, lat, lon, ip, token=None, status, user):
        from src import utils
        outlet = cls(
            name=name,
            num=num,
            lat=lat,
            lon=lon,
            ip=ip,
            token=token or utils.generate_string(20),
            status=status,
            user_id=user.id
        )
        db.session.add(outlet)
        db.session.commit()
        return outlet

    def update(self, *, name, num=1, lat, lon, ip, token=None, status):
        self.name = name
        self.num = num
        self.lat = lat
        self.lon = lon
        self.ip = ip
        if token:
            self.token = token
        self.status = status
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_create_product(cls, *, outlet_id=None, date=None):
        from datetime import datetime, timedelta
        res = db.session.query(func.date(OutletProduct.ts_create), func.count(OutletProduct.ts_create)). \
            join(OutletRequest).join(Outlet). \
            group_by(Outlet.name, func.date(OutletProduct.ts_create)). \
            filter(and_(OutletProduct.ts_create >= (datetime.now() - timedelta(days=7))))

        if outlet_id:
            res = res.filter(Outlet.id == outlet_id)

        if date:
            d1 = date.replace(hour=0, minute=0, second=0)
            d2 = date.replace(hour=23, minute=59, second=59)
            res = res.filter(and_(OutletProduct.ts_create >= d1, OutletProduct.ts_create <= d2))

        return res

    @classmethod
    def get_usage_product(cls, *, outlet_id=None, date=None):
        res = cls.get_create_product(outlet_id=outlet_id, date=date).filter(
            OutletProduct.ts_usage >= OutletProduct.ts_create)

        return res


class OutletAdsGroup(db.Model):
    __tablename__ = 'outlet_group_advertise'

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey(Outlet.id, ondelete='CASCADE'), nullable=False)
    outlet = relationship(Outlet, backref='group')
    group_id = Column(Integer, ForeignKey(GroupAdvertise.id, ondelete='CASCADE'), nullable=False)
    group = relationship(GroupAdvertise, backref='outlet')


class Product(db.Model):
    __tablename__ = 'products'
    choices_enabled = [(1, 'Активный'), (0, 'Отключен')]

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(String(50))
    date_begin = Column(TIMESTAMP, default=datetime.now)
    date_end = Column(TIMESTAMP, default=datetime.now)
    max_count = Column(Integer, default=0)
    max_count_per_outlet = Column(Integer, default=0)
    bar_code = Column(String(50))
    enabled = Column(SmallInteger, default=1)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))
    user = relationship(User, backref='products')

    def update(self, *, name, code, date_begin, date_end, max_count, max_count_per_outlet, bar_code, enabled):
        self.name = name
        self.code = code
        self.date_begin = date_begin
        self.date_end = date_end
        self.max_count = max_count or 0
        self.max_count_per_outlet = max_count_per_outlet or 0
        self.bar_code = bar_code or 0
        self.enabled = enabled or 0
        db.session.commit()
        return self

    @classmethod
    def new(cls, *, name, code, date_begin, date_end, max_count, max_count_per_outlet, bar_code, enabled, user):
        product = cls(
            name=name,
            code=code,
            date_begin=date_begin,
            date_end=date_end,
            max_count=max_count,
            max_count_per_outlet=max_count_per_outlet,
            bar_code=bar_code,
            enabled=enabled,
            user_id=user.id
        )
        db.session.add(product)
        db.session.commit()
        return product

    def remove(self):
        db.session.delete(self)
        if db.session.commit():
            return True
        return False

    @classmethod
    def get_create_product(cls, *, product_id=None, date=None):
        from datetime import datetime, timedelta
        res = db.session.query(OutletProduct.product_id, func.date(OutletProduct.ts_create),
                               func.count(OutletProduct.ts_create)). \
            join(OutletRequest).join(Product). \
            group_by(Product.name, func.date(OutletProduct.ts_create)). \
            filter(and_(OutletProduct.ts_create >= (datetime.now() - timedelta(days=7))))

        if product_id:
            res = res.filter(Product.id == product_id)

        if date:
            d1 = date.replace(hour=0, minute=0, second=0)
            d2 = date.replace(hour=23, minute=59, second=59)
            res = res.filter(and_(OutletProduct.ts_create >= d1, OutletProduct.ts_create <= d2))

        return res

    @classmethod
    def get_showes_poduct(cls, *, product_id=None, date=None):
        from datetime import datetime, timedelta
        res = db.session.query(OutletProduct.product_id, func.date(OutletRequest.ts_usage),
                               func.count(OutletRequest.ts_usage)). \
            join(OutletRequest).join(Product). \
            group_by(OutletProduct.product_id, func.date(OutletRequest.ts_usage)). \
            filter(and_(OutletRequest.ts_usage >= (datetime.now() - timedelta(days=7))))

        if product_id:
            res = res.filter(Product.id == product_id)

        if date:
            d1 = date.replace(hour=0, minute=0, second=0)
            d2 = date.replace(hour=23, minute=59, second=59)
            res = res.filter(and_(OutletProduct.ts_create >= d1, OutletProduct.ts_create <= d2))

        return res

    @classmethod
    def get_usage_product(cls, *, product_id=None, date=None):
        res = cls.get_create_product(product_id=product_id, date=date).filter(
            OutletProduct.ts_usage >= OutletProduct.ts_create)

        return res


class OutletRequest(db.Model):
    __tablename__ = 'outlet_request'

    id = Column(Integer, primary_key=True)
    token = Column(String(50))
    outlet_id = Column(Integer, ForeignKey(Outlet.id), nullable=False)
    outlet = relationship(Outlet, backref='requests')
    outlet_ip = Column(String(50))
    ts_create = Column(TIMESTAMP, nullable=False, default=datetime.now)
    ts_usage = Column(TIMESTAMP, nullable=True)


class OutletProduct(db.Model):
    __tablename__ = 'outlet_product'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id))
    product = relationship(Product, backref='outlet')
    outlet_request_id = Column(Integer, ForeignKey(OutletRequest.id))
    outlet_request = relationship(OutletRequest, backref='outlet_request')
    ts_create = Column(TIMESTAMP, nullable=False, default=datetime.now)
    ts_usage = Column(TIMESTAMP, nullable=True)


class OutletMac(db.Model):
    __tablename__ = 'outlet_mac'

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey(Outlet.id))
    mac = Column(String(32))
    ts_first_seen = Column(TIMESTAMP, nullable=False, default=datetime.now)
    ts_last_seen = Column(TIMESTAMP, nullable=False, default=datetime.now, onupdate=datetime.now)
