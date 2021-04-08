import random
import string
import hmac
import hashlib


def generate_string(length=20):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def encrypt_sha256(secret_key: bytes, text: bytes):
    return hmac.new(secret_key, text, hashlib.sha256).hexdigest()


def decrypt_sha256(secret_key: bytes):
    return hmac.new(secret_key, digestmod=hashlib.sha256).hexdigest()
