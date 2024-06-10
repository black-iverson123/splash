import os



basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'Darkseid'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_SENDER = 'noreply@splash.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('username')
    MAIL_PASSWORD = os.environ.get('password')
    ADMIN = os.environ.get('admin')