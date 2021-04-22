from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, SmallInteger, func, and_
from sqlalchemy.orm import relationship
from .database import Base, session, insert
from datetime import datetime


class Azs(Base):
    __tablename__ = 'azs'
    choices_status = [(1, 'Активный'), (0, 'Отключен')]

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    num = Column(Integer)
    lat = Column(Float)
    lon = Column(Float)
    ip = Column(String(20))
    token = Column(String(50), unique=True)
    status = Column(Integer)
    ts_create = Column(TIMESTAMP, default=datetime.now)
    ts_update = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def new(cls, *, name, num=1, lat, lon, ip, token=None, status):
        from src import utils
        azs = cls(
            name=name,
            num=num,
            lat=lat,
            lon=lon,
            ip=ip,
            token=token or utils.generate_string(20),
            status=status
        )
        insert(azs)
        return azs

    def update(self, *, name, num=1, lat, lon, ip, token=None, status):
        self.name = name
        self.num = num
        self.lat = lat
        self.lon = lon
        self.ip = ip
        if token:
            self.token = token
        self.status = status
        session.commit()

    def remove(self):
        session.delete(self)
        session.commit()

    @classmethod
    def get_create_product(cls, azs_id, date=None):
        from datetime import datetime, timedelta
        res = session.query(func.date(AzsProduct.ts_create), func.count(AzsProduct.ts_create)). \
            join(AzsRequest).join(Azs). \
            group_by(Azs.name, func.date(AzsProduct.ts_create)). \
            filter(and_(Azs.id == azs_id, AzsProduct.ts_create >= (datetime.now() - timedelta(days=7))))

        if date:
            d1 = date.replace(hour=0, minute=0, second=0)
            d2 = date.replace(hour=23, minute=59, second=59)
            res = res.filter(and_(AzsProduct.ts_create >= d1, AzsProduct.ts_create <= d2))

        return res

    @classmethod
    def get_usage_product(cls, azs_id, date=None):
        res = cls.get_create_product(azs_id, date).filter(AzsProduct.ts_usage >= AzsProduct.ts_create)

        return res


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(String(50))
    date_begin = Column(TIMESTAMP, default=datetime.now)
    date_end = Column(TIMESTAMP, default=datetime.now)
    max_count = Column(Integer, default=0)
    max_count_per_azs = Column(Integer, default=0)
    bar_code = Column(String(50))
    enabled = Column(SmallInteger, default=1)

    def update(self, *, name, code, date_begin, date_end, max_count, max_count_per_azs, bar_code, enabled):
        self.name = name
        self.code = code
        self.date_begin = date_begin
        self.date_end = date_end
        self.max_count = max_count or 0
        self.max_count_per_azs = max_count_per_azs or 0
        self.bar_code = bar_code or 0
        self.enabled = enabled or 0
        session.commit()
        return self

    @classmethod
    def new(cls, *, name, code, date_begin, date_end, max_count, max_count_per_azs, bar_code, enabled):
        product = cls(
            name=name,
            code=code,
            date_begin=date_begin,
            date_end=date_end,
            max_count=max_count,
            max_count_per_azs=max_count_per_azs,
            bar_code=bar_code,
            enabled=enabled
        )
        session.add(product)
        session.commit()
        return product

    def remove(self):
        session.delete(self)
        if session.commit():
            return True
        return False


class AzsRequest(Base):
    __tablename__ = 'azs_request'

    id = Column(Integer, primary_key=True)
    token = Column(String(50))
    azs_id = Column(Integer, ForeignKey(Azs.id))
    azs = relationship(Azs, backref='requests')
    azs_ip = Column(String(50))
    ts_create = Column(TIMESTAMP, nullable=False, default=datetime.now)
    ts_usage = Column(TIMESTAMP, nullable=True)


class AzsProduct(Base):
    __tablename__ = 'azs_product'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id))
    product = relationship(Product, backref='azs')
    azs_request_id = Column(Integer, ForeignKey(AzsRequest.id))
    azs_request = relationship(AzsRequest, backref='azs_request')
    ts_create = Column(TIMESTAMP, nullable=False, default=datetime.now)
    ts_usage = Column(TIMESTAMP, nullable=True)
