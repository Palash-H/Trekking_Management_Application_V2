from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from model import db, Trek, Booking, User
from datetime import date
from sqlalchemy.exc import IntegrityError

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/api/treks/<int:trek_id>/book', methods=['POST'])
@jwt_required()
def book_trek(trek_id):
    # 1. Verify User is a Trekker
    claims = get_jwt()
    if claims.get("role") != 'trekker':
        return jsonify({"msg": "Only Trekkers can book a trek."}), 403
        
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Trekkers can book for themselves + friends. Default to 1 slot.
    requested_slots = data.get('slots_requested', 1) 
    
    if not isinstance(requested_slots, int) or requested_slots < 1:
        return jsonify({"msg": "Must request at least 1 slot."}), 400

    try:
        
        trek = Trek.query.with_for_update().get(trek_id)
        
        if not trek:
            return jsonify({"msg": "Trek not found."}), 404
            
        if trek.status != 'Active': # Assuming you have statuses like 'Pending', 'Active'
            return jsonify({"msg": "This trek is not currently active for booking."}), 400
            
        # 3. Check Capacity
        if trek.slots < requested_slots:
            return jsonify({"msg": f"Booking failed. Only {trek.slots} slots remaining."}), 409
            
        # 4. Check if user already booked this exact trek (Optional MVP logic)
        existing_booking = Booking.query.filter_by(
            trekker_id=current_user_id, 
            trek_id=trek_id
        ).first()
        
        
        if existing_booking:
            return jsonify({"msg": "You have already booked this trek."}), 409

        # 5. Create the Booking Record
        new_booking = Booking(
            trekker_id=current_user_id,
            trek_id=trek.id,
            book_date=date.today(),
            booked_slots=requested_slots,
            status='Confirmed',    
            pay_status='Pending'
        )
        
        # 6. Deduct the inventory safely
        trek.slots = trek.slots - requested_slots
        
        # 7. Commit Transaction (Releases the database lock)
        db.session.add(new_booking)
        db.session.commit()
        
        return jsonify({
            "msg": "Booking successful!", 
            "booking_id": new_booking.id,
            "remaining_slots": trek.slots
        }), 201

    except Exception as e:
        # If anything fails, rollback the transaction to prevent corrupted data
        db.session.rollback()
        return jsonify({"msg": "An error occurred while processing your booking."}), 500

@booking_bp.route('/api/treks/<int:trek_id>/roster', methods=['GET'])
@jwt_required()
def get_trek_roster(trek_id):
    """Returns the participant list. Only accessible by Admins or assigned Staff."""
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"msg": "Trek not found"}), 404
        
    # Security: Ensure only Admins or the EXACT assigned staff member can view this
    if claims.get("role") != 'admin' and trek.assigned_staff != current_user_id:
        return jsonify({"msg": "Unauthorized. You are not assigned to this trek."}), 403
        
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    
    output = []
    for b in bookings:
        
        output.append({
            "booking_id": b.id,
            "trekker_name": b.trekker.name,
            "contact": b.trekker.contact,
            "booked_slots": b.booked_slots,
            "book_date": b.book_date.strftime('%Y-%m-%d')
        })
        
    return jsonify({
        "trek_name": trek.name,
        "total_booked_slots": trek.total_slots - trek.slots,
        "roster": output
    }), 200

@booking_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancels a booking and restores the slots to the Trek inventory"""
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404
        
    if booking.status == 'Cancelled':
        return jsonify({"msg": "Booking is already cancelled"}), 400

    
    if claims.get("role") != 'admin' and booking.trekker_id != current_user_id:
        return jsonify({"msg": "Unauthorized to cancel this booking."}), 403
        
    try:
        
        trek = Trek.query.with_for_update().get(booking.trek_id)
        
        # 3. Update states
        booking.status = 'Cancelled'
        trek.slots = trek.slots + booking.booked_slots 
        
        db.session.commit()
        return jsonify({"msg": "Booking cancelled successfully. Slots restored."}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error while cancelling."}), 500

