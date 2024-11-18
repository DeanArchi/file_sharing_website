# File Sharing Website
A file-sharing web application that allows users to upload, download, and manage files with access control features. This project includes a user authentication system with roles (admin and regular users) and allows admins to manage file permissions and track download activity.

## Features

- **User Authentication**: Users can sign up, log in, and log out.
- **Admin Control**: Admin users can upload, manage, and delete files, as well as control user access to downloads.
- **Download Statistics**: Tracks the number of downloads for each file.
- **File Access Control**: Regular users can only download files they have permission to access.
- **File Downloads Log**: Logging of file downloads by each user.

## Technologies Used

- **Backend**: Python, Flask
- **Database**: SQLAlchemy (SQLite)
- **Authentication**: Flask-Login
- **File Storage**: File system
- **Environment Variables**: `dotenv` for environment configuration

## Installation

Follow these steps to set up the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/DeanArchi/file_sharing_website.git
cd file_sharing_website
```
### 2. Set Up a Virtual Environment
Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
### 3. Install Dependencies
Install required Python packages:
```bash
pip install -r requirements.txt
```
### 4. Configure Environment Variables
Create a .env file in the root directory and add the following variables:
```bash
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///your_database.db
UPLOAD_FOLDER=uploads
```

### 5. Run the Application
```bas
flask run
```
