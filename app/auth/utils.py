import random
import string
import hmac
import hashlib
from flask import request


def generate_string(length=20):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def encrypt_sha256(secret_key: bytes, text: bytes):
    return hmac.new(secret_key, text, hashlib.sha256).hexdigest()


def decrypt_sha256(secret_key: bytes):
    return hmac.new(secret_key, digestmod=hashlib.sha256).hexdigest()


def get_token_from_header():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        _, token = auth_header.split(' ')
        return token
    return None
