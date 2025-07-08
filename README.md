# Vehicle Parking App

A full-stack vehicle parking management system built with Flask (backend) and Vue.js (frontend).

## Project Structure

```
├── backend/          # Flask API server
│   ├── app.py       # Main Flask application
│   ├── models.py    # Database models
│   ├── auth_routes.py    # Authentication routes
│   ├── admin_routes.py   # Admin functionality routes
│   ├── user_routes.py    # User functionality routes
│   ├── requirements.txt  # Python dependencies
│   └── templates/   # Flask templates
├── frontend/        # Vue.js client application
│   ├── src/         # Vue.js source code
│   ├── package.json # Node.js dependencies
│   └── vite.config.js    # Vite configuration
```

## Features

- User authentication and authorization
- Admin dashboard for parking lot management
- User dashboard for booking and releasing parking spots
- Real-time parking availability
- Booking history and summaries
- Email notifications and reminders
- Background task processing with Celery

## Prerequisites

Before running this application, make sure you have the following installed:

### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Redis Server** (optional, for Celery background tasks)

### Optional Dependencies
- **Redis** - For background task processing (Celery)
- **Email Server** - For sending notifications (Gmail SMTP or similar)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Vehicle-Parking-App_23f000717-main
```

### 2. Backend Setup (Flask)

#### Navigate to backend directory
```bash
cd backend
```

#### Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Python dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the backend directory (optional, for environment variables):
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///users.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Frontend Setup (Vue.js)

#### Navigate to frontend directory
```bash
cd ../frontend
```

#### Install Node.js dependencies
```bash
npm install
```

## Running the Application

### 1. Start the Backend Server

```bash
cd backend
# Activate virtual environment if not already active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python app.py
```

The Flask backend will start at `http://localhost:5000`

### 2. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The Vue.js frontend will start at `http://localhost:5173` (or another available port)

### 3. Optional: Start Redis and Celery (for background tasks)

If you want to enable background tasks (email reminders, etc.):

#### Start Redis server
```bash
# Windows (if Redis is installed)
redis-server

# macOS (with Homebrew)
brew services start redis

# Linux
sudo systemctl start redis
```

#### Start Celery worker
```bash
cd backend
celery -A celery_tasks.celery_app worker --loglevel=info
```

#### Start Celery Beat (for scheduled tasks)
```bash
cd backend
celery -A celery_tasks.celery_app beat --loglevel=info
```

## Usage

1. **Access the Application**: Open your browser and navigate to `http://localhost:5173`
2. **Register an Account**: Create a new user account or use the admin account
3. **Login**: Use your credentials to access the system
4. **Admin Features**: 
   - Manage parking lots
   - View all bookings
   - User management
   - Generate reports
5. **User Features**:
   - View available parking spots
   - Book parking spaces
   - Release parking spots
   - View booking history

## Default Admin Account

The application creates a default admin account:
- **Username**: `admin`
- **Password**: `admin123`

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard data
- `POST /admin/parking-lots` - Create parking lot
- `GET /admin/users` - Get all users
- `GET /admin/bookings` - Get all bookings

### User Routes
- `GET /user/dashboard` - User dashboard data
- `POST /user/book` - Book a parking spot
- `POST /user/release` - Release a parking spot
- `GET /user/history` - Get booking history

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Backend: Change the port in `app.py`
   - Frontend: Vite will automatically find an available port

2. **Database Issues**
   - Delete `users.db` file and restart the backend to recreate the database

3. **Dependencies Issues**
   - Make sure you're using the correct Python/Node.js versions
   - Try deleting `node_modules` and running `npm install` again
   - For Python, try creating a fresh virtual environment

4. **CORS Errors**
   - Ensure Flask-CORS is properly configured in the backend
   - Check that the frontend is making requests to the correct backend URL

### Environment Variables

The application supports the following environment variables:

- `FLASK_ENV`: Set to `development` or `production`
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `MAIL_*`: Email configuration for notifications
- `REDIS_URL`: Redis connection URL for Celery

## Development

### Backend Development
- The Flask app runs in debug mode by default
- Changes to Python files will automatically restart the server
- Database schema changes require deleting `users.db` and restarting

### Frontend Development
- Vite provides hot module replacement
- Changes to Vue files will automatically update in the browser
- Build for production: `npm run build`

## Production Deployment

For production deployment, consider:

1. **Backend**:
   - Use a production WSGI server like Gunicorn
   - Configure a production database (PostgreSQL, MySQL)
   - Set up proper environment variables
   - Configure Redis for Celery in production

2. **Frontend**:
   - Build the production bundle: `npm run build`
   - Serve with a web server like Nginx
   - Configure proper API base URLs

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please check the troubleshooting section above or create an issue in the repository.
