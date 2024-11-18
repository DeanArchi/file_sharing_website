import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import File, DownloadLog, FileAccess, User

# Initialize blueprint for the main part of the app
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """
        Display the homepage with a list of all files.

        Returns:
            Rendered index template showing the files.
    """
    return render_template('index.html', files=File.query.all())


@main.route('/profile')
@login_required
def profile():
    """
        Display the admin's profile page with a list of all files and allows to manage files.

        Returns:
            Rendered profile template showing the user's name and all files.
    """
    return render_template('profile.html', name=current_user.name, files=File.query.all())


@main.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """
        Handle file upload functionality.

        Only admins can upload files. Checks if the file already exists before uploading.
        Also assigns permissions for the uploaded file to all users.

        Returns:
            Redirects to the profile page with a success or error message.
    """
    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)

        # Check if file already exists
        existing_file = File.query.filter_by(filename=filename).first()
        if existing_file:
            flash('File already exists.')
            return redirect(url_for('main.profile'))

        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        # Create a new file record in the database
        new_file = File(filename=filename, path=file_path)
        db.session.add(new_file)
        db.session.commit()

        # Assign file access permissions for all users
        users = User.query.all()
        for user in users:
            new_permission = FileAccess(user_id=user.id, file_id=new_file.id, permission=True)
            db.session.add(new_permission)
        db.session.commit()
        flash('File uploaded successfully')
    return redirect(url_for('main.profile'))


@main.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    """
        Handle file download functionality.

        Checks if the user has permission to download the file and increments the download count.
        If the user is an admin, they can download any file.

        Returns:
            Sends the file to the user for download if they have permission.
    """
    if current_user.is_admin:
        file = File.query.get(file_id)
        if file:
            file.download_count += 1
            db.session.add(DownloadLog(user_id=current_user.id, file_id=file.id))
            db.session.commit()
            return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], path=file.filename, as_attachment=True)

    file_access = FileAccess.query.filter_by(user_id=current_user.id, file_id=file_id).first()
    if not file_access or not file_access.permission:
        flash('You do not have permission to download this file.')
        return redirect(url_for('main.index'))

    file = File.query.get(int(file_id))

    if file:
        file.download_count += 1
        db.session.add(DownloadLog(user_id=current_user.id, file_id=file.id))
        db.session.commit()
        return send_from_directory(directory=current_app.config['UPLOAD_FOLDER'], path=file.filename, as_attachment=True)

    flash('File not found.')
    return redirect(url_for('main.index'))


@main.route('/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    """
        Handle file deletion functionality.

        Only admins can delete files. Deletes the file from the system and from the database.

        Returns:
            Redirects to the profile page with a success or error message.
    """
    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    file = File.query.get(file_id)
    if file:
        # Remove file access records
        FileAccess.query.filter_by(file_id=file_id).delete()
        # Remove download logs
        DownloadLog.query.filter_by(file_id=file_id).delete()
        db.session.commit()

        # Delete the file from the filesystem
        os.remove(file.path)

        # Delete the file record from the database
        db.session.delete(file)
        db.session.commit()
        flash('File deleted successfully.')
    else:
        flash('File not found.')

    return redirect(url_for('main.profile'))


@main.route('/admin/files/permissions', methods=['GET', 'POST'])
@login_required
def manage_file_permissions():
    """
        Admin functionality to manage file permissions for users.

        Allows admins to assign or remove file access permissions for users.

        Returns:
            Rendered template showing the file permissions management page.
    """
    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    files = File.query.all()
    users = User.query.all()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        file_id = request.form.get('file_id')
        permission = request.form.get('permission') == 'on'

        # Check if permission exists for the user and file
        existing_permission = FileAccess.query.filter_by(user_id=user_id, file_id=file_id).first()
        if existing_permission:
            existing_permission.permission = permission
        else:
            new_permission = FileAccess(user_id=user_id, file_id=file_id, permission=permission)
            db.session.add(new_permission)

        db.session.commit()
        return redirect(url_for('main.manage_file_permissions'))

    # Prepare file permissions data to display in the template
    file_permissions = {}
    for file in files:
        file_permissions[file.id] = {
            'file': file,
            'permissions': {user.id: False for user in users}
        }

    for file in files:
        for access in file.file_access:
            file_permissions[file.id]['permissions'][access.user_id] = access.permission

    return render_template('admin_file_permissions.html', files=files, users=users, file_permissions=file_permissions)
