from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_caching import Cache
from models import db, ParkingLot, ParkingHistory, User
from sqlalchemy import text, func, and_
from datetime import datetime, timedelta
import hashlib
import json


REDIS_AVAILABLE = False

admin_bp = Blueprint('admin', __name__)


cache = Cache()

def init_cache(app):
    """Initialize cache with app"""
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

def make_cache_key(*args):
    """Generate cache key from arguments"""
    return hashlib.md5('_'.join(str(arg) for arg in args).encode()).hexdigest()

def clear_parking_cache():
    """Clear all parking-related cache entries"""
    cache.delete_memoized(get_parking_lots)
    cache.delete_memoized(get_parking_summary)
    cache.delete_memoized(get_users)

# -------------------- Add New Parking Lot --------------------
@admin_bp.route('/add-parking-lot', methods=['POST', 'OPTIONS'])
@cross_origin(origins='http://localhost:5173')
def add_parking_lot():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        data = request.get_json(force=True)

        name = data.get('name')
        address = data.get('address')
        pincode = data.get('pincode')
        price_per_hour = data.get('price')
        max_spots = data.get('maxSpots')
        created_by = data.get('adminId')

        if not all([name, address, pincode, price_per_hour, max_spots]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            price_per_hour = float(price_per_hour)
            max_spots = int(max_spots)
        except ValueError:
            return jsonify({'error': 'Invalid price or maxSpots format'}), 400

        new_lot = ParkingLot(
            name=name,
            address=address,
            pincode=pincode,
            price_per_hour=price_per_hour,
            max_spots=max_spots,
            created_by=created_by
        )

        db.session.add(new_lot)
        db.session.commit()

        # Clear cache after adding new lot
        clear_parking_cache()

        return jsonify({'message': 'Parking lot added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add parking lot: {str(e)}'}), 500

# -------------------- Get All Parking Lots (Cached) --------------------
@admin_bp.route('/parking-lots', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
@cache.memoize(timeout=300) 
def get_parking_lots():
    try:
        lots = ParkingLot.query.all()
        result = [
            {
                'id': lot.id,
                'name': lot.name,
                'address': lot.address,
                'pincode': lot.pincode,
                'price_per_hour': lot.price_per_hour,
                'max_spots': lot.max_spots,
                'created_by': lot.created_by
            }
            for lot in lots
        ]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'Failed to fetch parking lots: {str(e)}'}), 500

# -------------------- Get Parking Spots (Cached) --------------------
@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@cross_origin(origins='http://localhost:5173', supports_credentials=True)
@cache.memoize(timeout=60)  # Cache for 1 minute (spots change frequently)
def get_parking_spots(lot_id):
    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404

        # Get occupied spots
        active_spots = db.session.query(ParkingHistory.spot_id).filter_by(
            lot_id=lot.id,
            status='Parked'
        ).all()
        occupied_ids = {spot.spot_id for spot in active_spots}

        spots = []
        for spot_id in range(1, lot.max_spots + 1):
            status = 'OCCUPIED' if spot_id in occupied_ids else 'AVAILABLE'
            spots.append({
                'spot_id': spot_id,
                'status': status
            })

        result = {
            'lot_id': lot.id,
            'total_spots': lot.max_spots,
            'spots': spots
        }
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# -------------------- Delete Parking Lot --------------------
@admin_bp.route('/delete-parking-lot/<int:lot_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origins='http://localhost:5173')
def delete_parking_lot(lot_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404

        db.session.delete(lot)
        db.session.commit()
        
        # Clear cache after deletion
        clear_parking_cache()
        cache.delete_memoized(get_parking_spots, lot_id)
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete parking lot: {str(e)}'}), 500

# -------------------- Edit Parking Lot --------------------
@admin_bp.route('/edit-parking-lot/<int:lot_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(origins='http://localhost:5173')
def edit_parking_lot(lot_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    try:
        data = request.get_json(force=True)
        lot = ParkingLot.query.get(lot_id)

        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404

        if 'name' in data:
            lot.name = data['name']
        if 'address' in data:
            lot.address = data['address']
        if 'pincode' in data:
            lot.pincode = data['pincode']
        if 'price' in data:
            lot.price_per_hour = float(data['price'])
        if 'maxSpots' in data:
            lot.max_spots = int(data['maxSpots'])

        db.session.commit()
        
        # Clear cache after update
        clear_parking_cache()
        cache.delete_memoized(get_parking_spots, lot_id)
        
        return jsonify({'message': 'Parking lot updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update parking lot: {str(e)}'}), 500

# -------------------- Get Users (Cached) --------------------
@admin_bp.route('/api/users', methods=['GET'])
@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_users():
    try:
        users = User.query.all()
        result = [{
            'id': u.id,
            'email': u.username,
            'fullname': u.fullname,
            'address': u.address,
            'pincode': u.pincode
        } for u in users]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

# -------------------- Search User by ID (Cached) --------------------
@admin_bp.route('/api/search-user', methods=['GET'])
@cross_origin(origins='http://localhost:5173')
@cache.memoize(timeout=300)  
def search_user_by_id():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'user_id is required'}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        result = {
            'id': user.id,
            'email': user.username,
            'fullname': user.fullname,
            'address': user.address,
            'pincode': user.pincode
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@admin_bp.route('/api/search-location', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5176', 'http://127.0.0.1:5176'])

def search_by_location():
    location = request.args.get('location')
    if not location:
        return jsonify({'message': 'Location is required'}), 400

    try:
        print(f"DEBUG: Searching for location: '{location}'")  # Debug print
        lots = ParkingLot.query.filter(ParkingLot.address.ilike(f"%{location}%")).all()
        print(f"DEBUG: Found {len(lots)} lots")  # Debug print
        
        result = []
        for lot in lots:
            # Get latest status for each spot
            occupied_count = 0
            spots = []
            
            for spot_id in range(1, lot.max_spots + 1):
                latest_status = db.session.query(ParkingHistory).filter_by(
                    lot_id=lot.id,
                    spot_id=spot_id
                ).order_by(ParkingHistory.timestamp.desc()).first()
                
                status = 'Available'
                if latest_status and latest_status.status:
                    status_lower = latest_status.status.strip().lower()
                    if status_lower not in ['available', 'free', 'empty']:
                        status = 'Occupied'
                        occupied_count += 1
                
                spots.append({
                    'spot_id': spot_id,
                    'status': status
                })

            result.append({
                'id': lot.id,
                'name': lot.name,
                'address': lot.address,
                'price_per_hour': lot.price_per_hour,
                'max_spots': lot.max_spots,
                'occupied': occupied_count,
                'spots': spots
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@admin_bp.route('/api/summary', methods=['GET'])
@cache.memoize(timeout=120)  # Cache for 2 minutes
def get_parking_summary():
    try:
        lots = ParkingLot.query.all()
        result = []
        
        for lot in lots:
            total_spots = lot.max_spots
            occupied = 0
            
            # Count occupied spots
            for spot_id in range(1, total_spots + 1):
                latest_status = db.session.query(ParkingHistory).filter_by(
                    lot_id=lot.id,
                    spot_id=spot_id
                ).order_by(ParkingHistory.timestamp.desc()).first()
                
                if latest_status and latest_status.status:
                    status_lower = latest_status.status.strip().lower()
                    if status_lower not in ['available', 'free', 'empty', 'vacant']:
                        occupied += 1
            
            available = max(0, total_spots - occupied)
            revenue = occupied * (lot.price_per_hour or 0)
            
            result.append({
                'lot_id': lot.id,
                'lot_name': lot.name,
                'total_spots': total_spots,
                'occupied': occupied,
                'available': available,
                'revenue': revenue
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch parking summary'}), 500

# -------------------- Cache Management --------------------
@admin_bp.route('/api/cache/clear', methods=['POST'])
@cross_origin(origins='http://localhost:5173')
def clear_all_cache():
    """Clear all cache"""
    try:
        cache.clear()
        return jsonify({'message': 'All cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@admin_bp.route('/api/cache/stats', methods=['GET'])
@cross_origin(origins='http://localhost:5173')
def get_cache_stats():
    """Get basic cache info"""
    return jsonify({
        'cache_type': 'Simple in-memory cache',
        'status': 'Active'
    }), 200

# -------------------- Debug Endpoint (No Cache) --------------------
@admin_bp.route('/api/debug-parking-data', methods=['GET'])
def debug_parking_data():
    """Debug endpoint - no caching for real-time data"""
    try:
        lots = ParkingLot.query.all()
        debug_data = []
        
        for lot in lots:
            history = db.session.query(ParkingHistory).filter_by(
                lot_id=lot.id
            ).order_by(ParkingHistory.timestamp.desc()).limit(10).all()
            
            history_data = [{
                'spot_id': h.spot_id,
                'status': h.status,
                'timestamp': h.timestamp.isoformat() if h.timestamp else None
            } for h in history]
            
            debug_data.append({
                'lot_id': lot.id,
                'lot_name': lot.name,
                'max_spots': lot.max_spots,
                'price_per_hour': lot.price_per_hour,
                'recent_history': history_data
            })
        
        return jsonify(debug_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------- Search by Vehicle Number (Cached) --------------------
@admin_bp.route('/api/search-vehicle', methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5176', 'http://127.0.0.1:5176'])
# @cache.memoize(timeout=180)  # Temporarily disabled cache
def search_by_vehicle():
    vehicle_no = request.args.get('vehicle_no')
    if not vehicle_no:
        return jsonify({'message': 'vehicle_no is required'}), 400

    try:
        vehicle_no = vehicle_no.strip().upper()
        print(f"DEBUG: Searching for vehicle: '{vehicle_no}'")  # Debug print
        
        # Search for vehicle in parking history
        vehicle_records = db.session.query(ParkingHistory).filter(
            ParkingHistory.vehicle_no.ilike(f"%{vehicle_no}%")
        ).order_by(ParkingHistory.timestamp.desc()).limit(10).all()
        
        print(f"DEBUG: Found {len(vehicle_records)} vehicle records")  # Debug print
        
        result = []
        for record in vehicle_records:
            result.append({
                'id': record.id,
                'vehicle_no': record.vehicle_no,
                'user_id': record.user_id,
                'lot_id': record.lot_id,
                'spot_id': record.spot_id,
                'status': record.status,
                'timestamp': record.timestamp.isoformat() if record.timestamp else None,
                'lot_name': record.lot.name if record.lot else None
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Vehicle search failed: {str(e)}'}), 500