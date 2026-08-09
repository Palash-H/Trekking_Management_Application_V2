# staff_bp.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from model import db, Trek, User,Booking

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff/my-assignments', methods=['GET'])
@jwt_required()
def get_my_assignments():
    """Returns all treks assigned to the logged-in Staff member"""
    claims = get_jwt()
    if claims.get("role") != 'trekstaff':
        return jsonify({"msg": "Only Trek Staff can access this."}), 403
        
    current_user_id = get_jwt_identity()
    
    # Query the Trek table where assigned_staff matches the logged-in user
    assigned_treks = Trek.query.filter_by(assigned_staff=current_user_id).all()
    
    output = []
    for t in assigned_treks:
        output.append({
            "trek_id": t.id,
            "name": t.name,
            "location": t.location,
            "start_date": t.start_date.strftime('%Y-%m-%d'),
            "end_date": t.end_date.strftime('%Y-%m-%d'),
            "status": t.status,
            "total_trekkers_booked": t.total_slots - t.slots
        })
        
    return jsonify({"assignments": output}), 200


@staff_bp.route('/api/staff/treks/<int:trek_id>/status', methods=['PUT'])
@jwt_required()
def update_trek_status_and_slots(trek_id):
    """Allows Staff to update the status OR available slots of a trek they are leading"""
    claims = get_jwt()
    if claims.get("role") != 'trekstaff':
        return jsonify({"msg": "Only Trek Staff can access this."}), 403
        
    current_user_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)
    
    if not trek:
        return jsonify({"msg": "Trek not found."}), 404

    if trek.status == 'Completed':
        return jsonify({"msg": "This trek is completed and cannot be modified."}), 403
        
    if trek.assigned_staff != current_user_id:
        return jsonify({"msg": "You are not authorized to modify this trek."}), 403
        
    data = request.get_json()
    
    # 1. Handle Status Update
    if 'status' in data:
        new_status = data['status']
        valid_statuses = ['Active', 'Started', 'Completed', 'Cancelled']
        if new_status not in valid_statuses:
            return jsonify({"msg": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        trek.status = new_status
        
    # 2. Handle Manual Slot Update (if they need to increase/decrease total capacity)
    if 'add_slots' in data:
        try:
            extra_slots = int(data['add_slots'])
            trek.total_slots += extra_slots
            trek.slots += extra_slots
        except ValueError:
            return jsonify({"msg": "add_slots must be an integer"}), 400

    try:
        db.session.commit()
        return jsonify({"msg": "Trek updated successfully.", "status": trek.status, "available_slots": trek.slots}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error."}), 500

@staff_bp.route('/staff/treks/<int:trek_id>/participants', methods=['GET'])
@jwt_required()
def get_trek_participants(trek_id):
    """Read: View all trekkers booked for a specific trek"""
    
    # --- STAFF SECURITY CHECK ---
    claims = get_jwt()
    if claims.get("role") != 'trekstaff':
        return jsonify({"msg": "Staff Auth required"}), 403
        
    current_staff_id = int(get_jwt_identity())
    
    # Fetch the trek
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"msg": "Trek not found"}), 404
        
    # --- STRICT OWNERSHIP CHECK ---
    # "Ensure only assigned staff can manage a trek"
    if trek.assigned_staff != current_staff_id:
        return jsonify({"msg": "Access denied. You are not assigned to this trek."}), 403
        
    # Join Bookings with Users to get the actual Trekker details
    participants = db.session.query(Booking, User)\
        .join(User, Booking.trekker_id == User.id)\
        .filter(Booking.trek_id == trek_id).all()
        
    participants_list = []
    for booking, user in participants:
        participants_list.append({
            "booking_id": booking.id,
            "trekker_name": user.name,
            "trekker_email": user.email,
            "booked_slots": getattr(booking, 'booked_slots', 1),
            "booking_status": booking.status,
            "booking_date": getattr(booking, 'book_date', None)
        })
        
    return jsonify({
        "trek_name": trek.name,
        "total_participants": len(participants_list),
        "participants": participants_list,
        "trek_status":trek.status
    }), 200

@staff_bp.route('/staff/bookings/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_participant_status(booking_id):
    """Update a specific participant's booking status (e.g., Checked-In, No-Show)"""
    
    claims = get_jwt()
    if claims.get("role") != 'trekstaff' :
        return jsonify({"msg": "Staff Auth required"}), 403
        
    current_staff_id = int(get_jwt_identity())
    
    # Fetch the booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404
        
    # Fetch the associated trek to verify ownership
    trek = Trek.query.get(booking.trek_id)
    
    # --- STRICT OWNERSHIP CHECK ---
    if trek.assigned_staff != current_staff_id:
        return jsonify({"msg": "Access denied. You are not assigned to this trek."}), 403
        
    # Update the status from JSON payload
    data = request.get_json()
    new_status = data.get('status') # e.g., 'Checked-In', 'Completed', 'Cancelled'
    
    if not new_status:
        return jsonify({"msg": "New status is required"}), 400
        
    booking.status = new_status
    db.session.commit()
    
    return jsonify({"msg": f"Booking {booking_id} status updated to {new_status}"}), 200

@staff_bp.route('/api/staff/bookings/<int:booking_id>/remove', methods=['POST'])
@jwt_required()
def remove_trekker(booking_id):
    """Allows Staff to forcefully remove a trekker and refund the slots to the trek"""
    claims = get_jwt()
    if claims.get("role") != 'trekstaff':
        return jsonify({"msg": "Only Trek Staff can access this."}), 403
        
    current_staff_id = int(get_jwt_identity())
    
    # 1. Fetch the booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404
        
    # Prevent double-refunding slots if the trekker is already cancelled
    if booking.status == 'Cancelled':
        return jsonify({"msg": "This booking is already cancelled."}), 400

    if booking.trek.status == 'Completed':
        return jsonify({"msg": "Cannot remove participants from a completed trek."}), 403

    try:
        # 2. Lock the trek row to securely update the available slots
        trek = Trek.query.with_for_update().get(booking.trek_id)
        
        # 3. STRICT OWNERSHIP CHECK
        if trek.assigned_staff != current_staff_id:
            db.session.rollback() # Release the lock if unauthorized
            return jsonify({"msg": "Access denied. You are not assigned to manage this trek."}), 403
            
        # 4. Update states and do the inventory math
        booking.status = 'Cancelled'
        trek.slots = trek.slots + booking.booked_slots # Restore the slots
        
        db.session.commit()
        return jsonify({
            "msg": f"Trekker removed successfully. {booking.booked_slots} slots restored.",
            "available_slots": trek.slots
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error while removing trekker."}), 500


# ==========================================
# MISSING STAFF ENDPOINT
# ==========================================

@staff_bp.route('/api/staff/dashboard/summary', methods=['GET'])
@jwt_required()
def staff_dashboard_summary():
    """Quick aggregate metrics for the Staff Dashboard"""
    claims = get_jwt()
    if claims.get("role") != 'trekstaff':
        return jsonify({"msg": "Only Trek Staff can access this."}), 403
        
    current_staff_id = int(get_jwt_identity())
    
    assigned_treks = Trek.query.filter_by(assigned_staff=current_staff_id).all()
    trek_ids = [trek.id for trek in assigned_treks]
    total_participants = Booking.query.filter( Booking.trek_id.in_(trek_ids)).count()
    
    total_assigned = len(assigned_treks)
    active_treks = sum(1 for t in assigned_treks if t.status in ['Open', 'In-Progress'])
    completed_treks = sum(1 for t in assigned_treks if t.status == 'Completed')
    
    # Calculate total participants across all their treks
    # total_participants = sum((t.total_slots - t.slots) for t in assigned_treks)
    
    return jsonify({
        "total_assigned": total_assigned,
        "active_treks": active_treks,
        "completed_treks": completed_treks,
        "total_participants_managed": total_participants
    }), 200


