import os
from flask import current_app, render_template_string
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipient, body, html_body=None):
    """Send an email."""
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@taskmanager.com'),
        recipients=[recipient]
    )
    msg.body = body
    if html_body:
        msg.html = html_body
    
    # Send email in background thread
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user, token):
    """Send password reset email to user."""
    reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
    
    subject = "Password Reset Request - Task Manager"
    
    body = f"""
Dear {user.username},

You have requested to reset your password for your Task Manager account.

Please click the following link to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email and your password will remain unchanged.

Best regards,
The Task Manager Team
"""
    
    html_body = f"""
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>Dear {user.username},</p>
    <p>You have requested to reset your password for your Task Manager account.</p>
    <p>Please click the button below to reset your password:</p>
    <p style="margin: 30px 0;">
        <a href="{reset_url}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px;">
            Reset Password
        </a>
    </p>
    <p>Or copy and paste this link into your browser:</p>
    <p style="color: #666; word-break: break-all;">{reset_url}</p>
    <p><strong>This link will expire in 24 hours.</strong></p>
    <p>If you did not request this password reset, please ignore this email and your password will remain unchanged.</p>
    <p>Best regards,<br>The Task Manager Team</p>
</body>
</html>
"""
    
    send_email(subject, user.email, body, html_body)

def send_password_reset_confirmation_email(user):
    """Send password reset confirmation email."""
    subject = "Password Reset Successful - Task Manager"
    
    body = f"""
Dear {user.username},

Your password has been successfully reset.

If you did not make this change, please contact our support team immediately.

Best regards,
The Task Manager Team
"""
    
    html_body = f"""
<html>
<body>
    <h2>Password Reset Successful</h2>
    <p>Dear {user.username},</p>
    <p>Your password has been successfully reset.</p>
    <p>If you did not make this change, please contact our support team immediately.</p>
    <p>Best regards,<br>The Task Manager Team</p>
</body>
</html>
"""
    
    send_email(subject, user.email, body, html_body)