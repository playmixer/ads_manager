from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, select
from .database import Base, session
from datetime import datetime


# class Outlet(Base):
#     __tablename__ = 'azs'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(50))
#     num = Column(Integer)
#     lat = Column(Float)
#     lon = Column(Float)
#     ip = Column(String(20))
#     token = Column(String(50))
#     status = Column(Integer)
#     ts_create = Column(TIMESTAMP, default=datetime.now())
#     ts_update = Column(TIMESTAMP, default=datetime.now())
#
#     @classmethod
#     def select(cls):
#         return select(cls)
#
#     @classmethod
#     def all(cls):
#         return cls.select().all()
