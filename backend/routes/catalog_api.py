# public_treks_bp.py
from flask import Blueprint, jsonify
# from app.models import Trek
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from model import db, Trek, User, Booking
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from extensions import cache

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

catalog_bp = Blueprint('catalog', __name__)

# this is for users.
@catalog_bp.route('/api/treks', methods=['GET'])
# @cache.cached(timeout=60, query_string=True) 
def get_all_active_treks():
    auto_update_trek_statuses()
    """Public endpoint to list and rigorously filter all Open treks"""
    
    # 1. Capture all possible query parameters
    search = request.args.get('search', '').lower()
    name = request.args.get('name', '').lower()
    location = request.args.get('location', '').lower()
    difficulty = request.args.get('difficulty', '')
    duration = request.args.get('duration')
    start_date_str = request.args.get('start_date')
    
    # 2. Base Query: ONLY approved/open treks
    query = Trek.query.filter_by(status='Active') 
    
    # 3. Apply General Search (Checks both Name and Location)
    if search:
        query = query.filter(
            (Trek.name.ilike(f'%{search}%')) | 
            (Trek.location.ilike(f'%{search}%'))
        )
        
    # 4. Apply Specific Filters (Stackable)
    if name:
        query = query.filter(Trek.name.ilike(f'%{name}%'))
        
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))
        
    if difficulty:
        # e.g., 'Easy', 'Moderate', 'Hard' (Exact match, ignoring case variations if standardized)
        query = query.filter(Trek.difficulty.ilike(difficulty))
        
    if duration:
        try:
            # We filter for treks that take THIS amount of time or less (Better UX)
            max_duration = int(duration)
            query = query.filter(Trek.time_duration <= max_duration)
        except ValueError:
            pass # Ignore invalid integer inputs gracefully
            
    if start_date_str:
        try:
            # Filter for treks starting ON or AFTER the requested date
            date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Trek.start_date >= date_obj)
        except ValueError:
            pass # Ignore invalid date formats gracefully
            
    # 5. Execute the highly filtered database query
    treks = query.all() 
    
    # 6. Format the output
    output = []
    for t in treks:
        output.append({
            "id": t.id,
            "name": t.name,
            "desc": t.desc,
            "location": t.location,
            "difficulty": getattr(t, 'difficulty', 'Moderate'), 
            "time_duration": getattr(t, 'time_duration', None),
            "start_date": t.start_date.strftime('%Y-%m-%d') if t.start_date else None,
            "end_date": t.end_date.strftime('%Y-%m-%d') if getattr(t, 'end_date', None) else None,
            "status" : t.status,
            "trek_fee": t.trek_fee,
            "total_slots": t.total_slots,
            "available_slots": t.slots,
            "is_sold_out": t.slots <= 0
        })
        
    return jsonify({"treks": output}), 200

@catalog_bp.route('/api/treks/<int:trek_id>', methods=['GET'])
def get_single_trek(trek_id):
    """Public endpoint to view details of a specific trek"""
    t = Trek.query.get(trek_id)
    
    if not t:
        return jsonify({"msg": "Trek not found"}), 404
        
    return jsonify({
        "id": t.id,
        "name": t.name,
        "desc": t.desc,
        "location": t.location,
        "difficulty": t.difficulty,
        "time_duration": t.time_duration,
        "start_date": t.start_date.strftime('%Y-%m-%d') if t.start_date else None,
        "end_date": t.end_date.strftime('%Y-%m-%d'),
        "trek_fee": t.trek_fee,
        "available_slots": t.slots
    }), 200


