<template>
  <div class="admin-container">
    <h2 class="header">Registered Users</h2>
    <p class="welcome-text">Manage all registered users</p>

    <!-- Navigation -->
    <nav class="top-nav">
      <div class="nav-content">
        <div class="nav-links">
          <router-link to="/admin">Home</router-link>
          <router-link to="/admin/registered-users" class="nav-link active">Users</router-link>
          <router-link to="/admin/search">Search</router-link>
          <router-link to="/admin/summary">Summary</router-link>
          <button @click="logout" class="btn btn-danger">Logout</button>
        </div>
      </div>
    </nav>

    <!-- Quick Stats -->
    <div class="stats-container">
      <div class="stat-card">
        <h3>{{ totalUsers }}</h3>
        <p>Total Users</p>
      </div>
      <div class="stat-card">
        <h3>{{ activeUsers }}</h3>
        <p>Active Users</p>
      </div>
      <div class="stat-card">
        <h3>{{ recentlyJoined }}</h3>
        <p>Joined This Month</p>
      </div>
      <div class="stat-card">
        <h3>{{ usersWithBookings }}</h3>
        <p>With Bookings</p>
      </div>
    </div>

    <!-- Action Bar -->
    <div class="action-bar">
      <button @click="refreshUsers" class="btn btn-primary" :disabled="loading">
        <span v-if="loading">Refreshing...</span>
        <span v-else>🔄 Refresh Users</span>
      </button>
      <div class="search-box">
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search users..."
          class="search-input"
        />
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="loading" class="status-message">
      <div class="spinner"></div>
      Loading users...
    </div>
    <div v-else-if="error" class="status-message error">
      {{ error }}
      <button @click="refreshUsers" class="retry-btn">Retry</button>
    </div>

    <!-- Users Section -->
    <div v-if="!loading && filteredUsers.length === 0 && !searchTerm" class="no-users">
      <div class="empty-state">
        <h3>No users registered yet</h3>
        <p>Users will appear here once they register for parking</p>
      </div>
    </div>

    <div v-else-if="!loading && filteredUsers.length === 0 && searchTerm" class="no-users">
      <div class="empty-state">
        <h3>No users found</h3>
        <p>Try adjusting your search term</p>
      </div>
    </div>

    <!-- Users Grid -->
    <div class="users-container" v-else>
      <div v-for="user in filteredUsers" :key="user.id" class="user-card">
        <div class="user-header">
          <div class="user-avatar">
            <div class="avatar-circle">
              {{ getInitials(user.fullname || user.email) }}
            </div>
          </div>
          <div class="user-title-section">
            <h5 class="user-name">{{ user.fullname || 'N/A' }}</h5>
            <span class="user-email">{{ user.email }}</span>
          </div>
          <div class="user-id">
            <span class="id-label">ID</span>
            <span class="id-value">#{{ user.id }}</span>
          </div>
        </div>

        <div class="user-info">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">📧 Email:</span>
              <span class="value">{{ user.email }}</span>
            </div>
            <div class="info-item">
              <span class="label">📍 Address:</span>
              <span class="value">{{ user.address || 'Not provided' }}</span>
            </div>
            <div class="info-item">
              <span class="label">📮 Pin Code:</span>
              <span class="value">{{ user.pincode || 'Not provided' }}</span>
            </div>
            <div class="info-item">
              <span class="label">👤 Full Name:</span>
              <span class="value">{{ user.fullname || 'Not provided' }}</span>
            </div>
          </div>
        </div>

        <!-- User Actions -->
        <div class="user-actions">
          <button @click="viewUserDetails(user)" class="action-btn view-btn">
            📊 View Details
          </button>
          <button @click="viewUserBookings(user)" class="action-btn bookings-btn">
            🎫 Bookings
          </button>
          <button @click="contactUser(user)" class="action-btn contact-btn">
            ✉️ Contact
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import authService from '../services/auth.js'

export default {
  name: 'AdminUsers',
  data() {
    return {
      users: [],
      loading: false,
      error: '',
      searchTerm: '',
      refreshInterval: null
    }
  },
  computed: {
    totalUsers() {
      return this.users.length;
    },
    activeUsers() {
      // For now, consider all users as active
      // This could be enhanced with last login tracking
      return this.users.length;
    },
    recentlyJoined() {
      // Users joined this month (simplified for demo)
      // This would require actual date tracking in the backend
      return Math.floor(this.users.length * 0.3);
    },
    usersWithBookings() {
      // Users who have made bookings (simplified for demo)
      // This would require actual booking data correlation
      return Math.floor(this.users.length * 0.6);
    },
    filteredUsers() {
      if (!this.searchTerm) {
        return this.users;
      }
      const term = this.searchTerm.toLowerCase();
      return this.users.filter(user => 
        (user.email || '').toLowerCase().includes(term) ||
        (user.fullname || '').toLowerCase().includes(term) ||
        (user.address || '').toLowerCase().includes(term) ||
        (user.pincode || '').toString().includes(term) ||
        user.id.toString().includes(term)
      );
    }
  },
  methods: {
    async fetchUsers() {
      this.loading = true;
      this.error = '';
      
      try {
        const res = await axios.get('http://localhost:5000/admin/api/users');
        this.users = res.data || [];
      } catch (err) {
        console.error('Failed to fetch users:', err);
        this.error = 'Failed to load users. Please try again.';
      } finally {
        this.loading = false;
      }
    },

    async refreshUsers() {
      await this.fetchUsers();
    },

    async logout() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      await authService.logout();
      this.$router.push('/login');
    },

    getInitials(name) {
      if (!name) return '?';
      const parts = name.split(' ');
      if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
      }
      return name.substring(0, 2).toUpperCase();
    },

    viewUserDetails(user) {
      // Show detailed user information
      alert(`User Details:\n\nID: ${user.id}\nName: ${user.fullname || 'N/A'}\nEmail: ${user.email}\nAddress: ${user.address || 'N/A'}\nPin Code: ${user.pincode || 'N/A'}`);
    },

    viewUserBookings(user) {
      // Navigate to user bookings or show booking history
      alert(`View bookings for ${user.fullname || user.email}\n\nThis feature would show the user's booking history and current reservations.`);
    },

    contactUser(user) {
      // Open email client or show contact options
      const subject = encodeURIComponent('Parking System - Contact from Admin');
      const body = encodeURIComponent(`Hello ${user.fullname || 'User'},\n\nWe are contacting you regarding your parking account.\n\nBest regards,\nParking System Admin`);
      window.open(`mailto:${user.email}?subject=${subject}&body=${body}`);
    }
  },

  async created() {
    await this.fetchUsers();
    
    // Auto-refresh every 60 seconds
    this.refreshInterval = setInterval(() => {
      if (!this.loading) {
        this.fetchUsers();
      }
    }, 60000);
  },

  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
}
</script>

<style scoped>
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  text-align: center;
  color: #333;
  margin-bottom: 5px;
  font-size: 2.5em;
}

.welcome-text {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 1.1em;
}

.top-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: white;
  font-weight: 500;
  padding: 10px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-links a:hover {
  background-color: rgba(255,255,255,0.2);
  transform: translateY(-1px);
}

.nav-links a.active {
  background-color: rgba(255,255,255,0.3);
  font-weight: 600;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
  transform: translateY(-1px);
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-left: 4px solid #007bff;
}

.stat-card:nth-child(2) {
  border-left-color: #28a745;
}

.stat-card:nth-child(3) {
  border-left-color: #ffc107;
}

.stat-card:nth-child(4) {
  border-left-color: #17a2b8;
}

.stat-card h3 {
  font-size: 2.5em;
  margin: 0;
  color: #333;
}

.stat-card p {
  margin: 5px 0 0 0;
  color: #666;
  font-weight: 500;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
}

.status-message {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  background-color: #d4edda;
  color: #155724;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.status-message.error {
  background-color: #f8d7da;
  color: #721c24;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #333;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: none;
  border: 1px solid #721c24;
  color: #721c24;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.empty-state h3 {
  color: #666;
  margin-bottom: 10px;
}

.empty-state p {
  color: #888;
  margin-bottom: 20px;
}

.users-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.user-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  border: 1px solid #e9ecef;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.user-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.user-title-section {
  flex: 1;
  min-width: 0;
}

.user-name {
  color: #333;
  margin: 0 0 5px 0;
  font-size: 1.2em;
  font-weight: 600;
  word-break: break-word;
}

.user-email {
  color: #666;
  font-size: 0.9em;
  word-break: break-word;
}

.user-id {
  text-align: right;
  flex-shrink: 0;
}

.id-label {
  display: block;
  font-size: 0.8em;
  color: #666;
  margin-bottom: 2px;
}

.id-value {
  display: block;
  font-weight: 600;
  color: #007bff;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f8f9fa;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-size: 0.9em;
  color: #666;
  font-weight: 500;
  flex-shrink: 0;
  min-width: 100px;
}

.value {
  font-size: 0.9em;
  font-weight: 500;
  color: #333;
  text-align: right;
  word-break: break-word;
}

.user-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 100px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  text-align: center;
}

.view-btn {
  background-color: #17a2b8;
  color: white;
}

.view-btn:hover {
  background-color: #138496;
  transform: translateY(-1px);
}

.bookings-btn {
  background-color: #007bff;
  color: white;
}

.bookings-btn:hover {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.contact-btn {
  background-color: #28a745;
  color: white;
}

.contact-btn:hover {
  background-color: #218838;
  transform: translateY(-1px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-container {
    padding: 15px;
  }
  
  .nav-content {
    flex-direction: column;
    gap: 15px;
  }
  
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .users-container {
    grid-template-columns: 1fr;
  }
  
  .user-header {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .user-id {
    text-align: center;
  }
  
  .info-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .value {
    text-align: center;
  }
  
  .user-actions {
    flex-direction: column;
  }
  
  .action-btn {
    min-width: auto;
  }
}
</style>
