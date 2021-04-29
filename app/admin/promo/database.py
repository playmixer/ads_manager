# import sqlalchemy
# from sqlalchemy.orm import declarative_base, sessionmaker
# import config
#
# engine = sqlalchemy.create_engine(config.PROMO_DB_URI, echo=False)
#
# Base = declarative_base()
#
# Session = sessionmaker()
# Session.configure(bind=engine)
# session = Session()
#
#
# def select(statement):
#     with engine.connect() as con:
#         rs = con.execute(statement)
#         for row in rs:
#             yield row
