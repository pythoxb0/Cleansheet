from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, File
from app.cleaning import process_file
from io import BytesIO
import uuid
import os
from datetime import datetime
from app.forms import LoginForm, RegistrationForm, UploadForm

from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import os



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
    search_query = request.args.get('q', '')
    return render_template('help_center.html')

@main.route('/contact')
def contact(   ):
    return render_template('contact.html')    

                    
@main.route('/404')
def not_found():
    return render_template('404.html'), 404

from flask import send_file, after_this_request
import os
import tempfile

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if file is present
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        try:
            # Create a temporary directory if it doesn't exist
            temp_dir = os.path.join(os.getcwd(), 'temp_files')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Get form data
            remove_duplicates = 'remove_duplicates' in request.form
            trim_whitespace = 'trim_whitespace' in request.form
            fill_missing = request.form.get('fill_missing', '')
            custom_value = request.form.get('custom_value', '')
            rename_columns = request.form.get('rename_columns', '')
            
            # Process the file
            filename = secure_filename(file.filename)
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Apply cleaning operations
            if remove_duplicates:
                df = df.drop_duplicates()
            
            if trim_whitespace:
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
            
            # Handle missing values
            if fill_missing == 'mean':
                df = df.fillna(df.mean(numeric_only=True))
            elif fill_missing == 'median':
                df = df.fillna(df.median(numeric_only=True))
            elif fill_missing == 'custom' and custom_value:
                df = df.fillna(custom_value)
            
            # Handle column renaming
            if rename_columns:
                rename_dict = {}
                for pair in rename_columns.split(','):
                    if ':' in pair:
                        old, new = pair.split(':', 1)
                        rename_dict[old.strip()] = new.strip()
                if rename_dict:
                    df = df.rename(columns=rename_dict)
            
            # Save cleaned file to temporary directory
            cleaned_filename = 'cleaned_' + filename
            cleaned_filepath = os.path.join(temp_dir, cleaned_filename)
            
            if filename.endswith('.csv'):
                df.to_csv(cleaned_filepath, index=False)
                download_mimetype = 'text/csv'
            else:
                df.to_excel(cleaned_filepath, index=False)
                download_mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            flash('File processed successfully! Click "Download" to get your cleaned file.', 'success')
            
            # Return both the success message and download link
            return render_template('upload.html', 
                                 download_file=cleaned_filename,
                                 original_filename=filename)
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
    
    return render_template('upload.html')

@main.route('/download/<filename>')
def download_file(filename):
    """Download the cleaned file"""
    temp_dir = os.path.join(os.getcwd(), 'temp_files')
    file_path = os.path.join(temp_dir, filename)
    
    if os.path.exists(file_path):
        # Clean up the file after sending
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as error:
                print(f"Error removing file: {error}")
            return response
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash('File not found. Please process your file again.', 'error')
        return redirect(url_for('main.upload'))
def upload():
    if request.method == 'POST':
        # Check if file is present
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Check file extension
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            flash('Invalid file type. Please upload CSV or Excel files.', 'error')
            return redirect(request.url)
        
        try:
            # Get form data
            remove_duplicates = 'remove_duplicates' in request.form
            trim_whitespace = 'trim_whitespace' in request.form
            fill_missing = request.form.get('fill_missing', '')
            custom_value = request.form.get('custom_value', '')
            rename_columns = request.form.get('rename_columns', '')
            
            # Process the file based on extension
            filename = secure_filename(file.filename)
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Apply cleaning operations
            if remove_duplicates:
                df = df.drop_duplicates()
            
            if trim_whitespace:
                # Trim whitespace from string columns
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
            
            # Handle missing values
            if fill_missing == 'mean':
                df = df.fillna(df.mean(numeric_only=True))
            elif fill_missing == 'median':
                df = df.fillna(df.median(numeric_only=True))
            elif fill_missing == 'custom' and custom_value:
                df = df.fillna(custom_value)
            
            # Handle column renaming
            if rename_columns:
                rename_dict = {}
                for pair in rename_columns.split(','):
                    if ':' in pair:
                        old, new = pair.split(':', 1)
                        rename_dict[old.strip()] = new.strip()
                if rename_dict:
                    df = df.rename(columns=rename_dict)
            
            # Save cleaned file
            cleaned_filename = 'cleaned_' + filename
            if filename.endswith('.csv'):
                df.to_csv(cleaned_filename, index=False)
            else:
                df.to_excel(cleaned_filename, index=False)
            
            flash('File processed successfully!', 'success')
            # You can add a download link here
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
    
    return render_template('upload.html')
