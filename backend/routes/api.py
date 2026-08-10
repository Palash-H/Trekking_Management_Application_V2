# api.py
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from datetime import datetime, timedelta, date
from sqlalchemy.exc import IntegrityError
import os


from model import db, User, TokenBlocklist, Trek, Booking 


auth_b = Blueprint('auth', __name__)



@auth_b.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
        
    user = User.query.filter_by(email=email).first()
    
    # 1. Verify user exists and password matches
    if not user or not check_password_hash(user.passhash, password):
        return jsonify({"msg": "Invalid credentials"}), 401
        
    if user.role in ['trekker', 'trekstaff']:
        # Check Blacklist Status
        if getattr(user, 'blacklist_status', False): 
            return jsonify({"msg": "Your account has been blacklisted. Please contact support."}), 403
            
        
        if getattr(user, 'active_status', True) == False: 
            return jsonify({"msg": "Your account is currently deactivated. Please contact support."}), 403
            
    # 3. Create token and inject role for Vue.js routing
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    
    return jsonify({
        "msg": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "contact": user.contact
        }
    }), 200

@auth_b.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()

    # 1. Validate required fields
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"msg": "Email, password, and name are required."}), 400

    email = data.get('email').strip().lower()
    
    # 2. Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered."}), 409

   
    new_user = User(
        name=data.get('name'),
        email=email,
        passhash=generate_password_hash(data.get('password')),
        contact = data.get('contact'),
        role='trekker', # Hardcoded to prevent privilege escalation
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "Registration successful. You can now log in."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error occurred during registration."}), 500



@auth_b.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    
    jti = get_jwt()["jti"]
    
    
    blocked_token = TokenBlocklist(jti=jti)
    
    try:
        db.session.add(blocked_token)
        db.session.commit()
        return jsonify({"message": "Successfully logged out"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error logging out"}), 500




@auth_b.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "contact": user.contact,
        "role": user.role,
        "blacklist_status": user.blacklist_status
    }), 200
        




