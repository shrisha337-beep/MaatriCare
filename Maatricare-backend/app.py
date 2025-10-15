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
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    trimester = db.Column(db.String(20), nullable=False)
    parity = db.Column(db.Integer, nullable=False)
    blood_pressure = db.Column(db.String(20))
    heart_rate = db.Column(db.Integer)
    bmi = db.Column(db.Float)
    anemia = db.Column(db.String(10))
    gestational_diabetes = db.Column(db.String(10))
    hypertension = db.Column(db.String(10))
    ai_risk_prediction = db.Column(db.String(50))
    outcome = db.Column(db.String(50))

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "age": self.age,
            "trimester": self.trimester,
            "parity": self.parity,
            "blood_pressure": self.blood_pressure,
            "heart_rate": self.heart_rate,
            "bmi": self.bmi,
            "anemia": self.anemia,
            "gestational_diabetes": self.gestational_diabetes,
            "hypertension": self.hypertension,
            "ai_risk_prediction": self.ai_risk_prediction,
            "outcome": self.outcome
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
@app.route('/api/dashboard/<string:email>', methods=['GET'])
def get_user_dashboard(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch patient's health record for this user (dummy or linked data)
    patient = Patient.query.filter_by(user_id=user.id).first()

    if not patient:
        return jsonify({
            "username": user.username,
            "email": user.email,
            "health_data": "No patient data linked yet."
        })

    # Return user + patient details
    return jsonify({
        "username": user.username,
        "email": user.email,
        "health_data": {
            "age": patient.age,
            "trimester": patient.trimester,
            "bmi": patient.bmi,
            "bp": patient.blood_pressure,
            "heart_rate": patient.heart_rate,
            "anemia": patient.anemia,
            "gestational_diabetes": patient.gestational_diabetes,
            "hypertension": patient.hypertension,
            "ai_prediction": patient.ai_risk_prediction,
            "outcome": patient.outcome
        }
    })
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
@app.route('/api/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([p.to_dict() for p in patients])
import pandas as pd

def load_csv_data():
    data = pd.read_csv('maatricare_dummy_data.csv')  # change name if needed
    for _, row in data.iterrows():
        existing = Patient.query.filter_by(patient_id=row['Patient_ID']).first()
        if not existing:
            new_patient = Patient(
                patient_id=row['Patient_ID'],
                age=row['Age'],
                trimester=row['Trimester'],
                parity=row['Parity'],
                blood_pressure=row['Blood_Pressure'],
                heart_rate=row['Heart_Rate'],
                bmi=row['BMI'],
                anemia=row['Anemia'],
                gestational_diabetes=row['Gestational_Diabetes'],
                hypertension=row['Hypertension'],
                ai_risk_prediction=row['AI_Risk_Prediction'],
                outcome=row['Outcome']
            )
            db.session.add(new_patient)
    db.session.commit()
    print("✅ Patient data loaded successfully!")

with app.app_context():
    db.create_all()
    load_csv_data()    

if __name__ == "__main__":
    app.run(debug=True)
    load_csv_data()
    app.run(debug=True)
    
    