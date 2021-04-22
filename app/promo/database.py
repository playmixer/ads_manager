import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
import config

engine = sqlalchemy.create_engine(config.PROMO_DB_URI, echo=False)

Base = declarative_base()

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


def init_db():
    from . import models
    # Base.metadata.create_all(bind=engine)


def insert(obj):
    with Session.begin() as sess:
        sess.add(obj)
