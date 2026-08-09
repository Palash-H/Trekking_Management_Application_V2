from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from model import db, User, TokenBlocklist, Trek, Booking
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import joinedload

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

auth_bp = Blueprint('admin', __name__)

@auth_bp.route('/admin/create_staff', methods=['POST'])
@jwt_required()
def staff_create():
    """Protected endpoint for Admins to create new Staff members"""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required, Login as Admin"}), 403
        
    data = request.get_json()
    email = data.get('email')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with this email already exists!"}), 400

    new_staff = User(
        name=data.get('name'),
        email=email,
        passhash=generate_password_hash(data.get('password')),
        contact=data.get('contact'),
        role='trekstaff' # Explicitly set to 'trekstaff'
    )
    db.session.add(new_staff)
    db.session.commit()

    return jsonify({"msg": "Staff Created Successfully"}), 201


# @auth_bp.route('/admin/staff_list', methods=['GET'])
# @jwt_required()
# def get_staff_list():
#     # Verify Admin Privileges
#     claims = get_jwt()
#     if claims.get("role") != 'admin':
#         return jsonify({"msg": "Admin Auth required"}), 403

#     # Query only users with the 'trekstaff' role
#     staff_members = User.query.filter_by(role='trekstaff').all()
    
#     # Format the data for the frontend dropdown
#     # Note: Use 'username' if your model uses 'username' instead of 'name'
#     staff_data = [{"id": staff.id, "name": staff.name} for staff in staff_members]
    
#     return jsonify(staff_data), 200

@auth_bp.route('/admin/create_trek', methods=['POST'])
@jwt_required()
def create_trek():
    # 1. Verify Admin Privileges
    auto_update_trek_statuses()
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required, Please login as Admin"}), 403

    data = request.get_json()

    # 2. Date and Time Calculation
    try:
        start_date_str = data.get('date')
        time_duration = int(data.get('time')) 
        
        # Convert string to Python date object
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        # Calculate end_date (Start Date + Duration in days)
        end_date = start_date + timedelta(days=time_duration)

    except (ValueError, TypeError):
        return jsonify({"msg": "Invalid date format or time duration. Use YYYY-MM-DD for date."}), 400

    # 3. Validate Required Fields exist
    if not all([data.get('name'), data.get('desc'), data.get('location'), data.get('slots'), data.get('staff_id')]):
        return jsonify({"msg": "Missing required fields (name, desc, location, slots, staff_id)"}), 400

    # 4. Validate the assigned_staff exists and is actually a staff member
    staff_id = data.get('staff_id')
    staff_member = User.query.get(staff_id)
    
    if not staff_member or staff_member.role != 'trekstaff':
        return jsonify({"msg": "Invalid staff_id. User does not exist or is not Trek Staff."}), 400

    # 5. Create the new Trek
    new_trek = Trek(
        name = data.get('name'),
        desc = data.get('desc'),
        location = data.get('location'),
        difficulty = data.get('difficulty', 'Moderate'),
        time_duration = time_duration,
        total_slots = int(data.get('slots')), # Cast to int safely
        slots = int(data.get('slots')),       # Available slots equal total slots initially
        start_date = start_date,
        end_date = end_date,
        assigned_staff = staff_id,            # Safely validated in step 4
        trek_fee = float(data.get('fee', 0.00)) # Cast to float safely
    )

    # 6. Secure Database Commit
    try:
        db.session.add(new_trek)
        db.session.commit()
        return jsonify({"msg": f"Trek created successfully! End date calculated as {end_date}"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error while creating Trek."}), 500

@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Read: Fetch all users (Trekkers and Staff)"""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    search_query = request.args.get('search', '').lower()
        
    query = User.query.filter(User.role != 'admin')
    
    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        )
        
    users = query.all()
    
    # --- THE FIX: Convert SQLAlchemy objects to a list of dictionaries ---
    users_list = []
    for u in users:
        users_list.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "contact":getattr(u, 'contact', ''),
            "active_status": getattr(u, 'active_status', True), # Failsafe if column is missing
            "blacklist_status": getattr(u, 'blacklist_status', False) # Failsafe if column is missing
        })
        
    return jsonify({"users": users_list}), 200

@auth_bp.route('/api/admin/users/<int:user_id>/<string:action>', methods=['PATCH', 'PUT'])
@jwt_required()
def update_user_status(user_id, action):
    """
    Update: Blacklist, Unblacklist, Deactivate, or Activate a user or staff member.
    Valid actions in URL: 'blacklist', 'unblacklist', 'deactivate', 'activate'
    """
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    if user.role == 'admin':
        return jsonify({"msg": "Cannot modify an Admin's status"}), 400
        
    # Standardize the action string
    action = action.lower().strip()
    
    # Apply the corresponding state changes
    if action == 'blacklist':
        user.blacklist_status = True
    elif action == 'unblacklist':
        user.blacklist_status = False
    elif action == 'deactivate':
        user.active_status = False
    elif action == 'activate':
        user.active_status = True
    else:
        return jsonify({
            "msg": f"Invalid action '{action}'. Must be one of: blacklist, unblacklist, deactivate, activate."
        }), 400
        
    try:
        db.session.commit()
        # Grammar formatting for the success message (e.g., 'activate' -> 'activated')
        action_past_tense = action + "ed" if not action.endswith('e') else action + "d"
        
        return jsonify({
            "msg": f"{user.role.capitalize()} {user.email} successfully {action_past_tense}.",
            "active_status": user.active_status,
            "blacklist_status": user.blacklist_status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error while updating status."}), 500
    
# @auth_bp.route('/admin/treks/<int:trek_id>', methods=['PUT'])
# @jwt_required()
# def update_trek(trek_id):
#     """Update: Modify existing trek details"""
#     claims = get_jwt()
#     if claims.get("role") != 'admin':
#         return jsonify({"msg": "Admin Auth required"}), 403
        
#     trek = Trek.query.get(trek_id)
#     if not trek:
#         return jsonify({"msg": "Trek not found"}), 404
        
#     data = request.get_json()
    
#     # Update fields if provided in the payload
#     if 'name' in data: trek.name = data['name']
#     if 'desc' in data: trek.desc = data['desc']
#     if 'start_date' in data:
#         try:
#             # Converts "YYYY-MM-DD" string into a Python Date object
#             parsed_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
#             trek.start_date = parsed_date
#         except ValueError:
#             return jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}), 400
#     if 'difficulty' in data: trek.difficulty = data['difficulty']
#     if 'trek_fee' in data: trek.trek_fee = data['trek_fee']
#     if 'status' in data: trek.status = data['status'] # e.g., 'Pending', 'Active'
#     # if 'assigned_staff' in data: trek.assigned_staff = data['assigned_staff']
#     if 'trek_fee' in data: trek.trek_fee = data['trek_fee']
#     # Special handling if they want to assign a different staff member
#     if 'staff_id' in data:
#         new_staff = User.query.get(data['staff_id'])
#         if not new_staff or new_staff.role != 'trekstaff':
#             return jsonify({"msg": "Invalid staff_id provided"}), 400
#         trek.assigned_staff = data['staff_id']
        
#     try:
#         db.session.commit()
#         return jsonify({"msg": "Trek updated successfully"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"msg": "Database error"}), 500

@auth_bp.route('/admin/treks/<int:trek_id>', methods=['PUT'])
@jwt_required()
def update_trek(trek_id):
    """Update: Modify existing trek details and auto-calculate end_date"""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"msg": "Trek not found"}), 404

    if trek.status in ['Completed', 'Cancelled']:
        return jsonify({"msg": f"Cannot modify a {trek.status} trek."}), 403
        
    data = request.get_json()
    
    # Flag to check if we need to do math on the end_date
    recalculate_end_date = False
    
    # Update standard fields
    if 'name' in data: trek.name = data['name']
    if 'desc' in data: trek.desc = data['desc']
    if 'difficulty' in data: trek.difficulty = data['difficulty']
    if 'trek_fee' in data: trek.trek_fee = data['trek_fee']
    if 'status' in data: trek.status = data['status'] 
    
    # 1. Handle Start Date
    if 'start_date' in data:
        try:
            parsed_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            trek.start_date = parsed_date
            recalculate_end_date = True
        except ValueError:
            return jsonify({"msg": "Invalid date format. Use YYYY-MM-DD"}), 400
            
    # 2. Handle Duration (Using 'time_duration' based on your previous models)
    if 'time_duration' in data or 'duration' in data:
        # Accepts either key from the Vue frontend
        duration_val = data.get('time_duration', data.get('duration'))
        try:
            trek.time_duration = int(duration_val)
            recalculate_end_date = True
        except ValueError:
            return jsonify({"msg": "Duration must be a valid number"}), 400

    # 3. Auto-Calculate the End Date 
    if recalculate_end_date and trek.start_date and trek.time_duration:
        # Adds the duration days to the start date
        trek.end_date = trek.start_date + timedelta(days=trek.time_duration)

    # 4. Handle Staff Assignment
    if 'staff_id' in data:
        new_staff = User.query.get(data['staff_id'])
        if not new_staff or new_staff.role != 'trekstaff':
            return jsonify({"msg": "Invalid staff_id provided"}), 400
        trek.assigned_staff = data['staff_id']
        
    try:
        db.session.commit()
        return jsonify({
            "msg": "Trek updated successfully", 
            "end_date": trek.end_date.strftime('%Y-%m-%d') if trek.end_date else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Database error while updating trek."}), 500

@auth_bp.route('/admin/treks/<int:trek_id>', methods=['DELETE'])
@jwt_required()
def delete_trek(trek_id):
    """Delete: Remove a trek (cascades to delete associated bookings)"""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"msg": "Trek not found"}), 404

    if trek.status in ['Completed', 'Cancelled']:
        return jsonify({"msg": f"Cannot delete a {trek.status} trek. History must be preserved."}), 403
        
    try:
        db.session.delete(trek)
        db.session.commit()
        return jsonify({"msg": f"Trek '{trek.name}' and its bookings deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error deleting trek. Check foreign key constraints."}), 500




@auth_bp.route('/api/admin/dashboard-stats', methods=['GET'])
@jwt_required()
def admin_stats():
    """Returns quick aggregate metrics for the Admin Dashboard"""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    # 1. Count Total Users by role
    total_trekkers = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='trekstaff').count()
    
    # 2. Count Active Treks
    active_treks = Trek.query.filter_by(status='Active').count()
    total_bookings=Booking.query.count()
    
    # 3. Calculate Total Revenue (Only from Confirmed bookings)
    # This joins the Booking and Trek tables to multiply booked_slots * trek_fee
    revenue_query = db.session.query(
        func.sum(Booking.booked_slots * Trek.trek_fee)
    ).join(Trek).filter(Booking.status != 'Cancelled').scalar()
    
    total_revenue = float(revenue_query) if revenue_query else 0.0
    
    return jsonify({
        "total_trekkers": total_trekkers,
        "total_staff": total_staff,
        "active_treks": active_treks,
        "total_bookings":total_bookings,
        "total_revenue": total_revenue
    }), 200

# routes/auth_bp.py (Add this to your existing file)

@auth_bp.route('/api/admin/treks/<int:trek_id>/assign', methods=['PUT'])
@jwt_required()
def assign_staff(trek_id):
    # Ensure you have your check_admin() helper running here!
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
    
    data = request.get_json()
    staff_id = data.get('staff_id')
    
    trek = Trek.query.get_or_404(trek_id)
    staff = User.query.filter_by(id=staff_id, role='trekstaff').first()
    
    if not staff:
        return jsonify({"msg": "Invalid staff ID or user is not a staff member"}), 400
        
    trek.assigned_staff = staff.id 
    db.session.commit()
    
    return jsonify({"msg": f"Staff {staff.name} successfully assigned to {trek.name}"}), 200

# @auth_bp.route('/api/admin/bookings', methods=['GET'])
# @jwt_required()
# def view_all_bookings():
#     # check_admin() logic goes here...
#     claims = get_jwt()
#     if claims.get("role") != 'admin':
#         return jsonify({"msg": "Admin Auth required"}), 403
    
#     # We join Booking with Trek and User so the frontend has names, not just IDs
#     all_bookings = db.session.query(Booking, Trek, User)\
#         .join(Trek, Booking.trek_id == Trek.id)\
#         .join(User, Booking.trekker_id == User.id).all()
        
#     output = []
#     for b, t, u in all_bookings:
#         output.append({
#             "booking_id": b.id,
#             "trekker_name": u.name,
#             "trekker_email": u.email,
#             "trek_name": t.name,
#             "booked_slots": getattr(b, 'booked_slots', 1), # Safely get slots
#             "status": b.status,
#             "booking_date": getattr(b, 'book_date', None)
#         })
        
#     return jsonify({"bookings": output}), 200

@auth_bp.route('/api/admin/bookings', methods=['GET'])
@jwt_required()
def view_all_bookings():
    """Admin view of all bookings globally, with search capabilities"""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
    
    search_query = request.args.get('search', '').lower()
    
    # Base query joining all three tables
    query = db.session.query(Booking, Trek, User)\
        .join(Trek, Booking.trek_id == Trek.id)\
        .join(User, Booking.trekker_id == User.id)
        
    # Apply search filter if provided
    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%')) |
            (Trek.name.ilike(f'%{search_query}%'))
        )
        
    all_bookings = query.all()
        
    output = []
    for b, t, u in all_bookings:
        
        # Handle datetime formatting so JSON doesn't crash
        date_str = "N/A"
        if getattr(b, 'book_date', None):
            # Assuming book_date is a datetime/date object. 
            # If it is already a string in your DB, you can just use b.book_date directly.
            date_str = b.book_date.strftime('%Y-%m-%d') if hasattr(b.book_date, 'strftime') else b.book_date

        output.append({
            "id": b.id,                        # Changed from booking_id
            "user_name": u.name,               # Changed from trekker_name
            "trekker_email": u.email,          # (Vue isn't using this yet, but good to have)
            "trek_name": t.name,               
            "participants": getattr(b, 'booked_slots', 1), # Changed from booked_slots
            "status": b.status,
            "booking_date": date_str
        })
        
    return jsonify({"bookings": output}), 200

@auth_bp.route('/api/admin/treks', methods=['GET'])
@jwt_required()
def get_all_treks_admin():
    auto_update_trek_statuses()
    """Admin view of all treks (Open, Pending, Completed, etc.) with search"""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    search_query = request.args.get('search', '').lower()
    
    query = Trek.query
    
    if search_query:
        query = query.filter(
            (Trek.name.ilike(f'%{search_query}%')) | 
            (Trek.location.ilike(f'%{search_query}%')) |
            (Trek.status.ilike(f'%{search_query}%'))
        )
        
    treks = query.all()
    
    output = []
    for t in treks:
        output.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "desc":t.desc,
            "start_date": t.start_date.strftime('%Y-%m-%d') if t.start_date else None,
            "status": t.status,
            "total_slots": t.total_slots,
            "difficulty": t.difficulty,
            "time_duration": t.time_duration,
            "available_slots": t.slots,
            "assigned_staff": t.assigned_staff,
            "trek_fee":t.trek_fee
        })
        
    return jsonify({"treks": output}), 200


# ==========================================
# MISSING ADMIN ENDPOINTS
# ==========================================

@auth_bp.route('/api/admin/treks/<int:trek_id>', methods=['GET'])
@jwt_required()
def get_single_trek_admin(trek_id):
    """Admin view of a single trek (Includes assigned staff details)"""
    claims = get_jwt()
    if claims.get("role") != 'admin': return jsonify({"msg": "Admin Auth required"}), 403
        
    trek = Trek.query.get(trek_id)
    if not trek: return jsonify({"msg": "Trek not found"}), 404
        
    staff = User.query.get(trek.assigned_staff) if trek.assigned_staff else None
        
    return jsonify({
        "id": trek.id,
        "name": trek.name,
        "desc": trek.desc,
        "location": trek.location,
        "status": trek.status,
        "difficulty": getattr(trek, 'difficulty', 'Moderate'),
        "start_date": trek.start_date.strftime('%Y-%m-%d') if trek.start_date else None,
        "end_date": trek.end_date.strftime('%Y-%m-%d') if getattr(trek, 'end_date', None) else None,
        "total_slots": trek.total_slots,
        "available_slots": trek.slots,
        "assigned_staff_id": trek.assigned_staff,
        "assigned_staff_name": staff.name if staff else "Unassigned"
    }), 200

@auth_bp.route('/api/admin/staff', methods=['GET'])
@jwt_required()
def get_only_staff():
    """Dedicated endpoint to list and search ONLY staff members"""
    claims = get_jwt()
    if claims.get("role") != 'admin': return jsonify({"msg": "Admin Auth required"}), 403
    
    # ADDED: Search extraction
    search_query = request.args.get('search', '').lower()
    
    query = User.query.filter_by(role='trekstaff')
    
    # ADDED: Search filtering for staff
    if search_query:
        query = query.filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        )
        
    staff_members = query.all()
    
    output = [{
        "id": s.id, 
        "name": s.name, 
        "email": s.email, 
        "contact": s.contact, 
        "active_status": getattr(s, 'active_status', True) == False,
        "blacklist_status": getattr(s, 'blacklist_status', False) == False
    } for s in staff_members]
    
    return jsonify({"staff": output}), 200

@auth_bp.route('/api/admin/staff/<int:staff_id>', methods=['GET'])
@jwt_required()
def get_single_staff(staff_id):
    """Admin view of a single staff member"""
    claims = get_jwt()
    if claims.get("role") != 'admin': return jsonify({"msg": "Admin Auth required"}), 403
    
    staff = User.query.filter_by(id=staff_id, role='trekstaff').first()
    if not staff: return jsonify({"msg": "Staff member not found"}), 404
    
    return jsonify({"id": staff.id, "name": staff.name, "email": staff.email, "contact": staff.contact}), 200

@auth_bp.route('/api/admin/staff/<int:staff_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_staff_details(staff_id):
    """Admin updating a staff member's profile"""
    claims = get_jwt()
    if claims.get("role") != 'admin': return jsonify({"msg": "Admin Auth required"}), 403
    
    staff = User.query.filter_by(id=staff_id, role='trekstaff').first()
    if not staff: return jsonify({"msg": "Staff member not found"}), 404
    
    data = request.get_json()
    if 'name' in data: staff.name = data['name']
    if 'contact' in data: staff.contact = data['contact']
    
    db.session.commit()
    return jsonify({"msg": "Staff details updated successfully"}), 200

@auth_bp.route('/api/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_single_user(user_id):
    """Admin view of a single user"""
    claims = get_jwt()
    if claims.get("role") != 'admin': return jsonify({"msg": "Admin Auth required"}), 403
    
    # FIX: Allow viewing anyone EXCEPT other admins
    user = User.query.filter(User.id == user_id, User.role != 'admin').first()
    
    if not user: return jsonify({"msg": "User not found"}), 404
    
    return jsonify({
        "id": user.id, 
        "name": user.name, 
        "email": user.email, 
        "contact": user.contact, 
        "blacklist_status": user.blacklist_status,
        "active_status": getattr(user, 'active_status', True)
    }), 200
@auth_bp.route('/api/admin/history/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_history_admin(user_id):
    """Admin viewing the booking history of a specific user"""
    claims = get_jwt()
    if claims.get("role") != 'admin': return jsonify({"msg": "Admin Auth required"}), 403
    
    # Verify user exists
    if not User.query.filter_by(id=user_id, role='trekker').first():
        return jsonify({"msg": "Trekker not found"}), 404
        
    bookings = Booking.query.options(joinedload(Booking.trek)).filter_by(trekker_id=user_id).all()
    
    history = [{
        "booking_id": b.id,
        "trek_name": b.trek.name,
        "start_date": b.trek.start_date.strftime('%Y-%m-%d') if b.trek.start_date else None,
        "booked_slots": b.booked_slots,
        "booking_status": b.status,
        "trek_status": b.trek.status
    } for b in bookings]
    
    return jsonify({"user_id": user_id, "history": history}), 200


@auth_bp.route('/api/admin/history/treks', methods=['GET'])
@jwt_required()
def get_historical_treks():
    """Admin view of strictly historical treks (Completed/Cancelled) with performance stats"""
    claims = get_jwt()
    if claims.get("role") != 'admin': return jsonify({"msg": "Admin Auth required"}), 403
    
    search_query = request.args.get('search', '').lower()
    
    # Filter ONLY for treks that are historically finished
    query = Trek.query.filter(Trek.status.in_(['Completed', 'Cancelled']))
    
    if search_query:
        query = query.filter(
            (Trek.name.ilike(f'%{search_query}%')) | 
            (Trek.location.ilike(f'%{search_query}%'))
        )
        
    historical_treks = query.all()
    
    output = []
    for t in historical_treks:
        slots_booked = t.total_slots - t.slots
        output.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "start_date": t.start_date.strftime('%Y-%m-%d') if t.start_date else None,
            "end_date": t.end_date.strftime('%Y-%m-%d') if getattr(t, 'end_date', None) else None,
            "status": t.status,
            "total_slots": t.total_slots,
            "booked_slots": slots_booked,
            "historical_revenue": slots_booked * getattr(t, 'trek_fee', 0)
        })
        
    return jsonify({"historical_treks": output}), 200