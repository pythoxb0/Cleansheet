from flask_mail import Message
from flask import url_for, current_app
from app import mail

def send_password_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        subject='Password Reset Request - CleanSheet',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg.html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .button {{ background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>CleanSheet</h1>
                <p>Password Reset Request</p>
            </div>
            <div class="content">
                <h3>Hello {user.username},</h3>
                <p>You requested a password reset for your CleanSheet account.</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>If you didn't make this request, please ignore this email.</p>
                <p><strong>Note:</strong> This link will expire in 30 minutes.</p>
            </div>
            <div class="footer">
                <p>If you're having trouble clicking the button, copy and paste this URL into your browser:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>&copy; 2024 CleanSheet. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    mail.send(msg)