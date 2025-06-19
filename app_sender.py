from flask import Flask, render_template, request
import socket, hashlib, os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def sign_data(data):
    with open('keys/private_key.pem', 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    digest = hashlib.sha256(data).digest()
    signature = private_key.sign(digest, padding.PKCS1v15(), hashes.SHA256())
    return signature

def send_to_receiver(filename, file_data, signature):
    HOST = '127.0.0.1'
    PORT = 5001
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(len(filename).to_bytes(4, 'big'))
        s.sendall(filename.encode())

        s.sendall(len(file_data).to_bytes(8, 'big'))
        s.sendall(file_data)

        s.sendall(len(signature).to_bytes(4, 'big'))
        s.sendall(signature)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        with open(filepath, 'rb') as f:
            file_data = f.read()

        signature = sign_data(file_data)
        send_to_receiver(filename, file_data, signature)
        message = f"✅ Đã gửi {filename} và chữ ký tới người nhận."

    return render_template('sender.html', message=message)
