from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User

payment = Blueprint('payment', __name__)

@payment.route('/upgrade')
@login_required
def upgrade():
    """Show upgrade options"""
    if current_user.plan == 'pro':
        flash('You already have a Pro account!', 'info')
        return redirect(url_for('main.dashboard'))
    
    return render_template('upgrade.html')

@payment.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    """Process dummy payment"""
    if current_user.plan == 'pro':
        flash('You already have a Pro account!', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Get payment method from form
    payment_method = request.form.get('payment_method')
    
    # Simulate payment processing
    if payment_method == 'credit_card':
        # Simulate credit card processing
        card_number = request.form.get('card_number', '').replace(' ', '')
        expiry = request.form.get('expiry_date')
        cvv = request.form.get('cvv')
        
        if not (card_number and expiry and cvv):
            flash('Please fill all credit card details', 'danger')
            return redirect(url_for('payment.upgrade'))
            
        # Simple validation
        if len(card_number) != 16 or not card_number.isdigit():
            flash('Invalid card number', 'danger')
            return redirect(url_for('payment.upgrade'))
            
        if len(cvv) != 3 or not cvv.isdigit():
            flash('Invalid CVV', 'danger')
            return redirect(url_for('payment.upgrade'))
    
    elif payment_method == 'paypal':
        # Simulate PayPal processing
        flash('Redirecting to PayPal... (simulated)', 'info')
    
    else:
        flash('Please select a payment method', 'danger')
        return redirect(url_for('payment.upgrade'))
    
    # Upgrade user to pro plan
    current_user.upgrade_to_pro()
    
    # Log the transaction (you'd save this to a transactions table in real system)
    current_app.logger.info(f'User {current_user.id} upgraded to Pro plan')
    
    flash('🎉 Payment successful! Your account has been upgraded to Pro!', 'success')
    return redirect(url_for('main.dashboard'))

@payment.route('/downgrade')
@login_required
def downgrade():
    """Downgrade to free plan"""
    if current_user.plan == 'free':
        flash('You already have a Free account!', 'info')
        return redirect(url_for('main.dashboard'))
    
    current_user.downgrade_to_free()
    flash('Your account has been downgraded to Free plan', 'info')
    return redirect(url_for('main.dashboard'))

@payment.route('/payment-success')
@login_required
def payment_success():
    """Payment success page"""
    return render_template('payment_success.html')