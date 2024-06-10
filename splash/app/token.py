from itsdangerous import URLSafeTimedSerializer as Serializer

from app import app

def generate_token(email):
    s = Serializer(app.config['SECRET_KEY'])
    return s.dumps(email, salt='pdfack124!@#')

def confirm_token(token, expiration = 3600):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='pdfack124!@#', max_age=expiration)
        return email
    except Exception:
        return False