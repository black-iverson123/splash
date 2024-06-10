from flask_mail import Message
from app import app, mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to, subject, template):
    msg = Message(subject, html=template, sender=app.config['MAIL_SENDER'], recipients=[to])
    Thread(target=send_async_email, args=(app, msg)).start()
