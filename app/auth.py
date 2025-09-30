from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager, bcrypt, mail
from app.models import User
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.email_utils import send_password_reset_email

# Create the blueprint first
auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask import session




def send_password_reset_email(user):
    try:
        token = user.get_reset_token()
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        msg = Message(
            subject="Password Reset Request - CleanSheet",
            recipients=[user.email],
            html=f"""
            <h3>Password Reset Request</h3>
            <p>You requested a password reset for your CleanSheet account.</p>
            <p>Click the link below to reset your password (valid for 30 minutes):</p>
            <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
            <p><strong>Reset Link:</strong> {reset_url}</p>
            <p>If you didn't request this, please ignore this email.</p>
            <hr>
            <p><small>CleanSheet - Your data cleaning companion</small></p>
            """
        )
        mail.send(msg)
        return True  # Success
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False  # Failure




@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    print(f"DEBUG: Form created. Request method: {request.method}")  # DEBUG
    
    if form.validate_on_submit():
        print("DEBUG: Form validated successfully!")  # DEBUG
        try:
            username = form.username.data
            email = form.email.data.lower()
            password = form.password.data
            
            print(f"DEBUG: Form data - username: {username}, email: {email}")  # DEBUG
            
            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                print("DEBUG: Username already exists")  # DEBUG
                flash('Username already taken', 'danger')
                return render_template('auth/register.html', form=form)
                
            if User.query.filter_by(email=email).first():
                print("DEBUG: Email already exists")  # DEBUG
                flash('Email already registered', 'danger')
                return render_template('auth/register.html', form=form)
            
            # Create user with username
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            print("DEBUG: User created and committed to database")  # DEBUG
            
            session['registration_success'] = True
            print("DEBUG: Redirecting to login")  # DEBUG
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Registration error: {e}")  # DEBUG
            flash(f'Registration failed: {str(e)}', 'danger')
    else:
        print(f"DEBUG: Form validation failed. Errors: {form.errors}")  # DEBUG
    
    return render_template('auth/register.html', form=form)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Check for registration success message
    print(f"DEBUG: Session registration_success: {session.get('registration_success')}")  # DEBUG
    if session.get('registration_success'):
        flash('Registration successful! Please login.', 'success')
        session.pop('registration_success', None)
        print("DEBUG: Registration success message flashed")  # DEBUG
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))



@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            if send_password_reset_email(user):  # Now checks return value
                flash('A password reset link has been sent to your email.', 'info')
            else:
                flash('Error sending email. Please try again later.', 'danger')
        else:
            # For security, don't reveal if email exists
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_token_invalid'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Hash the new password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_password
        db.session.commit()
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset-token-invalid')
def reset_token_invalid():
    return render_template('auth/reset_token_invalid.html')


