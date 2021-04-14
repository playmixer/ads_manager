from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import create_app, db
from shutil import copyfile
import os

app = create_app()
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def install():
    if not os.path.exists('config.py'):
        copyfile('config.example.py', 'config.py')
        print('created config.py')
    print('installed')


if __name__ == '__main__':
    manager.run()
