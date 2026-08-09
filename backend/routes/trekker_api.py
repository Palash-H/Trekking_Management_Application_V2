# 1. THE COMPLETE IMPORT LIST
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash
import os
from model import db, User, Booking, Trek

# 2. THE BLUEPRINT SENTENCE
from datetime import date
from model import db, Trek

def auto_update_trek_statuses():
    """Checks all treks and updates statuses based on today's date"""
    today = date.today()
    changed = False
    
    # 1. Mark as 'Completed' if the end_date has passed
    # (Only touch treks that aren't already Completed or Cancelled)
    past_treks = Trek.query.filter(
        Trek.end_date < today,
        Trek.status.notin_(['Completed', 'Cancelled'])
    ).all()
    
    for t in past_treks:
        t.status = 'Completed'
        changed = True

    # 2. Mark as 'Started' if today is between start_date and end_date
    started_treks = Trek.query.filter(
        Trek.start_date <= today,
        Trek.end_date >= today,
        Trek.status == 'Active'
    ).all()
    
    for t in started_treks:
        t.status = 'Started'
        changed = True

    # Commit only if changes were actually made to save database performance
    if changed:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Auto-update failed:", e)

user_bp = Blueprint('user_bp', __name__)

# routes/user_bp.py (or wherever your user routes are)
@user_bp.route('/api/user/bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    auto_update_trek_statuses()
    claims = get_jwt()
    if claims.get("role") != 'trekker':
        return jsonify({"msg": "Only Trekkers can view this dashboard."}), 403
    
    current_user_id = int(get_jwt_identity())
    
    # This returns a list of Booking objects (with Trek data pre-loaded)
    bookings = Booking.query.options(joinedload(Booking.trek)).filter_by(trekker_id=current_user_id).all()

    history = []
    
    # 🌟 THE FIX: Iterate through 'b' (bookings) and access 't' (trek) via the relationship
    for b in bookings:
        t = b.trek  # Access the joined trek object
        
        # Safety check just in case a booking exists without a trek
        if not t: 
            continue 
            
        history.append({
            "booking_id": b.id,
            "trek_id": t.id,
            "trek_name": t.name,
            "location": t.location,
            "start_date": t.start_date.strftime('%Y-%m-%d') if getattr(t, 'start_date', None) else None,
            "trek_status": getattr(t, 'status', 'Unknown'),
            "booking_status": getattr(b, 'status', 'Unknown'),
            "booked_slots": getattr(b, 'booked_slots', 1)
        })
        
    return jsonify({"history": history}), 200

@user_bp.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Allow users to update their name, contact, or password"""
    
    # FIXED: Security check
    claims = get_jwt()
    if claims.get("role") != 'trekker':
        return jsonify({"msg": "Only Trekkers can update their profile here."}), 403

    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"msg": "No data provided"}), 400
        
    # Update fields
    if 'name' in data and data['name'].strip():
        user.name = data['name'].strip()
        
    # ADDED: Support for contact field
    if 'contact' in data and data['contact'].strip():
        user.contact = data['contact'].strip()
        
    # FIXED: Changed user.password to user.passhash to prevent database crash
    if 'password' in data and data['password'].strip():
        user.passhash = generate_password_hash(data['password'].strip())
        
    try:
        db.session.commit()
        return jsonify({"msg": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error while updating profile."}), 500


# ==========================================
# MISSING USER ENDPOINTS
# ==========================================

@user_bp.route('/api/user/dashboard/summary', methods=['GET'])
@jwt_required()
def user_dashboard_summary():
    """Quick aggregate metrics for the Trekker Dashboard"""
    claims = get_jwt()
    if claims.get("role") != 'trekker':
        return jsonify({"msg": "Only Trekkers can access this."}), 403
        
    current_user_id = int(get_jwt_identity())
    
    # Fetch all bookings with Trek data joined
    bookings = Booking.query.options(joinedload(Booking.trek)).filter_by(trekker_id=current_user_id).all()
    
    total_bookings = len(bookings)
    
    # 🌟 SAFE & SYNCED MATH
    # We use != 'Cancelled' to match the frontend, and getattr() to prevent crashes
    active_upcoming = sum(1 for b in bookings if b.status != 'Cancelled' and getattr(b.trek, 'status', '') in ['Active', 'Open', 'Started'])
    
    # Completed: Booking isn't cancelled AND Trek is finished
    completed_treks = sum(1 for b in bookings if b.status != 'Cancelled' and getattr(b.trek, 'status', '') == 'Completed')
    
    # 🌟 FIX: Cancelled: User cancelled the booking OR Admin cancelled the entire Trek
    cancelled_bookings = sum(1 for b in bookings if b.status == 'Cancelled' or getattr(b.trek, 'status', '') == 'Cancelled')
    
    return jsonify({
        "total_bookings": total_bookings,
        "upcoming_treks": active_upcoming,
        "completed_treks": completed_treks,
        "cancelled_bookings": cancelled_bookings
    }), 200
@user_bp.route('/api/user/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_single_booking_user(booking_id):
    """Trekker fetching details of a single booking (Digital Receipt)"""
    claims = get_jwt()
    if claims.get("role") != 'trekker':
        return jsonify({"msg": "Only Trekkers can access this."}), 403
        
    current_user_id = int(get_jwt_identity())
    
    # Fetch booking and join Trek details
    booking = Booking.query.options(joinedload(Booking.trek)).filter_by(id=booking_id).first()
    
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404
        
    # Security: Ensure they own this booking
    if booking.trekker_id != current_user_id:
        return jsonify({"msg": "Unauthorized access to booking."}), 403
        
    return jsonify({
        "booking_id": booking.id,
        "booked_slots": booking.booked_slots,
        "booking_status": booking.status,
        "booking_date": getattr(booking, 'book_date', None),
        "total_paid": booking.booked_slots * getattr(booking.trek, 'trek_fee', 0),
        "trek_details": {
            "trek_id": booking.trek.id,
            "name": booking.trek.name,
            "location": booking.trek.location,
            "start_date": booking.trek.start_date.strftime('%Y-%m-%d') if booking.trek.start_date else None,
            "end_date": booking.trek.end_date.strftime('%Y-%m-%d') if getattr(booking.trek, 'end_date', None) else None,
            "status": booking.trek.status
        }
    }), 200