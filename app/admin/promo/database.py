import sqlalchemy
import config

engine = sqlalchemy.create_engine(config.PROMO_DB_URI, echo=False)


def select(statement):
    with engine.connect() as con:
        rs = con.execute(statement)
        for row in rs:
            yield row
