# tasks.py (or inside celery_worker.py)
import time
import csv
from flask import current_app
from celery_worker import celery
from model import db, Booking, Trek, User
import os
from datetime import date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import func 

def send_real_email(to_email, subject, body, is_html=False):
    """Helper function to send real emails."""
    
    #  Email Configuration
    SMTP_SERVER = 'localhost'
    SMTP_PORT = 1025
    SENDER_EMAIL = 'admin@gmail.com'
    
    
    # SMTP_SERVER = 'smtp.gmail.com'
    # SMTP_PORT = 587
    # SENDER_EMAIL = 'your_actual_email@gmail.com'
    # SENDER_PASSWORD = 'your_app_password'

    # 2. Build the email message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body (HTML or Plain Text)
    content_type = "html" if is_html else "plain"
    msg.attach(MIMEText(body, content_type))

    # 3. Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # server.starttls() # Uncomment this line if Gmail/Production
            # server.login(SENDER_EMAIL, SENDER_PASSWORD) # using Gmail
            
            server.send_message(msg)
            print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {str(e)}")

@celery.task(bind=True)
def generate_booking_report_csv(self):
    """
    Background task to generate a CSV report of all bookings.
    """
    # 1. Update task state to tell the frontend we are working
    self.update_state(state='PROGRESS', meta={'status': 'Compiling database records...'})
    
   
    time.sleep(3) 
    
    # 2. Query the database inside the background worker
    bookings = Booking.query.all()
    
    # 3. Create the file path
    filename = f"booking_report_{self.request.id}.csv"
    filepath = os.path.join(current_app.root_path, 'static/reports', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 4. Write data to CSV
    self.update_state(state='PROGRESS', meta={'status': 'Writing to CSV file...'})
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Booking ID', 'Trek ID', 'Trekker ID', 'Booked Slots', 'Date', 'Status'])
        
        for b in bookings:
            writer.writerow([b.id, b.trek_id, b.trekker_id, b.booked_slots, b.book_date, b.status])
            
    # 5. Return the filename so the frontend knows what to download
    return {'status': 'Complete', 'filename': filename}

# tasks.py (Add this below your existing admin task)

@celery.task(bind=True)
def generate_user_history_csv(self, user_id):
    """
    Background task to generate a CSV report of a single user's booking history.
    """
    self.update_state(state='PROGRESS', meta={'status': 'Compiling your history...'})
    
    
    user_bookings = db.session.query(Booking, Trek).join(Trek, Booking.trek_id == Trek.id)\
        .filter(Booking.trekker_id == user_id).all()
        
    filename = f"user_history_{user_id}_{self.request.id}.csv"
    filepath = os.path.join(current_app.root_path, 'static/reports', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    self.update_state(state='PROGRESS', meta={'status': 'Writing CSV file...'})
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Required columns from the prompt: User ID, Trek Name, Location, Booking Status, Dates
        writer.writerow(['User ID', 'Trek Name', 'Location', 'Booking Status', 'Start Date', 'End Date'])
        
        for booking, trek in user_bookings:
            writer.writerow([
                booking.trekker_id,
                trek.name,
                trek.location,
                booking.status,
                trek.start_date.strftime('%Y-%m-%d'),
                trek.end_date.strftime('%Y-%m-%d')
            ])
            
    return {'status': 'Complete', 'filename': filename}





@celery.task(bind=True)
def send_daily_reminders(self):
    """
    Scheduled Job: Send reminders for treks starting tomorrow.
    """
    tomorrow = date.today() + timedelta(days=2)
    
    # Find all treks starting tomorrow
    upcoming_treks = Trek.query.filter_by(start_date=tomorrow, status='Active').all()
    
    for trek in upcoming_treks:
        bookings = Booking.query.filter_by(trek_id=trek.id, status='Confirmed').all()
        for booking in bookings:
            user = User.query.get(booking.trekker_id)
            if user:
                # Build the subject and message
                subject = f"Reminder: {trek.name} starts day after tomorrow!"
                body = (
                    f"Hello {user.name},\n\n"
                    f"This is a quick reminder that your trek '{trek.name}' "
                    f"at {trek.location} starts day after tomorrow ({tomorrow}).\n\n"
                    f"Please make sure you have all your gear ready. Safe travels!\n\n"
                    f"- The TrekApp Team"
                )
                
                
                send_real_email(user.email, subject, body, is_html=False)
                
    return "Daily reminders processed."



@celery.task(bind=True)
def send_monthly_report(self):
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    
    
    popular_treks = db.session.query(
        Trek.name, func.count(Booking.id).label('count')
    ).join(Booking, Trek.id == Booking.trek_id) \
     .group_by(Trek.id) \
     .order_by(func.count(Booking.id).desc()) \
     .limit(3).all()

    
    popular_html = "<ul>"
    for trek_name, count in popular_treks:
        popular_html += f"<li>{trek_name} - {count} bookings</li>"
    popular_html += "</ul>"
    
    # Build the HTML Report
    html_content = f"""
    <html>
        <body>
            <h2>Monthly Trekking Activity Report</h2>
            <hr>
            <p><strong>Total Treks Conducted:</strong> {total_treks}</p>
            <p><strong>Total User Bookings:</strong> {total_bookings}</p>
            <h3>Most Popular Treks this Month:</h3>
            {popular_html}
        </body>
    </html>
    """
    
    admin = User.query.filter_by(role='admin').first()
    if admin:
        send_real_email(admin.email, "Monthly Admin Report", html_content, is_html=True)
        
    return "Monthly report sent."
