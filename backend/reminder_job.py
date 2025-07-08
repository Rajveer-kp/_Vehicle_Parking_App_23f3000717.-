# reminder_job.py - Enhanced with Daily Reminders and Monthly Reports

from flask import current_app
from models import db, User, ParkingHistory, ParkingLot
from extensions import mail
from flask_mail import Message
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import csv
import io
import os
from collections import defaultdict

def send_daily_reminders():
    """Send daily reminders to users who haven't visited recently"""
    try:
        # Find users who haven't booked parking in the last 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        inactive_users = db.session.query(User).filter(
            User.role == 'user',
            ~User.id.in_(
                db.session.query(ParkingHistory.user_id).filter(
                    ParkingHistory.timestamp >= cutoff_date
                )
            )
        ).all()

        reminders_sent = 0
        for user in inactive_users:
            try:
                subject = '🚗 Daily Parking Reminder - Book Your Spot!'
                
                html_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #007bff; margin: 0;">🚗 Parking Reminder</h1>
                            <p style="color: #666; margin: 10px 0 0 0;">Vehicle Parking System</p>
                        </div>
                        
                        <div style="background-color: #e3f2fd; border: 1px solid #2196f3; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                            <h2 style="color: #1976d2; margin: 0 0 10px 0;">💡 Haven't visited lately?</h2>
                            <p style="color: #1976d2; margin: 0;">Hi {user.fullname or user.username}, we noticed you haven't booked a parking spot recently. Don't forget to reserve your spot if you need one!</p>
                        </div>
                        
                        <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                            <h3 style="color: #333; margin: 0 0 15px 0;">Quick Actions:</h3>
                            <ul style="color: #666; padding-left: 20px;">
                                <li>🅿️ Browse available parking lots</li>
                                <li>� Book a parking spot for today</li>
                                <li>⏰ Schedule recurring bookings</li>
                                <li>📊 View your parking history</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #666; margin: 0;">Log in to the parking system to manage your bookings!</p>
                            <p style="color: #999; font-size: 12px; margin: 10px 0 0 0;">This reminder is sent daily at {datetime.now().strftime('%I:%M %p')}.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                msg = Message(
                    subject=subject,
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[user.username],  # Assuming username is email
                    html=html_body
                )
                mail.send(msg)
                reminders_sent += 1
                current_app.logger.info(f"📨 Sent daily reminder to {user.username}")
                
            except Exception as e:
                current_app.logger.error(f"❌ Failed to send daily reminder to {user.username}: {e}")

        current_app.logger.info(f"✅ Daily reminders completed: {reminders_sent} sent")
        return reminders_sent
        
    except Exception as e:
        current_app.logger.error(f"❌ Daily reminder job failed: {e}")
        return 0

def send_monthly_activity_report():
    """Send monthly activity reports to all users"""
    try:
        # Get current month data
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        
        # Get previous month for the report
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year
            
        report_start = datetime(prev_year, prev_month, 1)
        report_end = start_of_month
        month_name = report_start.strftime('%B %Y')
        
        users = User.query.filter_by(role='user').all()
        reports_sent = 0
        
        for user in users:
            try:
                # Get user's parking data for the month
                user_parkings = ParkingHistory.query.filter(
                    ParkingHistory.user_id == user.id,
                    ParkingHistory.timestamp >= report_start,
                    ParkingHistory.timestamp < report_end
                ).all()
                
                if not user_parkings:
                    continue  # Skip users with no activity
                
                # Calculate statistics
                total_bookings = len(user_parkings)
                
                # Most used parking lot
                lot_usage = defaultdict(int)
                total_cost = 0
                
                for parking in user_parkings:
                    if parking.lot:
                        lot_usage[parking.lot.name] += 1
                        # Calculate cost (assuming 1 hour minimum)
                        hours = 1
                        if parking.status == 'Completed':
                            # Calculate actual hours if available
                            pass
                        total_cost += parking.lot.price_per_hour * hours
                
                most_used_lot = max(lot_usage.items(), key=lambda x: x[1]) if lot_usage else ("N/A", 0)
                
                # Generate HTML report
                html_report = generate_monthly_report_html(
                    user, month_name, total_bookings, most_used_lot, total_cost, user_parkings
                )
                
                subject = f'📊 Monthly Parking Report - {month_name}'
                
                msg = Message(
                    subject=subject,
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[user.username],
                    html=html_report
                )
                mail.send(msg)
                reports_sent += 1
                current_app.logger.info(f"� Sent monthly report to {user.username}")
                
            except Exception as e:
                current_app.logger.error(f"❌ Failed to send monthly report to {user.username}: {e}")
        
        current_app.logger.info(f"✅ Monthly reports completed: {reports_sent} sent")
        return reports_sent
        
    except Exception as e:
        current_app.logger.error(f"❌ Monthly report job failed: {e}")
        return 0

def generate_monthly_report_html(user, month_name, total_bookings, most_used_lot, total_cost, parkings):
    """Generate HTML for monthly activity report"""
    
    # Create parking details table
    parking_rows = ""
    for parking in parkings[-10:]:  # Show last 10 bookings
        status_color = "#28a745" if parking.status == "Completed" else "#ffc107" if parking.status == "Parked" else "#dc3545"
        parking_rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{parking.timestamp.strftime('%m/%d/%Y')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{parking.lot.name if parking.lot else 'N/A'}</td>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{parking.vehicle_no}</td>
            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">
                <span style="color: {status_color}; font-weight: bold;">{parking.status}</span>
            </td>
        </tr>
        """
    
    html_report = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 700px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #007bff; padding-bottom: 20px;">
                <h1 style="color: #007bff; margin: 0;">📊 Monthly Parking Report</h1>
                <h2 style="color: #666; margin: 10px 0 0 0;">{month_name}</h2>
                <p style="color: #999; margin: 5px 0 0 0;">Report for {user.fullname or user.username}</p>
            </div>
            
            <!-- Summary Cards -->
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 30px;">
                <div style="flex: 1; min-width: 150px; background-color: #e3f2fd; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="color: #1976d2; margin: 0; font-size: 24px;">{total_bookings}</h3>
                    <p style="color: #1976d2; margin: 5px 0 0 0; font-weight: bold;">Total Bookings</p>
                </div>
                <div style="flex: 1; min-width: 150px; background-color: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="color: #388e3c; margin: 0; font-size: 20px;">{most_used_lot[0]}</h3>
                    <p style="color: #388e3c; margin: 5px 0 0 0; font-weight: bold;">Most Used Lot</p>
                    <p style="color: #666; margin: 0; font-size: 12px;">({most_used_lot[1]} times)</p>
                </div>
                <div style="flex: 1; min-width: 150px; background-color: #fff3e0; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="color: #f57c00; margin: 0; font-size: 24px;">${total_cost:.2f}</h3>
                    <p style="color: #f57c00; margin: 5px 0 0 0; font-weight: bold;">Total Spent</p>
                </div>
            </div>
            
            <!-- Recent Bookings -->
            <div style="margin-bottom: 30px;">
                <h3 style="color: #333; margin: 0 0 15px 0;">Recent Bookings</h3>
                <table style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background-color: #007bff; color: white;">
                            <th style="padding: 12px; text-align: left;">Date</th>
                            <th style="padding: 12px; text-align: left;">Parking Lot</th>
                            <th style="padding: 12px; text-align: left;">Vehicle</th>
                            <th style="padding: 12px; text-align: left;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {parking_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Tips -->
            <div style="background-color: #f0f8ff; border: 1px solid #007bff; border-radius: 8px; padding: 20px;">
                <h3 style="color: #007bff; margin: 0 0 10px 0;">💡 Tips for Next Month</h3>
                <ul style="color: #333; margin: 0; padding-left: 20px;">
                    <li>Book your parking spots in advance to guarantee availability</li>
                    <li>Consider using recurring bookings for regular schedules</li>
                    <li>Check out different parking locations to find the best rates</li>
                    <li>Use the mobile app for quick bookings on the go</li>
                </ul>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; margin-top: 30px; border-top: 1px solid #dee2e6; padding-top: 20px;">
                <p style="color: #666; margin: 0;">Thank you for using our Vehicle Parking System!</p>
                <p style="color: #999; font-size: 12px; margin: 10px 0 0 0;">
                    Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_report

def generate_user_parking_csv(user_id):
    """Generate CSV export for user's parking history"""
    try:
        from flask import current_app
        current_app.logger.info(f"🔍 Starting CSV generation for user {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            current_app.logger.error(f"❌ User {user_id} not found")
            return None, "User not found"
            
        current_app.logger.info(f"✅ Found user: {user.username}")
            
        # Get all parking history for the user
        parkings = ParkingHistory.query.filter_by(user_id=user_id).order_by(ParkingHistory.timestamp.desc()).all()
        
        current_app.logger.info(f"📊 Found {len(parkings)} parking records")
        
        # Create CSV content even if no records (empty CSV with headers)
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Booking ID', 'Date', 'Entry Time', 'Exit Time', 'Parking Lot Name', 'Lot ID', 
            'Slot ID', 'Spot ID', 'Vehicle Number', 'Status', 'Price per Hour (₹)', 
            'Duration (Hours)', 'Total Cost (₹)', 'Location Address', 'Remarks'
        ])
        
        if not parkings:
            current_app.logger.warning(f"⚠️ No parking history found for user {user_id}, creating empty CSV")
            # Write a note row for empty data
            writer.writerow([
                'No Data', 'No parking history found', '', '', '', '', '', '', '', '', '', '', '', '', 'No parking records available for this user'
            ])
        else:
            # Write data rows
            for parking in parkings:
                duration = "N/A"
                total_cost = "N/A"
                exit_time = "N/A"
                
                # Try to get duration and cost information
                if parking.status == "Completed":
                    duration = "1.0"  # Default to 1 hour if not available
                    if parking.lot:
                        # Calculate total cost based on price per hour
                        total_cost = f"{float(parking.lot.price_per_hour):.2f}"
                
                # Format times
                entry_time = parking.timestamp.strftime('%Y-%m-%d %H:%M:%S') if parking.timestamp else 'N/A'
                
                writer.writerow([
                    parking.id,
                    parking.timestamp.strftime('%Y-%m-%d') if parking.timestamp else 'N/A',
                    entry_time,
                    exit_time,  # Would need to be tracked in a more complete system
                    parking.lot.name if parking.lot else 'N/A',
                    parking.lot_id or 'N/A',
                    'N/A',  # slot_id - would need to be added to schema
                    parking.spot_id or 'N/A',  # Use the actual spot_id from the model
                    parking.vehicle_no,
                    parking.status,
                    f"{float(parking.lot.price_per_hour):.2f}" if parking.lot else 'N/A',
                    duration,
                    total_cost,
                    parking.lot.address if parking.lot else 'N/A',
                    ''  # No remarks field in current model
                ])
        
        csv_content = output.getvalue()
        output.close()
        
        current_app.logger.info(f"✅ CSV generation completed for user {user_id}. Content length: {len(csv_content)}")
        
        return csv_content, None
        
    except Exception as e:
        current_app.logger.error(f"❌ CSV generation failed for user {user_id}: {e}")
        return None, str(e)
