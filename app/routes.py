from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, File
from app.cleaning import process_file
from io import BytesIO
import uuid
import os
from datetime import datetime

# Create the blueprint first
main = Blueprint('main', __name__)





@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    user_files = File.query.filter_by(user_id=current_user.id).order_by(File.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', files=user_files)


# Add to routes.py
@main.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@main.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return "Internal server error", 500


@main.route('/help-center')
def help_center():
    return render_template('help_center.html')

@main.route('/contact')
def contact(   ):
    return render_template('contact.html')                        


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if not (file.filename.lower().endswith(('.csv', '.xlsx', '.xls'))):
            flash('Please upload a CSV or Excel file', 'danger')
            return redirect(request.url)
        
        # Get cleaning options from form
        options = {
            'remove_duplicates': request.form.get('remove_duplicates') == 'on',
            'trim_whitespace': request.form.get('trim_whitespace') == 'on',
            'fill_missing': request.form.get('fill_missing', ''),
            'custom_value': request.form.get('custom_value', ''),
            'rename_map': {}
        }
        
        # Process rename mappings if provided
        rename_pairs = request.form.get('rename_columns', '')
        if rename_pairs:
            for pair in rename_pairs.split(','):
                if ':' in pair:
                    old_col, new_col = pair.split(':', 1)
                    options['rename_map'][old_col.strip()] = new_col.strip()
        
        try:
            # Process the file
            cleaned_file, original_rows, cleaned_rows = process_file(
                file, file.filename, options
            )
            
            # Check if user can process this file
            # if not current_user.can_process_file(original_rows):
            #     flash('Free tier limited to 500 rows. Upgrade to Pro for unlimited processing.', 'warning')
            #     return redirect(url_for('main.dashboard'))
            
            # Save file info to database
            new_file = File(
                user_id=current_user.id,
                original_filename=file.filename,
                cleaned_filename=f"cleaned_{file.filename}",
                rows_original=original_rows,
                rows_cleaned=cleaned_rows,
                operations=options
            )
            db.session.add(new_file)
            db.session.commit()
            
            # Send the cleaned file for download
            flash('File processed successfully!', 'success')
            return send_file(
                cleaned_file,
                as_attachment=True,
                download_name=f"cleaned_{file.filename}",
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html')