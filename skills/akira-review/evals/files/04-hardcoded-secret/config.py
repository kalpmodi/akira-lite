DB_PASSWORD = "S3cr3t-Prod-Db-Pass!"
INTERNAL_API_TOKEN = "akira-eval-fake-8f3b2a1c9d4e0000"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"

def connect():
    return {"password": DB_PASSWORD, "token": INTERNAL_API_TOKEN}
