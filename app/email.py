# app/email.py
from flask_mail import Mail, Message
from flask import current_app, render_template
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipient, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_token()
    send_email(
        '[CleanSheet] Reset Your Password',
        recipient=user.email,
        template='email/reset_password',
        user=user,
        token=token
    )