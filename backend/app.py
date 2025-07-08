from flask import Flask, render_template
from flask_cors import CORS
from models import db, User
from auth_routes import auth_bp
from admin_routes import admin_bp, init_cache
from user_routes import user_bp
from werkzeug.security import generate_password_hash
from flask_apscheduler import APScheduler
from datetime import datetime
import os
import logging

from extensions import mail  
from reminder_job import send_daily_reminders, send_monthly_activity_report  
from user_routes import user_bp, init_user_cache


REDIS_AVAILABLE = False


try:
    from celery_tasks import celery_app
    CELERY_AVAILABLE = True
    logging.info("✅ Celery configuration imported successfully")
except ImportError as e:
    CELERY_AVAILABLE = False
    logging.warning(f"⚠️ Celery not available: {e}. Background tasks disabled.")

class Config:
    SCHEDULER_API_ENABLED = True
    
 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
  
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'rajveerkharade9@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'vrjdfdrzowqusred')
 
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    CORS_ORIGINS = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174", 
        "http://127.0.0.1:5174",
        "http://localhost:5175", 
        "http://127.0.0.1:5175",
        "http://localhost:5176", 
        "http://127.0.0.1:5176",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Dynamic configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'users.db')
    
  
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
  
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    db.init_app(app)
    mail.init_app(app)
    init_cache(app)  # Admin cache
    init_user_cache(app)
  
    init_cache(app)
  
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")


    with app.app_context():
        try:
            db.create_all()
            create_default_admin(app)
        except Exception as e:
            app.logger.error(f'Database initialization error: {str(e)}')

    
    @app.route('/')
    def index():
        """API root endpoint"""
        return {
            'status': 'success',
            'message': 'Vehicle Parking System Backend API is running!',
            'version': '1.0.0',
            'endpoints': {
                'api_info': '/api',
                'health_check': '/health',
                'auth': '/auth',
                'admin': '/admin', 
                'user': '/user'
            }
        }
    
    @app.route('/api')
    def api_info():
        return {
            'status': 'success', 
            'message': 'Vehicle Parking System API is running!',
            'version': '1.0.0',
            'features': {
                'redis_caching': False,
                'celery_tasks': CELERY_AVAILABLE,
                'flask_api': True,
                'vue_frontend': True,
                'bootstrap_ui': True,
                'sqlite_db': True
            },
            'endpoints': {
                'auth': '/auth',
                'admin': '/admin', 
                'user': '/user'
            },
            'caching': {
                'type': 'Flask-Caching',
                'status': 'memory_cache'
            }
        }
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        # Test caching system
        redis_status = 'memory_cache'
        
        return {
            'status': 'healthy',
            'database': db_status,
            'redis': redis_status,
            'celery': 'available' if CELERY_AVAILABLE else 'not_available',
            'timestamp': datetime.utcnow().isoformat()
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal server error: {str(error)}')
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Access forbidden'}, 403

    return app

def create_default_admin(app):
    """Create default admin user if not exists"""
    try:
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
            admin_user = User(
                username='admin',
                password=hashed_password,
                role='admin',
                fullname='System Administrator',
                address='Head Office',
                pincode='000000'
            )
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info('✅ Default admin user created (username: admin, password: admin123)')
    except Exception as e:
        app.logger.error(f'Failed to create default admin user: {str(e)}')
        db.session.rollback()

def setup_scheduler(app):
    """Setup and configure scheduler"""
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    def daily_reminder_wrapper():
        with app.app_context():
            try:
                send_daily_reminders()
                app.logger.info('✅ Daily reminders sent successfully')
            except Exception as e:
                app.logger.error(f'❌ Failed to send daily reminders: {str(e)}')

    def monthly_report_wrapper():
        with app.app_context():
            try:
                send_monthly_activity_report()
                app.logger.info('✅ Monthly reports sent successfully')
            except Exception as e:
                app.logger.error(f'❌ Failed to send monthly reports: {str(e)}')


    scheduler.add_job(
        id='DailyReminderJob',
        func=daily_reminder_wrapper,
        trigger='cron',
        hour=18,  # 6 PM
        minute=0,
        replace_existing=True
    )
    
  
    scheduler.add_job(
        id='MonthlyReportJob',
        func=monthly_report_wrapper,
        trigger='cron',
        day=1,  
        hour=9,  
        minute=0,
        replace_existing=True
    )
    
    app.logger.info(f'✅ Scheduler started:')
    app.logger.info(f'   📅 Daily reminders: Every day at 6:00 PM')
    app.logger.info(f'   📊 Monthly reports: 1st of every month at 9:00 AM')
    
    return scheduler


if __name__ == '__main__':
    # Create app
    app = create_app()
    
    # Setup scheduler
    scheduler = setup_scheduler(app)
    
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.logger.info(f'🚀 Starting Vehicle Parking System API on {host}:{port}')
    app.logger.info(f'🔧 Debug mode: {debug}')
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        app.logger.info('👋 Shutting down gracefully...')
        scheduler.shutdown()
    except Exception as e:
        app.logger.error(f'❌ Failed to start application: {str(e)}')
        if scheduler:
            scheduler.shutdown()
