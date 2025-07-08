from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_caching import Cache
from models import db, User, ParkingLot, ParkingHistory
from datetime import datetime, timedelta
from sqlalchemy import or_, func, and_
from functools import wraps
import hashlib
import logging

# Initialize cache
cache = Cache()

def init_user_cache(app):
    """Initialize cache with app for user routes"""
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# Cache decorator for user routes
def cache_user_data(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Generate cache key based on function name, args, and request parameters
                cache_key = f"user:{f.__name__}:{hashlib.md5(str(args + tuple(sorted(request.args.items()))).encode()).hexdigest()}"
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            except Exception as e:
                logging.warning(f"Cache read error: {e}")
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            
            try:
                cache.set(cache_key, result, timeout=timeout)
            except Exception as e:
                logging.warning(f"Cache write error: {e}")
            
            return result
        return decorated_function
    return decorator

# Cache invalidation helper
def invalidate_user_cache_pattern(pattern):
    """Invalidate cache entries matching pattern"""
    try:
        cache.clear()
        logging.info(f"Cleared user cache")
    except Exception as e:
        logging.warning(f"Cache invalidation error: {e}")

user_bp = Blueprint('user', __name__)

# -----------------------
# 📘 Route: User's Parking History
# -----------------------
@user_bp.route('/parking-history', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def get_user_parking_history():
    try:
        # Get user ID from headers
        user_id = request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401

        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get parking history - using your exact model fields
        try:
            history = db.session.query(ParkingHistory)\
                .filter(ParkingHistory.user_id == user_id)\
                .order_by(ParkingHistory.timestamp.desc())\
                .limit(50)\
                .all()
        except Exception as query_error:
            logging.error(f"Database query error: {str(query_error)}")
            return jsonify({'error': 'Database error occurred'}), 500

        result = []
        for h in history:
            try:
                # Get lot information safely using the relationship or direct query
                lot = None
                if h.lot_id:
                    try:
                        lot = ParkingLot.query.get(h.lot_id)
                    except Exception as lot_error:
                        logging.warning(f"Error fetching lot {h.lot_id}: {str(lot_error)}")
                
                # Ensure lot_id is always included and valid
                lot_id = h.lot_id if h.lot_id else None
                
                result.append({
                    'id': h.id,
                    'booking_id': h.id,  # For compatibility
                    'lot_id': lot_id,  # ✅ CRITICAL: Include lot_id
                    'parking_lot_id': lot_id,  # ✅ Alternative field name
                    'location': lot.name if lot else 'Unknown Location',
                    'parking_lot_name': lot.name if lot else 'Unknown Location',  # Alternative field name
                    'address': lot.address if lot else 'Unknown Address',
                    'parking_lot_address': lot.address if lot else 'Unknown Address',  # Alternative field name
                    'vehicle_no': h.vehicle_no or 'N/A',
                    'vehicle_number': h.vehicle_no or 'N/A',  # Alternative field name
                    'spot_id': h.spot_id,
                    'parking_spot_id': h.spot_id,  # Alternative field name
                    'entry_time': h.timestamp.isoformat() if h.timestamp else None,
                    'start_time': h.timestamp.isoformat() if h.timestamp else None,  # Alternative field name
                    'timestamp': h.timestamp.isoformat() if h.timestamp else None,
                    'exit_time': None,  # Your model doesn't have this field
                    'end_time': None,  # Alternative field name
                    'duration_hours': 0,  # Can't calculate without exit_time
                    'total_cost': 0,  # Can't calculate without exit_time
                    'amount': 0,  # Alternative field name
                    'total_amount': 0,  # Alternative field name
                    'status': h.status or 'Unknown',
                    'price_per_hour': lot.price_per_hour if lot else 0,
                    'hourly_rate': lot.price_per_hour if lot else 0  # Alternative field name
                })
            except Exception as item_error:
                logging.warning(f"Error processing history item {h.id}: {str(item_error)}")
                # Still include the item with minimal data to prevent frontend errors
                result.append({
                    'id': h.id,
                    'booking_id': h.id,
                    'lot_id': h.lot_id if hasattr(h, 'lot_id') else None,
                    'parking_lot_id': h.lot_id if hasattr(h, 'lot_id') else None,
                    'location': 'Error Loading Location',
                    'parking_lot_name': 'Error Loading Location',
                    'address': 'Error Loading Address',
                    'parking_lot_address': 'Error Loading Address',
                    'vehicle_no': h.vehicle_no if hasattr(h, 'vehicle_no') else 'N/A',
                    'vehicle_number': h.vehicle_no if hasattr(h, 'vehicle_no') else 'N/A',
                    'spot_id': h.spot_id if hasattr(h, 'spot_id') else 'N/A',
                    'parking_spot_id': h.spot_id if hasattr(h, 'spot_id') else 'N/A',
                    'entry_time': h.timestamp.isoformat() if hasattr(h, 'timestamp') and h.timestamp else None,
                    'start_time': h.timestamp.isoformat() if hasattr(h, 'timestamp') and h.timestamp else None,
                    'timestamp': h.timestamp.isoformat() if hasattr(h, 'timestamp') and h.timestamp else None,
                    'exit_time': None,
                    'end_time': None,
                    'duration_hours': 0,
                    'total_cost': 0,
                    'amount': 0,
                    'total_amount': 0,
                    'status': h.status if hasattr(h, 'status') else 'Unknown',
                    'price_per_hour': 50,  # Default rate
                    'hourly_rate': 50
                })
                continue

        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in get_user_parking_history: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# -----------------------
# 🚗 Route: Get All Parking Lots
# -----------------------
@user_bp.route('/parking-lots', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
@cache_user_data(timeout=600)  # Cache for 10 minutes
def get_all_parking_lots():
    try:
        search_query = request.args.get('search', '').strip()
        
        # Simple query using your exact model structure
        lots_query = ParkingLot.query
        
        # Apply search filter if provided
        if search_query:
            lots_query = lots_query.filter(
                or_(
                    ParkingLot.name.ilike(f'%{search_query}%'),
                    ParkingLot.address.ilike(f'%{search_query}%'),
                    ParkingLot.pincode.ilike(f'%{search_query}%')
                )
            )
        
        lots = lots_query.all()
        
        result = []
        for lot in lots:
            try:
                # Calculate occupied spots using your model structure
                occupied_count = 0
                try:
                    occupied_count = db.session.query(ParkingHistory)\
                        .filter_by(lot_id=lot.id, status='Parked')\
                        .count()
                except:
                    occupied_count = 0
                
                available = max(0, (lot.max_spots or 0) - occupied_count)
                
                result.append({
                    'id': lot.id,
                    'name': lot.name or 'Unnamed Lot',
                    'address': lot.address or 'No Address',
                    'pincode': lot.pincode or '',
                    'price_per_hour': lot.price_per_hour or 0,
                    'max_spots': lot.max_spots or 0,
                    'available_spots': available,
                    'occupied_spots': occupied_count,
                    'occupancy_rate': round((occupied_count / lot.max_spots) * 100, 1) if lot.max_spots and lot.max_spots > 0 else 0
                })
            except Exception as lot_error:
                logging.warning(f"Error processing lot {lot.id}: {str(lot_error)}")
                continue
        
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in get_all_parking_lots: {str(e)}")
        return jsonify({'error': f'Failed to fetch parking lots: {str(e)}'}), 500

# -----------------------
# 🔍 Route: Search Parking
# -----------------------
@user_bp.route('/search-parking', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
@cache_user_data(timeout=300)  # Cache for 5 minutes
def search_parking():
    try:
        query = request.args.get('q', '').strip()
        
        # Simple search query using your model structure
        lots_query = ParkingLot.query
        
        if query:
            lots_query = lots_query.filter(
                or_(
                    ParkingLot.address.ilike(f'%{query}%'),
                    ParkingLot.pincode.ilike(f'%{query}%'),
                    ParkingLot.name.ilike(f'%{query}%')
                )
            )
        
        lots = lots_query.all()
        
        result = []
        for lot in lots:
            try:
                # Calculate availability using your model
                occupied_count = db.session.query(ParkingHistory)\
                    .filter_by(lot_id=lot.id, status='Parked')\
                    .count()
                
                available_spots = max(0, (lot.max_spots or 0) - occupied_count)
                
                result.append({
                    'id': lot.id,
                    'name': lot.name or 'Unnamed Lot',
                    'address': lot.address or 'No Address',
                    'pincode': lot.pincode or '',
                    'price_per_hour': lot.price_per_hour or 0,
                    'max_spots': lot.max_spots or 0,
                    'available_spots': available_spots,
                    'occupied_spots': occupied_count
                })
            except Exception as lot_error:
                logging.warning(f"Error processing search lot {lot.id}: {str(lot_error)}")
                continue
        
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in search_parking: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

# -----------------------
# 🅿️ Route: Book a Parking Spot
# -----------------------
@user_bp.route('/book-spot', methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def book_parking():
    try:
        data = request.get_json()
        
        # Get user ID from headers
        user_id = request.headers.get('X-User-ID')
        vehicle_no = data.get('vehicleNo') or data.get('vehicle_no')
        lot_id = data.get('lotId') or data.get('lot_id')
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        if not vehicle_no or not lot_id:
            return jsonify({'error': 'Missing vehicle number or parking lot ID'}), 400

        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Validate parking lot exists
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404

        # ✅ MODIFIED: Check if the SAME VEHICLE is already parked (instead of blocking all user bookings)
        existing_vehicle_booking = ParkingHistory.query.filter_by(
            vehicle_no=vehicle_no.upper(),
            status='Parked'
        ).first()
        
        if existing_vehicle_booking:
            return jsonify({'error': 'This vehicle is already parked in another location'}), 400

        # Get occupied spots
        occupied_spots = db.session.query(ParkingHistory.spot_id)\
            .filter_by(lot_id=lot.id, status='Parked')\
            .all()
        
        occupied_spot_ids = {spot.spot_id for spot in occupied_spots}

        # Find the first available spot
        available_spot = None
        for i in range(1, lot.max_spots + 1):
            if i not in occupied_spot_ids:
                available_spot = i
                break

        if not available_spot:
            return jsonify({'error': 'No available spots in this parking lot'}), 409

        # Create booking using your exact model structure
        new_entry = ParkingHistory(
            user_id=user_id,
            lot_id=lot.id,
            spot_id=available_spot,
            vehicle_no=vehicle_no.upper(),
            timestamp=datetime.utcnow(),
            status='Parked'
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        # Invalidate related caches
        invalidate_user_cache_pattern("user:*")
        
        return jsonify({
            'message': f'Parking booked successfully at spot {available_spot}',
            'booking_id': new_entry.id,
            'spot_number': available_spot,
            'lot_name': lot.name,
            'address': lot.address,
            'price_per_hour': lot.price_per_hour,
            'entry_time': new_entry.timestamp.isoformat()
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in book_parking: {str(e)}")
        return jsonify({'error': 'Booking failed. Please try again.'}), 500

# -----------------------
# 🔓 Route: Release a Parking Spot
# -----------------------
@user_bp.route('/release-spot', methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def release_parking():
    try:
        data = request.get_json()
        user_id = request.headers.get('X-User-ID')
        history_id = data.get('historyId') or data.get('history_id')
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        if not history_id:
            return jsonify({'error': 'Booking ID is required'}), 400

        # Find the parking record
        history = ParkingHistory.query.filter_by(
            id=history_id,
            user_id=user_id,
            status='Parked'
        ).first()
        
        if not history:
            return jsonify({'error': 'Active parking record not found'}), 404

        # Since your model doesn't have exit_time, we'll just update the status
        history.status = 'Completed'
        db.session.commit()
        
        # Invalidate related caches
        invalidate_user_cache_pattern("user:*")
        
        return jsonify({
            'message': 'Parking spot released successfully',
            'duration_hours': 0,  # Can't calculate without exit_time field
            'total_cost': 0,  # Can't calculate without exit_time field
            'exit_time': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in release_parking: {str(e)}")
        return jsonify({'error': 'Failed to release parking spot'}), 500

# -----------------------
# 📊 Route: Parking Summary
# -----------------------
# Add this after your existing parking-summary route

# -----------------------
# 👤 Route: User's Personal Parking Summary
# -----------------------
@user_bp.route('/my-parking-summary', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def my_parking_summary():
    try:
        # Get user ID from request parameters or headers
        user_id = request.args.get('user_id') or request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's personal parking statistics
        total_bookings = ParkingHistory.query.filter_by(user_id=user_id).count()
        active_bookings = ParkingHistory.query.filter_by(user_id=user_id, status='Parked').count()
        completed_bookings = ParkingHistory.query.filter_by(user_id=user_id, status='Completed').count()
        
        # Calculate cancelled bookings if you have that status
        cancelled_bookings = ParkingHistory.query.filter_by(user_id=user_id, status='Cancelled').count()
        
        # Get current active parking session
        current_parking = ParkingHistory.query.filter_by(
            user_id=user_id, 
            status='Parked'
        ).first()
        
        current_parking_data = None
        if current_parking:
            # Get parking lot details
            lot = ParkingLot.query.get(current_parking.lot_id)
            current_parking_data = {
                'id': current_parking.id,
                'vehicle_no': current_parking.vehicle_no,
                'location': lot.name if lot else 'Unknown Location',
                'address': lot.address if lot else 'Unknown Address',
                'spot_id': current_parking.spot_id,
                'entry_time': current_parking.timestamp.isoformat() if current_parking.timestamp else None,
                'price_per_hour': lot.price_per_hour if lot else 0
            }
        
        # Get recent bookings (last 10)
        recent_bookings_query = ParkingHistory.query.filter_by(user_id=user_id)\
            .order_by(ParkingHistory.timestamp.desc())\
            .limit(10)\
            .all()
        
        recent_bookings = []
        total_amount_spent = 0  # You can calculate this if you have payment records
        
        for booking in recent_bookings_query:
            try:
                # Get parking lot details
                lot = ParkingLot.query.get(booking.lot_id)
                
                # Estimate amount (you can improve this calculation)
                estimated_amount = 0
                if lot and lot.price_per_hour:
                    # For completed bookings, estimate 2 hours average
                    # For active bookings, calculate current duration
                    if booking.status == 'Completed':
                        estimated_amount = lot.price_per_hour * 2  # Assume 2 hours average
                    elif booking.status == 'Parked':
                        # Calculate current duration in hours
                        duration_hours = (datetime.utcnow() - booking.timestamp).total_seconds() / 3600
                        estimated_amount = lot.price_per_hour * max(1, duration_hours)
                
                total_amount_spent += estimated_amount
                
                recent_bookings.append({
                    'id': booking.id,
                    'location': lot.name if lot else 'Unknown Location',
                    'address': lot.address if lot else 'Unknown Address',
                    'vehicle_no': booking.vehicle_no,
                    'spot_id': booking.spot_id,
                    'entry_time': booking.timestamp.isoformat() if booking.timestamp else None,
                    'status': booking.status.lower() if booking.status else 'unknown',
                    'amount': round(estimated_amount, 2)
                })
            except Exception as booking_error:
                logging.warning(f"Error processing booking {booking.id}: {str(booking_error)}")
                continue
        
        # Get user registration date (assuming you have created_at or similar field)
        member_since = '2024-01-01'  # Default fallback
        if hasattr(user, 'created_at') and user.created_at:
            member_since = user.created_at.strftime('%Y-%m-%d')
        elif hasattr(user, 'timestamp') and user.timestamp:
            member_since = user.timestamp.strftime('%Y-%m-%d')
        
        return jsonify({
            'user_id': int(user_id),
            'username': user.username,
            'fullname': user.fullname,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_amount_spent': round(total_amount_spent, 2),
            'current_parking': current_parking_data,
            'recent_bookings': recent_bookings,
            'last_updated': datetime.utcnow().isoformat(),
            'member_since': member_since,
            'membership_status': 'Active'  # You can make this dynamic based on your business logic
        }), 200
        
    except Exception as e:
        logging.error(f"Error in my_parking_summary: {str(e)}")
        return jsonify({'error': f'Failed to fetch user parking summary: {str(e)}'}), 500

# -----------------------
# 🚪 Route: Exit Current Parking
# -----------------------
@user_bp.route('/exit-parking', methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def exit_parking():
    try:
        data = request.get_json()
        user_id = data.get('user_id') or request.headers.get('X-User-ID')
        booking_id = data.get('booking_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        if not booking_id:
            return jsonify({'error': 'Booking ID required'}), 400
        
        # Find the active parking session
        parking_session = ParkingHistory.query.filter_by(
            id=booking_id,
            user_id=user_id,
            status='Parked'
        ).first()
        
        if not parking_session:
            return jsonify({'error': 'Active parking session not found'}), 404
        
        # Get parking lot for cost calculation
        lot = ParkingLot.query.get(parking_session.lot_id)
        
        # Calculate duration and cost
        duration_hours = (datetime.utcnow() - parking_session.timestamp).total_seconds() / 3600
        total_cost = 0
        
        if lot and lot.price_per_hour:
            total_cost = lot.price_per_hour * max(1, duration_hours)  # Minimum 1 hour charge
        
        # Update status to completed
        parking_session.status = 'Completed'
        
        # If you want to add exit_time field to your model later, uncomment:
        # parking_session.exit_time = datetime.utcnow()
        
        db.session.commit()
        
        # Invalidate related caches
        invalidate_user_cache_pattern("user:*")
        
        return jsonify({
            'message': 'Successfully exited parking',
            'duration_hours': round(duration_hours, 2),
            'total_cost': round(total_cost, 2),
            'exit_time': datetime.utcnow().isoformat(),
            'spot_released': parking_session.spot_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in exit_parking: {str(e)}")
        return jsonify({'error': f'Failed to exit parking: {str(e)}'}), 500

# -----------------------
# 👤 Route: User's Profile Management
# -----------------------
@user_bp.route('/profile', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
@cache_user_data(timeout=300)  # Cache for 5 minutes
def get_user_profile():
    """Get user profile information with statistics"""
    try:
        user_id = request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user statistics using your model
        total_bookings = ParkingHistory.query.filter_by(user_id=user_id).count()
        active_bookings = ParkingHistory.query.filter_by(user_id=user_id, status='Parked').count()
        completed_bookings = ParkingHistory.query.filter_by(user_id=user_id, status='Completed').count()
        
        # Get current active parking
        current_parking = ParkingHistory.query.filter_by(user_id=user_id, status='Parked').first()
        current_parking_info = None
        
        if current_parking:
            lot = ParkingLot.query.get(current_parking.lot_id)
            current_parking_info = {
                'id': current_parking.id,
                'vehicle_no': current_parking.vehicle_no,
                'location': lot.name if lot else 'Unknown Location',
                'spot_id': current_parking.spot_id,
                'entry_time': current_parking.timestamp.isoformat() if current_parking.timestamp else None
            }
        
        # Calculate total spent (estimated)
        total_spent = 0
        completed_parkings = ParkingHistory.query.filter_by(user_id=user_id, status='Completed').all()
        for parking in completed_parkings:
            if parking.lot_id:
                lot = ParkingLot.query.get(parking.lot_id)
                if lot and lot.price_per_hour:
                    total_spent += lot.price_per_hour * 2  # Assume 2 hours average
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.username,  # Assuming username is email
            'fullname': user.fullname,
            'address': user.address,
            'pincode': user.pincode,
            'role': user.role,
            'profile_stats': {
                'total_bookings': total_bookings,
                'active_bookings': active_bookings,
                'completed_bookings': completed_bookings,
                'total_spent': round(total_spent, 2)
            },
            'current_parking': current_parking_info,
            'member_since': '2024-01-01',  # You can make this dynamic
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error in get_user_profile: {str(e)}")
        return jsonify({'error': 'Failed to fetch user profile'}), 500

@user_bp.route('/profile', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def update_user_profile():
    """Update user profile information"""
    try:
        user_id = request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        updated_fields = []
        
        if 'fullname' in data:
            user.fullname = data['fullname'].strip()
            updated_fields.append('fullname')
        
        if 'address' in data:
            user.address = data['address'].strip()
            updated_fields.append('address')
        
        if 'pincode' in data:
            user.pincode = data['pincode'].strip()
            updated_fields.append('pincode')
        
        # Save changes
        db.session.commit()
        
        # Invalidate cache
        invalidate_user_cache_pattern("user:*")
        
        return jsonify({
            'message': 'Profile updated successfully',
            'updated_fields': updated_fields,
            'user': {
                'id': user.id,
                'username': user.username,
                'fullname': user.fullname,
                'address': user.address,
                'pincode': user.pincode,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in update_user_profile: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@user_bp.route('/profile/password', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def change_password():
    """Change user password"""
    try:
        user_id = request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'error': 'All password fields are required'}), 400
        
        # Verify current password
        from werkzeug.security import check_password_hash, generate_password_hash
        
        if not check_password_hash(user.password, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in change_password: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500

# -----------------------
# 🧹 Cache Management Routes
# -----------------------
@user_bp.route('/cache/clear', methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def clear_user_cache():
    """Clear user-related cache"""
    try:
        invalidate_user_cache_pattern("user:*")
        return jsonify({'message': 'User cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@user_bp.route('/cache/stats', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def get_user_cache_stats():
    """Get cache statistics"""
    return jsonify({
        'cache_type': 'Simple in-memory cache',
        'status': 'Active',
        'note': 'User routes caching enabled'
    }), 200

# -----------------------
# 🅿️ Route: Get Individual Parking Lot Details
# -----------------------
@user_bp.route('/parking-lot/<int:lot_id>', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def get_parking_lot_details(lot_id):
    """Get detailed information about a specific parking lot"""
    try:
        if not lot_id:
            return jsonify({'error': 'Parking lot ID is required'}), 400
        
        # Get the parking lot
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Calculate current occupancy
        occupied_count = 0
        try:
            occupied_count = db.session.query(ParkingHistory)\
                .filter_by(lot_id=lot.id, status='Parked')\
                .count()
        except Exception as count_error:
            logging.warning(f"Error counting occupied spots for lot {lot_id}: {str(count_error)}")
            occupied_count = 0
        
        available_spots = max(0, (lot.max_spots or 0) - occupied_count)
        occupancy_rate = round((occupied_count / lot.max_spots) * 100, 1) if lot.max_spots and lot.max_spots > 0 else 0
        
        # Get currently occupied spots for this lot
        occupied_spots_query = db.session.query(ParkingHistory.spot_id)\
            .filter_by(lot_id=lot.id, status='Parked')\
            .all()
        
        occupied_spot_ids = [spot.spot_id for spot in occupied_spots_query]
        
        return jsonify({
            'id': lot.id,
            'name': lot.name or 'Unnamed Lot',
            'address': lot.address or 'No Address',
            'pincode': lot.pincode or '',
            'price_per_hour': lot.price_per_hour or 0,
            'hourly_rate': lot.price_per_hour or 0,  # Alternative field name
            'max_spots': lot.max_spots or 0,
            'total_spots': lot.max_spots or 0,  # Alternative field name
            'available_spots': available_spots,
            'occupied_spots': occupied_count,
            'occupancy_rate': occupancy_rate,
            'occupied_spot_ids': occupied_spot_ids,
            'status': 'active',
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid parking lot ID format'}), 400
    except Exception as e:
        logging.error(f"Error in get_parking_lot_details for lot {lot_id}: {str(e)}")
        return jsonify({'error': f'Failed to fetch parking lot details: {str(e)}'}), 500

# -----------------------
# 🅿️ Route: Get Individual Parking Lot Details (Handle null/undefined)
# -----------------------
@user_bp.route('/parking-lot/', methods=['GET'])
@user_bp.route('/parking-lot/<path:lot_id>', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
def get_parking_lot_details_fallback(lot_id=None):
    """Handle requests with null, undefined, or invalid lot_id"""
    try:
        # Handle various invalid inputs
        if not lot_id or lot_id in ['null', 'undefined', 'None', '']:
            return jsonify({
                'error': 'Invalid parking lot ID',
                'message': 'Parking lot ID cannot be null or undefined',
                'fallback_data': {
                    'id': None,
                    'name': 'Unknown Location',
                    'address': 'Address not available',
                    'price_per_hour': 50,  # Default rate
                    'hourly_rate': 50,
                    'max_spots': 0,
                    'available_spots': 0,
                    'occupied_spots': 0,
                    'occupancy_rate': 0
                }
            }), 400
        
        # Try to convert to integer
        try:
            lot_id_int = int(lot_id)
            return get_parking_lot_details(lot_id_int)
        except ValueError:
            return jsonify({
                'error': 'Invalid parking lot ID format',
                'message': f'Parking lot ID "{lot_id}" is not a valid number',
                'fallback_data': {
                    'id': None,
                    'name': 'Unknown Location',
                    'address': 'Address not available',
                    'price_per_hour': 50,  # Default rate
                    'hourly_rate': 50,
                    'max_spots': 0,
                    'available_spots': 0,
                    'occupied_spots': 0,
                    'occupancy_rate': 0
                }
            }), 400
            
    except Exception as e:
        logging.error(f"Error in parking lot details fallback for ID {lot_id}: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': str(e),
            'fallback_data': {
                'id': None,
                'name': 'Unknown Location',
                'address': 'Address not available',
                'price_per_hour': 50,  # Default rate
                'hourly_rate': 50,
                'max_spots': 0,
                'available_spots': 0,
                'occupied_spots': 0,
                'occupancy_rate': 0
            }
        }), 500

# CSV Export Routes
@user_bp.route('/export-csv', methods=['POST'])
@cross_origin()
def trigger_csv_export():
    """Trigger CSV export for user's parking history"""
    try:
        # Get user_id from header (consistent with other endpoints)
        user_id = request.headers.get('X-User-ID')
        logging.info(f"🔍 CSV export request - User ID: {user_id}")
        
        if not user_id:
            logging.error("❌ CSV export failed - No User ID provided")
            return jsonify({'error': 'User ID is required'}), 400
            
        user = User.query.get(user_id)
        if not user:
            logging.error(f"❌ CSV export failed - User {user_id} not found")
            return jsonify({'error': 'User not found'}), 404
            
        logging.info(f"✅ Found user: {user.username}")
            
        # Start async CSV generation (simulate background job)
        from reminder_job import generate_user_parking_csv
        
        logging.info(f"📊 Generating CSV for user {user.username}")
        csv_content, error = generate_user_parking_csv(user.id)
        
        if error:
            logging.error(f"❌ CSV generation failed: {error}")
            return jsonify({'error': error}), 400
            
        # In a real implementation, you would:
        # 1. Start a background job (Celery task)
        # 2. Store the CSV in a file or cloud storage
        # 3. Send email notification when ready
        # 4. Return job ID for status tracking
        
        # For now, we'll return the CSV content directly
        from flask import Response
        
        # Create response with CSV content
        response = Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=parking_history_{user.username}_{datetime.now().strftime("%Y%m%d")}.csv'
            }
        )
        
        logging.info(f"✅ CSV export generated for user {user.username}")
        
        return response
        
    except Exception as e:
        logging.error(f"❌ CSV export failed: {str(e)}")
        return jsonify({'error': 'CSV export failed', 'message': str(e)}), 500

@user_bp.route('/export-csv/status/<job_id>', methods=['GET'])
@cross_origin()
def check_csv_export_status(job_id):
    """Check status of CSV export job (placeholder for async implementation)"""
    try:
        # This would normally check the status of a background job
        # For now, we'll simulate a completed job
        
        return jsonify({
            'job_id': job_id,
            'status': 'completed',
            'message': 'CSV export completed successfully',
            'download_url': f'/user/download-csv/{job_id}',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        })
        
    except Exception as e:
        logging.error(f"❌ Error checking CSV export status: {str(e)}")
        return jsonify({'error': 'Failed to check export status', 'message': str(e)}), 500

@user_bp.route('/download-csv/<job_id>', methods=['GET'])
@cross_origin() 
def download_csv_export(job_id):
    """Download completed CSV export (placeholder for async implementation)"""
    try:
        # This would normally serve a file from storage
        # For now, we'll redirect to the main export endpoint
        
        return jsonify({
            'message': 'Use /export-csv endpoint for direct download',
            'job_id': job_id
        })
        
    except Exception as e:
        logging.error(f"❌ Error downloading CSV: {str(e)}")
        return jsonify({'error': 'Download failed', 'message': str(e)}), 500

# Manual trigger routes for testing scheduled jobs
@user_bp.route('/trigger-daily-reminder', methods=['POST'])
@cross_origin()
def trigger_daily_reminder():
    """Manually trigger daily reminder (for testing)"""
    try:
        from reminder_job import send_daily_reminders
        
        reminders_sent = send_daily_reminders()
        
        return jsonify({
            'status': 'success',
            'message': f'Daily reminders triggered successfully',
            'reminders_sent': reminders_sent
        })
        
    except Exception as e:
        logging.error(f"❌ Error triggering daily reminder: {str(e)}")
        return jsonify({'error': 'Failed to trigger daily reminder', 'message': str(e)}), 500

@user_bp.route('/trigger-monthly-report', methods=['POST'])
@cross_origin()
def trigger_monthly_report():
    """Manually trigger monthly report (for testing)"""
    try:
        from reminder_job import send_monthly_activity_report
        
        reports_sent = send_monthly_activity_report()
        
        return jsonify({
            'status': 'success',
            'message': f'Monthly reports triggered successfully',
            'reports_sent': reports_sent
        })
        
    except Exception as e:
        logging.error(f"❌ Error triggering monthly report: {str(e)}")
        return jsonify({'error': 'Failed to trigger monthly report', 'message': str(e)}), 500

# -----------------------
# 🏠 Route: User Dashboard
# -----------------------
@user_bp.route('/dashboard', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
@cache_user_data(timeout=180)  # Cache for 3 minutes
def get_user_dashboard():
    """Get comprehensive user dashboard data"""
    try:
        user_id = request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({'error': 'User authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get comprehensive statistics
        total_bookings = ParkingHistory.query.filter_by(user_id=user_id).count()
        active_bookings = ParkingHistory.query.filter_by(user_id=user_id, status='Parked').count()
        completed_bookings = ParkingHistory.query.filter_by(user_id=user_id, status='Completed').count()
        
        # Get current active parking
        current_parking = ParkingHistory.query.filter_by(user_id=user_id, status='Parked').first()
        current_parking_details = None
        
        if current_parking:
            lot = ParkingLot.query.get(current_parking.lot_id)
            duration_hours = (datetime.utcnow() - current_parking.timestamp).total_seconds() / 3600
            current_cost = lot.price_per_hour * duration_hours if lot else 0
            
            current_parking_details = {
                'id': current_parking.id,
                'vehicle_no': current_parking.vehicle_no,
                'location': lot.name if lot else 'Unknown Location',
                'address': lot.address if lot else 'Unknown Address',
                'spot_id': current_parking.spot_id,
                'entry_time': current_parking.timestamp.isoformat() if current_parking.timestamp else None,
                'duration_hours': round(duration_hours, 2),
                'current_cost': round(current_cost, 2),
                'price_per_hour': lot.price_per_hour if lot else 0
            }
        
        # Get recent activity (last 5 bookings)
        recent_activity = ParkingHistory.query.filter_by(user_id=user_id)\
            .order_by(ParkingHistory.timestamp.desc())\
            .limit(5).all()
        
        activity_list = []
        for activity in recent_activity:
            lot = ParkingLot.query.get(activity.lot_id) if activity.lot_id else None
            activity_list.append({
                'id': activity.id,
                'location': lot.name if lot else 'Unknown Location',
                'vehicle_no': activity.vehicle_no,
                'timestamp': activity.timestamp.isoformat() if activity.timestamp else None,
                'status': activity.status,
                'spot_id': activity.spot_id
            })
        
        # Calculate monthly spending
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        monthly_bookings = ParkingHistory.query.filter(
            ParkingHistory.user_id == user_id,
            ParkingHistory.timestamp >= start_of_month,
            ParkingHistory.status == 'Completed'
        ).all()
        
        monthly_spending = 0
        for booking in monthly_bookings:
            if booking.lot_id:
                lot = ParkingLot.query.get(booking.lot_id)
                if lot and lot.price_per_hour:
                    monthly_spending += lot.price_per_hour * 2  # Assume 2 hours average
        
        # Quick actions available to user
        quick_actions = [
            {
                'id': 'book_parking',
                'title': 'Book Parking',
                'description': 'Find and book a parking spot',
                'icon': '🅿️',
                'endpoint': '/user/parking-lots'
            },
            {
                'id': 'view_history',
                'title': 'Parking History',
                'description': 'View your parking history',
                'icon': '📋',
                'endpoint': '/user/parking-history'
            },
            {
                'id': 'export_data',
                'title': 'Export Data',
                'description': 'Download your parking data as CSV',
                'icon': '📄',
                'endpoint': '/user/export-csv'
            },
            {
                'id': 'profile',
                'title': 'Profile Settings',
                'description': 'Manage your profile and settings',
                'icon': '👤',
                'endpoint': '/user/profile'
            }
        ]
        
        if current_parking:
            quick_actions.insert(0, {
                'id': 'exit_parking',
                'title': 'Exit Parking',
                'description': 'Exit your current parking spot',
                'icon': '🚪',
                'endpoint': '/user/exit-parking'
            })
        
        return jsonify({
            'user_info': {
                'id': user.id,
                'username': user.username,
                'fullname': user.fullname,
                'role': user.role
            },
            'statistics': {
                'total_bookings': total_bookings,
                'active_bookings': active_bookings,
                'completed_bookings': completed_bookings,
                'monthly_spending': round(monthly_spending, 2)
            },
            'current_parking': current_parking_details,
            'recent_activity': activity_list,
            'quick_actions': quick_actions,
            'notifications': {
                'has_active_parking': active_bookings > 0,
                'monthly_limit_warning': monthly_spending > 500,  # Warn if over $500/month
                'profile_incomplete': not all([user.fullname, user.address, user.pincode])
            },
            'last_updated': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error in get_user_dashboard: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500

