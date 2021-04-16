from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import create_app, db
from shutil import copyfile
import os
from app.auth.models import User, Role

app = create_app()
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def install():
    if not os.path.exists('config.py'):
        copyfile('config.example.py', 'config.py')
        print('created config.py')

    Role.create_roles()
    print('Roles created')
    print('installed')


@manager.command
def createsuperuser(username, password):
    u = User.registration(username, password)
    admin = Role.get_role(Role.TypeRole.admin)
    u_r = u.add_role(admin)
    if u_r:
        print('Superuser created')
        return True
    print('Create superuser failed')
    return False


@manager.command
def usersetrole(username, role):
    user = User.query.filter_by(username=username).first()
    if not user:
        print('User not found')
        return

    role = Role.query.filter_by(title=role).first()
    if not role:
        print('Role not found')
        return

    user_role = user.add_role(role)
    if user_role:
        print('Role added for user')
        return
    print('Role add failed')


if __name__ == '__main__':
    manager.run()
