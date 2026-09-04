import hashlib

def store_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()

def check_password(pw, stored):
    return hashlib.md5(pw.encode()).hexdigest() == stored
