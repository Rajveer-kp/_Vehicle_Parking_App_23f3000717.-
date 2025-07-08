from flask import Flask, Blueprint, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_session import Session
from models import db, User
import os
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# ✅ Session Config
app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'  # Always set a secure secret key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=2)  # 2 hour session timeout
Session(app)

# JWT Secret (in production, use environment variable)
JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 2

# ✅ Blueprint for authentication
auth_bp = Blueprint('auth_bp', __name__)
CORS(auth_bp, origins=["http://localhost:5173"], supports_credentials=True)

# ✅ Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        # Check for token in session (fallback)
        if not token and 'auth_token' in session:
            token = session['auth_token']
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = data['user_id']
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def generate_token(user_id, role):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ------------------ Login ------------------
@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # ✅ Generate JWT token
        token = generate_token(user.id, user.role)
        
        # ✅ Set session data
        session['user_id'] = user.id
        session['role'] = user.role
        session['auth_token'] = token
        session['login_time'] = datetime.datetime.utcnow().isoformat()
        
        return jsonify({
            'message': 'Login successful',
            'role': user.role,
            'user_id': user.id,
            'username': user.username,
            'fullname': user.fullname,
            'token': token,
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # seconds
        })
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# ------------------ Register ------------------
@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')
    address = data.get('address')
    pincode = data.get('pincode')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(
        username=username,
        password=hashed_password,
        role='user',
        fullname=fullname,
        address=address,
        pincode=pincode
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'})

# ------------------ Check Active Session ------------------
@auth_bp.route('/check-session', methods=['GET'])
@token_required
def check_session(current_user):
    """
    Check if the current session/token is valid
    """
    return jsonify({
        'message': 'Session active',
        'user_id': current_user.id,
        'username': current_user.username,
        'role': current_user.role,
        'fullname': current_user.fullname
    })

# ------------------ Logout ------------------
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user - clear session and invalidate token
    Note: In a production system, you'd typically blacklist the JWT token
    """
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# ------------------ Favicon (Optional) ------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# ✅ Register the blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

# ✅ Run the app
if __name__ == '__main__':
    app.run(debug=True)
