<template>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" />

  <div v-if="userId" class="dashboard">
    <!-- Header -->
    <nav class="header">
      <div class="header-content">
        <span class="logo">🚗 Welcome {{ username || 'User' }}</span>
        <div class="nav-buttons">
          <router-link to="/" class="nav-btn">Home</router-link>
          <router-link to="/user/summary" class="nav-btn">Summary</router-link>
          <button @click="openProfile" class="nav-btn profile-btn">
            <i class="bi bi-person-circle"></i>
            Profile
          </button>
          <button @click="logout" class="nav-btn logout-btn">Logout</button>
        </div>
      </div>
    </nav>

    <!-- Error Alert -->
    <div v-if="error" class="error-alert">
      <i class="bi bi-exclamation-triangle-fill"></i>
      <div class="error-content">
        <strong>Error:</strong> {{ error }}
        <button @click="clearError" class="error-close">×</button>
      </div>
      <button @click="refreshData" class="retry-btn">Retry</button>
    </div>

    <!-- Success Alert -->
    <div v-if="successMessage" class="success-alert">
      <i class="bi bi-check-circle-fill"></i>
      <div class="success-content">
        {{ successMessage }}
        <button @click="clearSuccess" class="success-close">×</button>
      </div>
    </div>

    <!-- Recent Parking History -->
    <div class="card">
      <div class="card-header">
        <div class="header-left">
          <i class="bi bi-journal-bookmark"></i>
          <strong>Recent Parking History</strong>
        </div>
        <div class="header-right">
          <button @click="fetchParkingHistory" class="refresh-btn" :disabled="historyLoading">
            <i class="bi bi-arrow-clockwise" :class="{ 'spinning': historyLoading }"></i>
          </button>
        </div>
      </div>
      
      <div class="table-container">
        <!-- Loading State for History -->
        <div v-if="historyLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading parking history...</p>
        </div>
        
        <!-- History Table -->
        <table v-else class="simple-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Location</th>
              <th>Vehicle No</th>
              <th>Spot</th>
              <th>Entry Time</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!parkingHistory.length" class="empty-row">
              <td colspan="7" class="no-data">
                <i class="bi bi-info-circle"></i>
                No parking history available.
              </td>
            </tr>
            <tr v-else v-for="parking in parkingHistory" :key="parking.id" class="data-row">
              <td>{{ parking.id }}</td>
              <td>
                <div class="location-cell">
                  <strong>{{ parking.location || 'Unknown' }}</strong>
                  <small>{{ parking.address || 'No address' }}</small>
                </div>
              </td>
              <td>
                <span class="vehicle-badge">{{ parking.vehicle_no }}</span>
              </td>
              <td>
                <span class="spot-badge">{{ parking.spot_id }}</span>
              </td>
              <td>{{ formatDateTime(parking.entry_time || parking.timestamp) }}</td>
              <td>
                <span :class="getStatusClass(parking.status)">
                  {{ parking.status }}
                </span>
              </td>
              <td>
                <button 
                  v-if="parking.status === 'Parked'" 
                  class="btn release-btn" 
                  @click="openReleaseModal(parking)"
                  title="Release parking spot"
                >
                  <i class="bi bi-box-arrow-right"></i>
                  Release
                </button>
                <span v-else class="action-disabled">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Search -->
    <div class="search-section">
      <div class="search-box">
        <span class="search-label">
          <i class="bi bi-search"></i>
          Search Location
        </span>
        <input
          type="text"
          class="search-input"
          v-model="searchQuery"
          placeholder="Enter location name, address, or pin code..."
          @input="debouncedSearch"
        />
        <button v-if="searchQuery" @click="clearSearch" class="clear-search-btn">
          <i class="bi bi-x-circle-fill"></i>
        </button>
      </div>
    </div>

    <!-- Parking Lots -->
    <div class="card">
      <div class="card-header">
        <div class="header-left">
          <i class="bi bi-p-square"></i>
          <strong>
            Parking Lots 
            <span class="location-indicator">
              {{ searchQuery ? `@ ${searchQuery}` : '@ All Locations' }}
            </span>
          </strong>
          <span v-if="parkingLots.length" class="results-count">
            ({{ parkingLots.length }} {{ parkingLots.length === 1 ? 'result' : 'results' }})
          </span>
        </div>
        <div class="header-right">
          <button @click="fetchParkingLots" class="refresh-btn" :disabled="lotsLoading">
            <i class="bi bi-arrow-clockwise" :class="{ 'spinning': lotsLoading }"></i>
          </button>
        </div>
      </div>
      
      <div class="table-container">
        <!-- Loading State for Lots -->
        <div v-if="lotsLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Searching parking lots...</p>
        </div>
        
        <!-- Lots Table -->
        <table v-else class="simple-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Address</th>
              <th>Price/Hr</th>
              <th>Availability</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!parkingLots.length" class="empty-row">
              <td colspan="6" class="no-data">
                <i class="bi bi-info-circle"></i>
                {{ searchQuery ? 'No parking lots found for your search.' : 'No parking lots available.' }}
              </td>
            </tr>
            <tr v-else v-for="lot in parkingLots" :key="lot.id" class="data-row">
              <td>{{ lot.id }}</td>
              <td>
                <div class="name-cell">
                  <strong>{{ lot.name || 'Unnamed Lot' }}</strong>
                </div>
              </td>
              <td>
                <div class="address-cell">
                  {{ lot.address }}
                  <small v-if="lot.pincode">{{ lot.pincode }}</small>
                </div>
              </td>
              <td>
                <span class="price-badge">₹{{ lot.price_per_hour || 0 }}</span>
              </td>
              <td>
                <div class="availability-cell">
                  <span :class="getAvailabilityClass(lot.availability)">
                    <i :class="getAvailabilityIcon(lot.availability)"></i>
                    {{ lot.availability || 0 }} spots
                  </span>
                  <small>of {{ lot.max_spots || 0 }} total</small>
                </div>
              </td>
              <td>
                <button
                  class="btn book-btn"
                  :disabled="!lot.availability || lot.availability === 0"
                  @click="openBookingModal(lot)"
                  :title="lot.availability ? 'Book parking spot' : 'No spots available'"
                >
                  <i class="bi bi-plus-circle"></i>
                  {{ lot.availability === 0 ? 'Full' : 'Book' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="stats-section">
      <div class="stat-card">
        <i class="bi bi-car-front"></i>
        <div class="stat-info">
          <span class="stat-number">{{ activeBookings }}</span>
          <span class="stat-label">Active Bookings</span>
        </div>
      </div>
      <div class="stat-card">
        <i class="bi bi-clock-history"></i>
        <div class="stat-info">
          <span class="stat-number">{{ totalBookings }}</span>
          <span class="stat-label">Total Bookings</span>
        </div>
      </div>
      <div class="stat-card">
        <i class="bi bi-p-square-fill"></i>
        <div class="stat-info">
          <span class="stat-number">{{ parkingLots.length }}</span>
          <span class="stat-label">Available Lots</span>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <Booking
      v-if="showBooking"
      :lot="selectedLot"
      :userId="userId"
      @close="closeBookingModal"
      @success="handleBookingSuccess"
    />

    <Release
      v-if="showRelease"
      :history="selectedHistory"
      :userId="userId"
      @close="closeReleaseModal"
      @success="handleReleaseSuccess"
    />
  </div>

  <!-- Not Logged In State -->
  <div v-else class="not-logged-in">
    <div class="login-prompt">
      <i class="bi bi-shield-lock"></i>
      <h2>Access Denied</h2>
      <p>Please log in to access your dashboard.</p>
      <button @click="$router.push('/login')" class="login-btn">
        <i class="bi bi-box-arrow-in-right"></i>
        Go to Login
      </button>
    </div>
  </div>

  <!-- Profile Modal -->
  <div v-if="showProfile" class="profile-modal-overlay" @click="closeProfile">
    <div class="profile-modal" @click.stop>
      <UserProfile 
        @close="closeProfile" 
        @profile-updated="handleProfileUpdated"
      />
    </div>
  </div>
</template>

<script>
// filepath: c:\Users\rajve\Downloads\vehical_parking_system-main\vehical_parking_system-main\frontend\src\components\UserDashboard.vue
import axios from 'axios'
import authService from '../services/auth.js'
import Booking from './Booking.vue'
import Release from './Release.vue'
import UserProfile from './UserProfile.vue'

export default {
  name: 'UserDashboard',
  components: { Booking, Release, UserProfile },
  data() {
    return {
      parkingHistory: [],
      parkingLots: [],
      searchQuery: '',
      userId: localStorage.getItem('userId') || null,
      username: localStorage.getItem('username') || localStorage.getItem('fullname') || 'User',
      showBooking: false,
      showRelease: false,
      selectedLot: null,
      selectedHistory: null,
      historyLoading: false,
      lotsLoading: false,
      error: '',
      successMessage: '',
      searchTimeout: null,
      refreshInterval: null,
      showProfile: false
    }
  },

  computed: {
    activeBookings() {
      return this.parkingHistory.filter(h => h.status === 'Parked').length
    },
    totalBookings() {
      return this.parkingHistory.length
    }
  },

  methods: {
    async fetchParkingHistory() {
      this.historyLoading = true;
      this.error = '';
      
      try {
        const userId = localStorage.getItem('userId');
        if (!userId) {
          throw new Error('User not logged in');
        }

        console.log('Fetching parking history for user:', userId);

        const response = await axios.get('http://localhost:5000/user/parking-history', {
          headers: {
            'X-User-ID': userId,
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          },
          timeout: 10000
        });
        
        console.log('Parking history response:', response.data);
        
        // Ensure we have proper data structure with lot_id
        this.parkingHistory = Array.isArray(response.data) ? response.data.map(item => ({
          id: item.id,
          location: item.location || item.parking_lot_name || 'Unknown Location',
          address: item.address || item.parking_lot_address || '',
          vehicle_no: item.vehicle_no || item.vehicle_number || '',
          spot_id: item.spot_id || item.parking_spot_id || '',
          entry_time: item.entry_time || item.start_time || item.timestamp,
          exit_time: item.exit_time || item.end_time,
          status: item.status || 'Unknown',
          amount: item.amount || item.total_amount || 0,
          lot_id: item.lot_id || item.parking_lot_id || null, // Ensure lot_id is available
          duration: item.duration || null,
          booking_id: item.booking_id || item.id
        })) : [];
        
      } catch (error) {
        console.error('Error fetching parking history:', error);
        this.handleApiError(error, 'Failed to load parking history');
      } finally {
        this.historyLoading = false;
      }
    },

    async fetchParkingLots() {
      this.lotsLoading = true;
      
      try {
        const userId = localStorage.getItem('userId');
        
        const url = this.searchQuery.trim()
          ? `http://localhost:5000/user/search-parking?q=${encodeURIComponent(this.searchQuery.trim())}`
          : `http://localhost:5000/user/parking-lots`;
        
        console.log('Fetching from URL:', url);
        
        const response = await axios.get(url, {
          headers: {
            'X-User-ID': userId,
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          },
          timeout: 10000
        });
        
        console.log('Parking lots response:', response.data);
        
        const lots = Array.isArray(response.data) ? response.data : [];
        this.parkingLots = lots.map(lot => ({
          id: lot.id,
          address: lot.address,
          availability: lot.available_spots || lot.availability || 0,
          name: lot.name,
          price_per_hour: lot.price_per_hour || lot.hourly_rate || 0,
          max_spots: lot.max_spots || lot.total_spots || 0,
          pincode: lot.pincode || lot.pin_code
        }));
        
      } catch (error) {
        console.error('Error fetching parking lots:', error);
        this.handleApiError(error, 'Failed to load parking lots');
      } finally {
        this.lotsLoading = false;
      }
    },

    handleApiError(error, defaultMessage) {
      if (error.response?.status === 401) {
        this.logout();
        return;
      }
      
      let errorMessage = defaultMessage;
      
      if (error.code === 'ERR_NETWORK') {
        errorMessage = 'Cannot connect to server. Please check if the backend is running.';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      this.error = errorMessage;
      
      // Auto-clear error after 10 seconds
      setTimeout(() => {
        this.error = '';
      }, 10000);
    },

    debouncedSearch() {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.fetchParkingLots();
      }, 500);
    },

    clearSearch() {
      this.searchQuery = '';
      this.fetchParkingLots();
    },

    openBookingModal(lot) {
      this.selectedLot = lot;
      this.showBooking = true;
    },

    closeBookingModal() {
      this.showBooking = false;
      this.selectedLot = null;
    },

    openReleaseModal(history) {
      console.log('Opening release modal for history:', history);
      
      // Ensure we have the required data for release
      const enhancedHistory = {
        ...history,
        // Provide fallback values to prevent undefined issues
        lot_id: history.lot_id || history.parking_lot_id || null,
        booking_id: history.booking_id || history.id,
        parking_lot_name: history.location || history.parking_lot_name || 'Unknown Location',
        parking_spot_id: history.spot_id || history.parking_spot_id || '',
        start_time: history.entry_time || history.start_time,
        vehicle_number: history.vehicle_no || history.vehicle_number || ''
      };
      
      console.log('Enhanced history data:', enhancedHistory);
      
      this.selectedHistory = enhancedHistory;
      this.showRelease = true;
    },

    closeReleaseModal() {
      this.showRelease = false;
      this.selectedHistory = null;
    },

    handleBookingSuccess(message) {
      this.successMessage = message || 'Parking spot booked successfully!';
      this.closeBookingModal();
      this.refreshData();
      this.clearSuccessAfterDelay();
    },

    handleReleaseSuccess(message) {
      this.successMessage = message || 'Parking spot released successfully!';
      this.closeReleaseModal();
      this.refreshData();
      this.clearSuccessAfterDelay();
    },

    clearSuccessAfterDelay() {
      setTimeout(() => {
        this.successMessage = '';
      }, 5000);
    },

    refreshData() {
      this.fetchParkingLots();
      this.fetchParkingHistory();
    },

    clearError() {
      this.error = '';
    },

    clearSuccess() {
      this.successMessage = '';
    },

    async logout() {
      // Clear intervals
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      
      // Use auth service for proper logout
      await authService.logout();
      
      // Redirect to login
      this.$router.push('/login');
    },

    // Profile modal methods
    openProfile() {
      this.showProfile = true;
    },

    closeProfile() {
      this.showProfile = false;
    },

    handleProfileUpdated(updatedUser) {
      // Update local user data if needed
      if (updatedUser.fullname) {
        this.username = updatedUser.fullname;
        localStorage.setItem('fullname', updatedUser.fullname);
      }
      // Optionally refresh other data if profile updates affect dashboard
      this.successMessage = 'Profile updated successfully!';
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (error) {
        return 'Invalid date';
      }
    },

    getStatusClass(status) {
      return {
        'status-badge': true,
        'status-parked': status === 'Parked',
        'status-completed': status === 'Completed',
        'status-reserved': status === 'Reserved'
      };
    },

    getAvailabilityClass(availability) {
      return {
        'availability-indicator': true,
        'availability-high': availability > 5,
        'availability-medium': availability > 0 && availability <= 5,
        'availability-none': availability === 0
      };
    },

    getAvailabilityIcon(availability) {
      if (availability > 5) return 'bi-check-circle-fill';
      if (availability > 0) return 'bi-exclamation-circle-fill';
      return 'bi-x-circle-fill';
    },

    setupAutoRefresh() {
      // Auto-refresh every 2 minutes
      this.refreshInterval = setInterval(() => {
        if (!this.historyLoading && !this.lotsLoading) {
          this.refreshData();
        }
      }, 120000);
    }
  },

  async mounted() {
    if (!this.userId) {
      this.$router.push('/login');
      return;
    }
    
    console.log('UserDashboard mounted, userId:', this.userId);
    
    // Initial data fetch
    await this.$nextTick();
    this.refreshData();
    
    // Setup auto-refresh
    this.setupAutoRefresh();
  },

  beforeUnmount() {
    // Clear timeouts and intervals
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
}
</script>

<style scoped>
/* Main Dashboard */
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* Header */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 28px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.nav-buttons {
  display: flex;
  gap: 15px;
  align-items: center;
}

.nav-btn {
  padding: 12px 24px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 25px;
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
}

.nav-btn:hover {
  background: white;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.profile-btn {
  border-color: #17a2b8;
  background: rgba(23,162,184,0.2);
}

.logout-btn {
  border-color: #dc3545;
  background: rgba(220,53,69,0.2);
}

/* Alert Messages */
.error-alert {
  background: linear-gradient(45deg, #dc3545, #c82333);
  color: white;
  padding: 15px 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(220,53,69,0.3);
}

.success-alert {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
  padding: 15px 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(40,167,69,0.3);
}

.error-content, .success-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-close, .success-close {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.retry-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: rgba(255,255,255,0.3);
}

/* Cards */
.card {
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  margin-bottom: 30px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.05);
}

.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 20px 25px;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left i {
  font-size: 22px;
  color: #007bff;
}

.header-left strong {
  color: #495057;
  font-size: 18px;
}

.location-indicator {
  color: #6c757d;
  font-weight: 400;
  font-size: 16px;
}

.results-count {
  color: #6c757d;
  font-weight: 400;
  font-size: 14px;
  margin-left: 8px;
}

.refresh-btn {
  background: #007bff;
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: scale(1.05);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Search Section */
.search-section {
  margin-bottom: 30px;
}

.search-box {
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  display: flex;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.search-box:focus-within {
  border-color: #007bff;
  box-shadow: 0 4px 25px rgba(0,123,255,0.15);
}

.search-label {
  background: linear-gradient(135deg, #e9ecef 0%, #f8f9fa 100%);
  padding: 18px 24px;
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  flex: 1;
  padding: 18px 24px;
  border: none;
  outline: none;
  font-size: 16px;
  background: transparent;
}

.search-input::placeholder {
  color: #6c757d;
}

.clear-search-btn {
  background: none;
  border: none;
  color: #6c757d;
  padding: 18px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.clear-search-btn:hover {
  color: #dc3545;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

/* Tables */
.table-container {
  overflow-x: auto;
}

.simple-table {
  width: 100%;
  border-collapse: collapse;
}

.simple-table th {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 18px 20px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.simple-table td {
  padding: 18px 20px;
  border-bottom: 1px solid #f1f3f4;
  vertical-align: middle;
}

.data-row:hover {
  background: #f8f9fa;
}

.empty-row {
  background: #fafbfc;
}

.no-data {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Table Cell Styles */
.location-cell, .name-cell, .address-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.location-cell strong, .name-cell strong {
  color: #495057;
  font-weight: 600;
}

.location-cell small, .address-cell small {
  color: #6c757d;
  font-size: 12px;
}

.vehicle-badge, .spot-badge {
  background: #007bff;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.spot-badge {
  background: #17a2b8;
}

.price-badge {
  background: #28a745;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.availability-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.availability-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.availability-high {
  color: #28a745;
}

.availability-medium {
  color: #ffc107;
}

.availability-none {
  color: #dc3545;
}

/* Status Badges */
.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-parked {
  background: #dc3545;
  color: white;
}

.status-completed {
  background: #28a745;
  color: white;
}

.status-reserved {
  background: #ffc107;
  color: #212529;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.book-btn {
  background: linear-gradient(45deg, #007bff, #0056b3);
  color: white;
}

.book-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,123,255,0.3);
}

.book-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.release-btn {
  background: linear-gradient(45deg, #dc3545, #c82333);
  color: white;
}

.release-btn:hover {
  background: linear-gradient(45deg, #c82333, #a71e2a);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(220,53,69,0.3);
}

.action-disabled {
  color: #6c757d;
  font-style: italic;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, white 0%, #f8f9fa 100%);
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(0,0,0,0.05);
}

.stat-card i {
  font-size: 32px;
  color: #007bff;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #495057;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Not Logged In State */
.not-logged-in {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-prompt {
  background: white;
  padding: 60px 40px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  max-width: 400px;
}

.login-prompt i {
  font-size: 64px;
  color: #dc3545;
  margin-bottom: 20px;
}

.login-prompt h2 {
  color: #495057;
  margin-bottom: 15px;
}

.login-prompt p {
  color: #6c757d;
  margin-bottom: 30px;
}

.login-btn {
  background: linear-gradient(45deg, #007bff, #0056b3);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.login-btn:hover {
  background: linear-gradient(45deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,123,255,0.3);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .dashboard {
    max-width: 100%;
    padding: 15px;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .nav-buttons {
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
  
  .nav-btn {
    padding: 10px 16px;
    font-size: 14px;
  }
  
  .search-box {
    flex-direction: column;
  }
  
  .search-label {
    text-align: center;
    border-bottom: 1px solid #dee2e6;
  }
  
  .card-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .simple-table {
    font-size: 14px;
  }
  
  .simple-table th,
  .simple-table td {
    padding: 12px 8px;
  }
}

@media (max-width: 480px) {
  .dashboard {
    padding: 10px;
  }
  
  .logo {
    font-size: 22px;
  }
  
  .nav-btn {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .card {
    margin-bottom: 20px;
  }
  
  .table-container {
    overflow-x: scroll;
  }
  
  .simple-table {
    min-width: 600px;
  }
}

/* Profile button and modal styles */
.profile-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.profile-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.profile-btn i {
  font-size: 16px;
}

.profile-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.profile-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .profile-modal {
    width: 95%;
    margin: 20px;
  }
}
</style>