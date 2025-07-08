

from celery import Celery
import os
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def make_celery(app_name=__name__):
 
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    celery = Celery(
        app_name,
        broker=redis_url,
        backend=redis_url,
        include=['celery_tasks']  
    )
    
    # Celery configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        beat_schedule={
        
            'send-daily-reminders': {
                'task': 'celery_tasks.send_daily_parking_reminders',
                'schedule': 86400.0,  # 24 hours
            },
          
            'cleanup-expired-sessions': {
                'task': 'celery_tasks.cleanup_expired_parking_sessions',
                'schedule': 3600.0,  # 1 hour
            },
         
            'generate-daily-reports': {
                'task': 'celery_tasks.generate_daily_reports',
                'schedule': 86400.0,  # 24 hours
            },
  
            'update-parking-stats': {
                'task': 'celery_tasks.update_parking_statistics',
                'schedule': 1800.0,  # 30 minutes
            }
        },
        beat_scheduler='celery.beat:PersistentScheduler',
        worker_hijack_root_logger=False,
        worker_log_color=False,
        task_routes={
            'celery_tasks.send_email': {'queue': 'email'},
            'celery_tasks.send_daily_parking_reminders': {'queue': 'email'},
            'celery_tasks.generate_reports': {'queue': 'reports'},
            'celery_tasks.cleanup_expired_parking_sessions': {'queue': 'maintenance'},
        }
    )
    
    return celery

# Create Celery instance
celery_app = make_celery()


@celery_app.task(bind=True, max_retries=3)
def send_email(self, to_email, subject, body, is_html=False):
    """
    Send email task
    """
    try:
        logging.info(f"Sending email to {to_email} with subject: {subject}")
        
      
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_username = os.environ.get('SMTP_USERNAME', 'rajveerkharade9@gmail.com')
        smtp_password = os.environ.get('SMTP_PASSWORD', 'vrjdfdrzowqusred')
        
  
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
  
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        
 
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logging.info(f"✅ Email sent successfully to {to_email}")
        return {"status": "success", "message": f"Email sent to {to_email}"}
        
    except Exception as e:
        logging.error(f"❌ Email sending failed: {str(e)}")
        if self.request.retries < self.max_retries:
            logging.info(f"Retrying email send (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        return {"status": "error", "message": str(e)}

@celery_app.task
def send_parking_reminder(user_email, user_name, vehicle_no, location, duration):
    """
    Send parking reminder to user
    """
    subject = "🚗 Parking Reminder - Vehicle Parking System"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #007bff; margin: 0;">🚗 Parking Reminder</h1>
                <p style="color: #666; margin: 10px 0 0 0;">Vehicle Parking System</p>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h2 style="color: #856404; margin: 0 0 10px 0;">⏰ Parking Duration Alert</h2>
                <p style="color: #856404; margin: 0;">Your vehicle has been parked for {duration}. Please check if you need to extend or exit.</p>
            </div>
            
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h3 style="color: #333; margin: 0 0 15px 0;">Parking Details:</h3>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="padding: 5px 0; border-bottom: 1px solid #dee2e6;"><strong>👤 Name:</strong> {user_name}</li>
                    <li style="padding: 5px 0; border-bottom: 1px solid #dee2e6;"><strong>🚗 Vehicle:</strong> {vehicle_no}</li>
                    <li style="padding: 5px 0; border-bottom: 1px solid #dee2e6;"><strong>📍 Location:</strong> {location}</li>
                    <li style="padding: 5px 0;"><strong>⏱️ Duration:</strong> {duration}</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #666; margin: 0;">Thank you for using our parking system!</p>
                <p style="color: #999; font-size: 12px; margin: 10px 0 0 0;">This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email.delay(user_email, subject, body, is_html=True)

@celery_app.task
def send_daily_parking_reminders():
    """
    Send daily reminders to users with long-duration parking
    """
    try:
        from app import create_app
        from models import db, User, ParkingHistory
        
        app = create_app()
        with app.app_context():
            # Find users with parking duration > 8 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=8)
            
            long_parked = db.session.query(ParkingHistory, User).join(
                User, ParkingHistory.user_id == User.id
            ).filter(
                ParkingHistory.status == 'Parked',
                ParkingHistory.timestamp < cutoff_time
            ).all()
            
            reminders_sent = 0
            for history, user in long_parked:
                duration_hours = (datetime.utcnow() - history.timestamp).total_seconds() / 3600
                duration_str = f"{int(duration_hours)} hours"
                
                send_parking_reminder.delay(
                    user.username,  # email
                    user.fullname,
                    history.vehicle_no,
                    history.lot.name if history.lot else "Unknown Location",
                    duration_str
                )
                reminders_sent += 1
            
            logging.info(f"✅ Sent {reminders_sent} parking reminders")
            return {"status": "success", "reminders_sent": reminders_sent}
            
    except Exception as e:
        logging.error(f"❌ Daily reminders failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def cleanup_expired_parking_sessions():
    """
    Cleanup expired parking sessions and update statuses
    """
    try:
        from app import create_app
        from models import db, ParkingHistory
        
        app = create_app()
        with app.app_context():
            # Find parking sessions older than 24 hours that are still "Parked"
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            expired_sessions = ParkingHistory.query.filter(
                ParkingHistory.status == 'Parked',
                ParkingHistory.timestamp < cutoff_time
            ).all()
            
            updated_count = 0
            for session in expired_sessions:
                session.status = 'Expired'
                updated_count += 1
            
            db.session.commit()
            
            logging.info(f"✅ Cleaned up {updated_count} expired parking sessions")
            return {"status": "success", "cleaned_up": updated_count}
            
    except Exception as e:
        logging.error(f"❌ Cleanup failed: {str(e)}")
        db.session.rollback()
        return {"status": "error", "message": str(e)}

@celery_app.task
def generate_daily_reports():
    """
    Generate daily parking reports
    """
    try:
        from app import create_app
        from models import db, ParkingLot, ParkingHistory
        
        app = create_app()
        with app.app_context():
            today = datetime.utcnow().date()
            
            # Calculate daily statistics
            daily_bookings = ParkingHistory.query.filter(
                db.func.date(ParkingHistory.timestamp) == today
            ).count()
            
            active_parkings = ParkingHistory.query.filter(
                ParkingHistory.status == 'Parked'
            ).count()
            
            total_revenue = db.session.query(
                db.func.sum(ParkingLot.price_per_hour)
            ).join(ParkingHistory).filter(
                db.func.date(ParkingHistory.timestamp) == today,
                ParkingHistory.status.in_(['Parked', 'Completed'])
            ).scalar() or 0
            
            report_data = {
                "date": today.isoformat(),
                "daily_bookings": daily_bookings,
                "active_parkings": active_parkings,
                "revenue": float(total_revenue),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            
            logging.info(f"✅ Generated daily report for {today} (cached in memory)")
            return {"status": "success", "report": report_data}
            
    except Exception as e:
        logging.error(f"❌ Report generation failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def update_parking_statistics():
    """
    Update parking statistics in cache
    """
    try:
        from app import create_app
        from models import db, ParkingLot, ParkingHistory, User
        
        app = create_app()
        with app.app_context():
            # Update global statistics
            total_users = User.query.count()
            total_lots = ParkingLot.query.count()
            active_parkings = ParkingHistory.query.filter(
                ParkingHistory.status == 'Parked'
            ).count()
            
            total_spots = db.session.query(
                db.func.sum(ParkingLot.max_spots)
            ).scalar() or 0
            
            occupancy_rate = (active_parkings / total_spots * 100) if total_spots > 0 else 0
            
            stats = {
                "total_users": total_users,
                "total_lots": total_lots,
                "total_spots": total_spots,
                "active_parkings": active_parkings,
                "occupancy_rate": round(occupancy_rate, 2),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Stats cached in memory only (Redis removed)
            logging.info(f"✅ Updated parking statistics (cached in memory)")
            return {"status": "success", "stats": stats}
            
    except Exception as e:
        logging.error(f"❌ Statistics update failed: {str(e)}")
        return {"status": "error", "message": str(e)}


def start_celery_worker():
    """Start Celery worker (for development)"""
    celery_app.worker_main(['worker', '--loglevel=info', '--concurrency=4'])

def start_celery_beat():
    """Start Celery beat scheduler (for development)"""
    celery_app.start(['beat', '--loglevel=info'])

if __name__ == '__main__':
    # Start worker if run directly
    start_celery_worker()
