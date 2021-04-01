from flask import current_app
from typing import List
import string
import random
import os
from datetime import datetime

__all__ = ['save_file', 'file_exists']

UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']


def generate_string(length=20):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def get_name_for_file(length=20):
    return generate_string(length).lower()


def extract_extension(filename: str):
    s_name = filename.split('.')
    return s_name[-1]


def mkdir(path: List[str]):
    acc = ''
    for p in path:
        acc = os.path.join(acc, p)
        if not os.path.exists(acc):
            os.mkdir(acc)


def create_path():
    date_now = datetime.utcnow()
    year = date_now.strftime('%Y')
    month = date_now.strftime('%m')
    day = date_now.strftime('%d')

    arr_path = [UPLOAD_FOLDER, year, month, day]
    path = os.path.join(*arr_path[1:])
    mkdir(arr_path)
    return path


def save_file(file):
    filename = get_name_for_file(20)
    ext = extract_extension(file.filename)
    unique_path = create_path()

    path = os.path.join(unique_path, '.'.join([filename, ext]))
    file.save(os.path.join(UPLOAD_FOLDER, path))

    return path, filename, ext


def file_exists(path):
    path_file = os.path.join(UPLOAD_FOLDER, path)
    if os.path.exists(path_file):
        if os.path.isfile(path_file):
            return True
    return False
