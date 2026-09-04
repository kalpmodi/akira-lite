import bcrypt

def store_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def check_password(pw, stored):
    return bcrypt.checkpw(pw.encode(), stored)
