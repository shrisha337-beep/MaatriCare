from flask import Flask, jsonify, request
from flask_cors import CORS 
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maatricare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

# Ensure tables are created
with app.app_context():
    db.create_all()

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=bcrypt.generate_password_hash(data['password']).decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201
@app.route('/')
def home():
    return jsonify({"message": "MaatriCare backend is running 🚀"})
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({
            'message': 'Login successful 🎉',
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'message': 'Invalid credentials ❌'}), 401

if __name__ == "__main__":
    app.run(debug=True)
    
    