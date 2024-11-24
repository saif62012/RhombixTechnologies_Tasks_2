from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from encryption import encrypt_file, decrypt_file
from audit_logger import log_event
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# Dummy user database
users = {'admin': {'password': 'password123'}}
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('upload'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        key = b'\x00' * 32  # Example AES key (replace with your own key logic)
        encrypt_file(file_path, key)
        log_event('UPLOAD', 'admin', file.filename)
        return 'File uploaded and encrypted successfully', 200
    return render_template('upload.html')

@app.route('/download/<filename>', methods=['GET'])
@login_required
def download(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    decrypted_path = file_path.replace('.enc', '.dec')
    key = b'\x00' * 32  # Example AES key
    decrypt_file(file_path, key)
    log_event('DOWNLOAD', 'admin', filename)
    return send_from_directory(UPLOAD_FOLDER, filename.replace('.enc', '.dec'))

if __name__ == '__main__':
    app.run(debug=True)
