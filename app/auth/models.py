from src.database import db
from sqlalchemy import and_, or_, delete
import datetime
import hashlib
from .utils import generate_string

__all__ = ['User', 'Sessions', 'db']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    salt = db.Column(db.String(200), nullable=False, default='')
    personal_token = db.Column(db.String(200), default=lambda x: generate_string(50))
    time_created = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)
    time_updated = db.Column(db.DATETIME, onupdate=datetime.datetime.utcnow)

    @classmethod
    def check_password(cls, username: str, password: str):
        u = cls.query.filter_by(username=username).first()
        if u:
            return u if u.password_matches(password) else False
        return False

    @classmethod
    def check_personal_token(cls, token):
        u = cls.query.filter_by(personal_token=token).first()
        if u:
            return u
        return False

    def password_matches(self, password: str):
        salt = self.salt
        return self.password_hash == self.password_hashing(password, salt)

    @classmethod
    def gen_salt(cls):
        return generate_string(20)

    @classmethod
    def password_hashing(cls, password, salt):
        pass_salt = password + salt
        pass_hashed = hashlib.md5(pass_salt.encode())
        return pass_hashed.hexdigest()

    @classmethod
    def registration(cls, username, password):
        salt = cls.gen_salt()
        pass_salt_hash = cls.password_hashing(password, salt)
        user = cls(
            username=username,
            password_hash=pass_salt_hash,
            salt=salt
        )
        db.session.add(user)
        db.session.commit()

        return user

    def set_password(self, password):
        new_password = self.password_hashing(password, self.salt)
        self.password_hash = new_password
        db.session.commit()

    def set_salt(self):
        self.salt = self.gen_salt()
        db.session.commit()


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref="sessions")
    device_id = db.Column(db.String(200))
    ip = db.Column(db.String(15))
    token = db.Column(db.String(200), nullable=False)
    time_created = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)
    time_end = db.Column(db.DATETIME, nullable=True, default=datetime.datetime.utcnow)

    @classmethod
    def create(cls, user, device_id, ip):
        lifetime = datetime.datetime.utcnow() + datetime.timedelta(days=60)
        sess = cls(
            user_id=user.id,
            device_id=device_id,
            ip=ip,
            token=generate_string(50),
            time_end=lifetime
        )
        db.session.add(sess)
        db.session.commit()
        return sess

    @classmethod
    def refresh(cls, token: str):
        sess = cls.query.filter_by(token=token).first()
        if sess:
            lifetime = datetime.datetime.utcnow() + datetime.timedelta(days=60)
            sess.token = generate_string(50)
            sess.time_end = lifetime
            db.session.commit()
        return sess

    @classmethod
    def delete_token(cls, token):
        sess = cls.query.filter_by(token=token).first()

        if sess:
            db.session.delete(sess)
            db.session.commit()
            return True
        return False
