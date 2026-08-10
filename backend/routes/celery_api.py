from flask import Blueprint, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from werkzeug.utils import secure_filename 
import os
from extensions import cache
import time

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/api/admin/reports/generate-bookings', methods=['POST'])
@jwt_required()
@cache.cached(timeout=60)
def trigger_report():
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    from tasks import generate_booking_report_csv
    task = generate_booking_report_csv.delay()
    
    return jsonify({"task_id": task.id}), 202


# 2. CHECK TASK STATUS (Polling)
@reports_bp.route('/api/admin/reports/status/<task_id>', methods=['GET'])
@jwt_required()
# @cache.cached(timeout=60)

def get_task_status(task_id):
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403

    from tasks import generate_booking_report_csv
    task = generate_booking_report_csv.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {"state": task.state, "status": "Waiting in queue..."}
    elif task.state == 'PROGRESS':
        response = {"state": task.state, "status": task.info.get('status', '')}
    elif task.state == 'SUCCESS':
        response = {
            "state": task.state,
            "status": task.info.get('status', ''),
            "filename": task.info.get('filename') 
        }
    else:
        response = {"state": task.state, "status": str(task.info)}
        
    return jsonify(response), 200


# 3. DOWNLOAD THE FILE (ADMIN)
@reports_bp.route('/api/admin/reports/download/<filename>', methods=['GET'])
@jwt_required()
def download_report(filename):
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403
        
    
    safe_filename = secure_filename(filename)
    reports_dir = os.path.join(current_app.root_path, 'static', 'reports')
    
    try:
        return send_from_directory(reports_dir, safe_filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"msg": "Report file not found."}), 404


@reports_bp.route('/api/user/export-history', methods=['POST'])
@jwt_required()
def trigger_user_report():
    current_user_id = int(get_jwt_identity())
    
    from tasks import generate_user_history_csv 
    task = generate_user_history_csv.delay(current_user_id)
    
    return jsonify({"task_id": task.id, "msg": "History export started"}), 202



@reports_bp.route('/api/user/export-status/<task_id>', methods=['GET'])
@jwt_required()
def get_user_task_status(task_id):
    
    from tasks import generate_user_history_csv 
    task = generate_user_history_csv.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': task.info.get('status', '')}
        if 'filename' in task.info:
            response['filename'] = task.info['filename']
    else:
        response = {'state': task.state, 'status': str(task.info)}
        
    return jsonify(response)



@reports_bp.route('/api/user/download/<filename>', methods=['GET'])
@jwt_required()
def download_user_report(filename):
    # Ensure they are a trekker
    claims = get_jwt()
    if claims.get("role") != 'trekker':
        return jsonify({"msg": "Only trekkers can download personal history"}), 403
        
    # Secure the filename
    safe_filename = secure_filename(filename)
    reports_dir = os.path.join(current_app.root_path, 'static', 'reports')
    
    try:
        return send_from_directory(reports_dir, safe_filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"msg": "Report file not found."}), 404


from sqlalchemy import func
from model import db, Trek, Booking

@reports_bp.route('/api/admin/statistics', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_trekking_statistics():
    """Returns analytics data for the admin reports page."""
    claims = get_jwt()
    if claims.get("role") != 'admin':
        return jsonify({"msg": "Admin Auth required"}), 403

    # 1. Most Popular Treks (Top 5)
    popular_treks_query = db.session.query(
        Trek.name, func.count(Booking.id).label('booking_count')
    ).join(Booking, Trek.id == Booking.trek_id) \
     .group_by(Trek.id) \
     .order_by(func.count(Booking.id).desc()) \
     .limit(5).all()
     
    popular_treks = [{"name": t[0], "bookings": t[1]} for t in popular_treks_query]

    # 2. Booking Status Breakdown (Confirmed vs Pending vs Cancelled)
    status_query = db.session.query(
        Booking.status, func.count(Booking.id)
    ).group_by(Booking.status).all()
    
    # Defaults just in case the database is empty
    status_breakdown = {"Confirmed": 0, "Pending": 0, "Cancelled": 0}
    total_bookings_ever = 0
    
    for status, count in status_query:
        # Standardize the capitalization (e.g., 'confirmed' -> 'Confirmed')
        clean_status = status.capitalize() if status else 'Pending'
        status_breakdown[clean_status] = count
        total_bookings_ever += count

    return jsonify({
        "popular_treks": popular_treks,
        "status_breakdown": status_breakdown,
        "total_bookings": total_bookings_ever,
        "generated_at":time.time()
    }), 200