from src.database import db
import datetime
import hashlib
from .utils import generate_string
import enum

user_role_table = db.Table('user_role', db.metadata,
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                           )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    salt = db.Column(db.String(200), nullable=False, default='')
    personal_token = db.Column(db.String(200), default=lambda x: generate_string(50))
    roles = db.relationship('Role', secondary=user_role_table)
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

    def add_role(self, role):
        self.roles.append(role)
        db.session.add(self)
        db.session.commit()
        return self


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


class Role(db.Model):
    class TypeRole(enum.Enum):
        admin = 'admin'

        @classmethod
        def get_all_role(cls):
            attrs = dir(cls)
            filtered = list(filter(lambda x: not x.startswith('__'), attrs))
            return filtered

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Enum(TypeRole), nullable=False, unique=True)
    date_create = db.Column(db.DATETIME, nullable=False, default=datetime.datetime.utcnow)

    @classmethod
    def create_roles(cls):
        roles = cls.TypeRole.get_all_role()
        for role in roles:
            r = cls.query.filter_by(title=role).first()
            if not r:
                new_role = cls(title=role)
                db.session.add(new_role)
                db.session.commit()

        return True

    @classmethod
    def get_role(cls, role: TypeRole):
        role = cls.query.filter_by(title=role).first()
        return role

