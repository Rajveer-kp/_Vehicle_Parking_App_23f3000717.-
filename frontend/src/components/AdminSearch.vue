<template>
  <div class="admin-container">
    <h2 class="header">Advanced Search System</h2>
    <p class="welcome-text">Search and analyze parking data across the system</p>

    <!-- Navigation -->
    <nav class="top-nav">
      <div class="nav-content">
        <div class="nav-links">
          <router-link to="/admin">Home</router-link>
          <router-link to="/admin/registered-users" class="nav-link">Users</router-link>
          <router-link to="/admin/search" class="nav-link active">Search</router-link>
          <router-link to="/admin/summary">Summary</router-link>
          <button @click="logout" class="btn btn-danger">Logout</button>
        </div>
      </div>
    </nav>



    <!-- Search Interface Card -->
    <div class="search-card">
      <div class="search-header">
        <div class="search-title">
          <i class="bi bi-search"></i>
          <h4>Smart Search</h4>
        </div>
        <div class="search-actions">
          <button @click="clearAllResults" class="btn btn-outline-secondary btn-sm" v-if="hasResults">
            <i class="bi bi-arrow-clockwise"></i> Clear All
          </button>
          <button @click="toggleAdvanced" class="btn btn-outline-primary btn-sm">
            <i class="bi bi-gear"></i> {{ showAdvanced ? 'Simple' : 'Advanced' }}
          </button>
        </div>
      </div>

      <!-- Search Type Selector -->
      <div class="search-type-selector">
        <div class="type-tabs">
          <button 
            v-for="type in searchTypes" 
            :key="type.value"
            @click="searchBy = type.value"
            :class="['type-tab', { active: searchBy === type.value }]"
          >
            <i :class="type.icon"></i>
            {{ type.label }}
          </button>
        </div>
      </div>

      <!-- Search Input -->
      <div class="search-input-section">
        <div class="input-group">
          <div class="input-icon">
            <i :class="getCurrentSearchIcon()"></i>
          </div>
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="getPlaceholder()"
            @keyup.enter="handleSearch"
            :disabled="loading"
            class="search-input"
          />
          <button 
            @click="handleSearch" 
            :disabled="!searchQuery.trim() || loading"
            class="search-btn"
          >
            <span v-if="loading">
              <div class="spinner-sm"></div>
              Searching...
            </span>
            <span v-else>
              <i class="bi bi-search"></i>
              Search
            </span>
          </button>
        </div>
      </div>

      <!-- Advanced Options -->
      <div v-if="showAdvanced" class="advanced-options">
        <div class="advanced-grid">
          <div class="option-group">
            <label>Date Range</label>
            <div class="date-inputs">
              <input type="date" v-model="filters.startDate" class="form-control">
              <span>to</span>
              <input type="date" v-model="filters.endDate" class="form-control">
            </div>
          </div>
          <div class="option-group" v-if="searchBy === 'vehicle'">
            <label>Status Filter</label>
            <select v-model="filters.status" class="form-control">
              <option value="">All Status</option>
              <option value="OCCUPIED">Occupied</option>
              <option value="AVAILABLE">Available</option>
              <option value="RESERVED">Reserved</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="loading" class="status-message">
      <div class="spinner"></div>
      Searching {{ searchTypes.find(t => t.value === searchBy)?.label.toLowerCase() }}...
    </div>
    
    <div v-else-if="error" class="status-message error">
      <i class="bi bi-exclamation-triangle"></i>
      {{ error }}
      <button @click="error = ''" class="retry-btn">
        <i class="bi bi-x"></i>
      </button>
    </div>

    <!-- Search Results -->
    <div class="results-section">
      <!-- User Results -->
      <div v-if="searchBy === 'user_id' && userResult" class="results-container">
        <div class="results-header">
          <h4><i class="bi bi-person-check"></i> User Profile</h4>
          <span class="result-count">1 user found</span>
        </div>
        <div class="user-result-card">
          <div class="user-avatar">
            <div class="avatar-circle">
              {{ getInitials(userResult.fullname || userResult.email) }}
            </div>
          </div>
          <div class="user-details">
            <div class="user-name">{{ userResult.fullname || 'Unknown User' }}</div>
            <div class="user-email">{{ userResult.email || 'No email provided' }}</div>
            <div class="user-meta">
              <div class="meta-item">
                <i class="bi bi-hash"></i>
                <span>ID: {{ userResult.id }}</span>
              </div>
              <div class="meta-item" v-if="userResult.address">
                <i class="bi bi-geo-alt"></i>
                <span>{{ userResult.address }}</span>
              </div>
              <div class="meta-item" v-if="userResult.pincode">
                <i class="bi bi-mailbox"></i>
                <span>PIN: {{ userResult.pincode }}</span>
              </div>
            </div>
          </div>
          <div class="user-status">
            <span class="status-badge active">
              <i class="bi bi-check-circle"></i>
              Active User
            </span>
          </div>
        </div>
      </div>

      <!-- Location Results -->
      <div v-if="searchBy === 'location' && parkingLots.length > 0" class="results-container">
        <div class="results-header">
          <h4><i class="bi bi-geo-alt"></i> Parking Locations</h4>
          <span class="result-count">{{ parkingLots.length }} location{{ parkingLots.length !== 1 ? 's' : '' }} found</span>
        </div>
        <div class="locations-grid">
          <div v-for="lot in parkingLots" :key="lot.id" class="location-card">
            <div class="location-header">
              <h5>{{ lot.name }}</h5>
              <div class="location-status">
                <span class="occupancy-badge" :class="getOccupancyClass(lot)">
                  {{ getOccupancyPercentage(lot) }}% Full
                </span>
              </div>
            </div>
            <div class="location-address">
              <i class="bi bi-geo-alt"></i>
              {{ lot.address }}
            </div>
            <div class="location-stats">
              <div class="stat-item">
                <i class="bi bi-currency-rupee"></i>
                <span>₹{{ lot.price_per_hour || 'N/A' }}/hr</span>
              </div>
              <div class="stat-item">
                <i class="bi bi-car-front"></i>
                <span>{{ lot.occupied || 0 }}/{{ lot.max_spots || 0 }} spots</span>
              </div>
            </div>
            
            <!-- Spot Visualization -->
            <div v-if="lot.spots && lot.spots.length > 0" class="spot-visualization">
              <div class="spot-legend">
                <span class="legend-item available">
                  <div class="legend-color"></div>
                  Available
                </span>
                <span class="legend-item occupied">
                  <div class="legend-color"></div>
                  Occupied
                </span>
              </div>
              <div class="spots-grid">
                <div 
                  v-for="spot in lot.spots" 
                  :key="spot.spot_id"
                  :class="['spot-visual', getSpotStatusClass(spot.status)]"
                  :title="`Spot ${spot.spot_id}: ${getSpotStatusLabel(spot.status)}`"
                >
                  {{ spot.spot_id }}
                </div>
              </div>
            </div>
            
            <div class="location-actions">
              <button class="btn btn-primary btn-sm">
                <i class="bi bi-eye"></i> View Details
              </button>
              <button class="btn btn-outline-primary btn-sm">
                <i class="bi bi-pencil"></i> Edit
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Vehicle Results -->
      <div v-if="searchBy === 'vehicle' && vehicleResults.length > 0" class="results-container">
        <div class="results-header">
          <h4><i class="bi bi-car-front"></i> Vehicle Records</h4>
          <span class="result-count">{{ vehicleResults.length }} record{{ vehicleResults.length !== 1 ? 's' : '' }} found</span>
        </div>
        <div class="vehicles-list">
          <div v-for="record in vehicleResults" :key="record.id" class="vehicle-card">
            <div class="vehicle-icon">
              <i class="bi bi-car-front-fill"></i>
            </div>
            <div class="vehicle-info">
              <div class="vehicle-number">{{ record.vehicle_no }}</div>
              <div class="vehicle-details">
                <div class="detail-item">
                  <i class="bi bi-person"></i>
                  <span>User ID: {{ record.user_id }}</span>
                </div>
                <div class="detail-item">
                  <i class="bi bi-clock"></i>
                  <span>{{ formatDate(record.entry_time || record.timestamp) }}</span>
                </div>
              </div>
            </div>
            <div class="vehicle-status">
              <span :class="['status-badge', record.status?.toLowerCase()]">
                {{ record.status || 'Unknown' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-if="showNoResults" class="no-results">
        <div class="no-results-icon">
          <i class="bi bi-search"></i>
        </div>
        <h4>No results found</h4>
        <p>We couldn't find any {{ searchTypes.find(t => t.value === searchBy)?.label.toLowerCase() }} matching <strong>"{{ searchQuery }}"</strong></p>
        <div class="no-results-actions">
          <button @click="clearSearch" class="btn btn-primary">
            <i class="bi bi-arrow-left"></i> Try Different Search
          </button>
          <button @click="toggleAdvanced" class="btn btn-outline-primary">
            <i class="bi bi-gear"></i> Advanced Options
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
  name: 'AdminSearch',
  data() {
    return {
      searchBy: 'user_id',
      searchQuery: '',
      userResult: null,
      parkingLots: [],
      vehicleResults: [],
      loading: false,
      error: '',
      showAdvanced: false,
      filters: {
        startDate: '',
        endDate: '',
        status: ''
      },
      searchTypes: [
        { value: 'user_id', label: 'User ID', icon: 'bi bi-person' },
        { value: 'location', label: 'Location', icon: 'bi bi-geo-alt' },
        { value: 'vehicle', label: 'Vehicle', icon: 'bi bi-car-front' }
      ],
      baseURL: 'http://127.0.0.1:5000',
      lastRequestURL: ''
    }
  },
  computed: {
    showNoResults() {
      if (this.loading || this.error) return false
      if (this.searchBy === 'user_id') return this.searchQuery && !this.userResult
      if (this.searchBy === 'location') return this.searchQuery && this.parkingLots.length === 0
      if (this.searchBy === 'vehicle') return this.searchQuery && this.vehicleResults.length === 0
      return false
    },
    hasResults() {
      return this.userResult || this.parkingLots.length > 0 || this.vehicleResults.length > 0
    }
  },
  methods: {
    async logout() {
      await authService.logout();
      this.$router.push('/login');
    },

    toggleAdvanced() {
      this.showAdvanced = !this.showAdvanced
    },

    getCurrentSearchIcon() {
      const type = this.searchTypes.find(t => t.value === this.searchBy)
      return type ? type.icon : 'bi bi-search'
    },

    getPlaceholder() {
      if (this.searchBy === 'user_id') return 'Enter User ID (e.g., 1)'
      if (this.searchBy === 'location') return 'Enter location name or address'
      if (this.searchBy === 'vehicle') return 'Enter vehicle number (e.g., KA01AB1234)'
      return 'Enter search term'
    },

    clearResults() {
      this.userResult = null
      this.parkingLots = []
      this.vehicleResults = []
      this.error = ''
    },

    clearSearch() {
      this.searchQuery = ''
      this.clearResults()
    },

    clearAllResults() {
      this.clearSearch()
      this.filters = {
        startDate: '',
        endDate: '',
        status: ''
      }
    },

    getInitials(name) {
      if (!name) return '?'
      const parts = name.split(' ')
      if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase()
      }
      return name.substring(0, 2).toUpperCase()
    },

    getOccupancyPercentage(lot) {
      if (!lot.max_spots || lot.max_spots === 0) return 0
      const occupied = lot.occupied || 0
      return Math.round((occupied / lot.max_spots) * 100)
    },

    getOccupancyClass(lot) {
      const percentage = this.getOccupancyPercentage(lot)
      if (percentage >= 90) return 'critical'
      if (percentage >= 70) return 'high'
      if (percentage >= 50) return 'medium'
      return 'low'
    },

    getSpotStatusClass(status) {
      if (!status) return 'unknown'
      const normalized = status.toString().toUpperCase().trim()
      
      if (['OCCUPIED', 'PARKED', 'BOOKED', 'TAKEN', 'BUSY', 'O'].includes(normalized)) {
        return 'occupied'
      }
      if (['AVAILABLE', 'FREE', 'EMPTY', 'VACANT', 'OPEN', 'A'].includes(normalized)) {
        return 'available'
      }
      if (['RESERVED', 'RESERVED_SPOT', 'HOLD', 'R'].includes(normalized)) {
        return 'reserved'
      }
      return 'unknown'
    },

    getSpotStatusLabel(status) {
      if (!status) return 'Unknown'
      const normalized = status.toString().toUpperCase().trim()
      
      if (['OCCUPIED', 'PARKED', 'BOOKED', 'TAKEN', 'BUSY', 'O'].includes(normalized)) {
        return 'Occupied'
      }
      if (['AVAILABLE', 'FREE', 'EMPTY', 'VACANT', 'OPEN', 'A'].includes(normalized)) {
        return 'Available'
      }
      if (['RESERVED', 'RESERVED_SPOT', 'HOLD', 'R'].includes(normalized)) {
        return 'Reserved'
      }
      return status
    },

    async handleSearch() {
      if (!this.searchQuery.trim()) {
        this.error = 'Please enter a search term'
        return
      }

      this.loading = true
      this.clearResults()

      try {
        if (this.searchBy === 'user_id') {
          await this.searchUser()
        } else if (this.searchBy === 'location') {
          await this.searchLocation()
        } else if (this.searchBy === 'vehicle') {
          await this.searchVehicle()
        }
      } catch (err) {
        console.error('Search error:', err)
        
        if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
          this.error = 'Backend server is not running. Please start the server on port 5000.'
        } else if (err.response?.status === 404) {
          this.error = `No ${this.searchBy === 'user_id' ? 'user' : this.searchBy} found with this ${this.searchBy === 'user_id' ? 'ID' : 'criteria'}.`
        } else if (err.response?.status === 401) {
          this.error = 'Authentication failed. Please login again.'
          setTimeout(() => this.logout(), 2000)
        } else if (err.response?.status === 400) {
          this.error = err.response?.data?.message || 'Invalid search parameter'
        } else {
          this.error = err.response?.data?.error || err.response?.data?.message || 'Search failed. Please try again.'
        }
      } finally {
        this.loading = false
      }
    },

    async searchUser() {
      try {
        const userId = this.searchQuery.trim()
        // Try different possible endpoints for user search
        let url = `${this.baseURL}/admin/api/users`
        let response
        
        console.log('Searching for user ID:', userId)
        
        try {
          // First try getting all users and filter by ID
          response = await axios.get(url, {
            headers: { 
              'Content-Type': 'application/json'
            },
            timeout: 10000
          })
          
          console.log('All users response:', response.data)
          
          // Filter for the specific user ID
          if (Array.isArray(response.data)) {
            const foundUser = response.data.find(user => user.id.toString() === userId.toString())
            if (foundUser) {
              this.userResult = foundUser
            } else {
              throw new Error('User not found')
            }
          } else {
            throw new Error('Invalid response format')
          }
          
        } catch (error) {
          // If that fails, try the search endpoint
          if (error.response?.status === 404 || error.message === 'User not found') {
            url = `${this.baseURL}/admin/api/search-user`
            this.lastRequestURL = `${url}?user_id=${userId}`
            
            response = await axios.get(url, {
              params: { user_id: userId },
              headers: { 
                'Content-Type': 'application/json'
              },
              timeout: 10000
            })
            
            this.userResult = response.data
          } else {
            throw error
          }
        }
        
      } catch (error) {
        console.error('User search error:', error)
        throw error
      }
    },

    async searchLocation() {
      try {
        const url = `${this.baseURL}/admin/api/search-location`
        this.lastRequestURL = `${url}?location=${this.searchQuery.trim()}`
        
        console.log('Making location search request to:', this.lastRequestURL)
        
        const response = await axios.get(url, {
          params: { location: this.searchQuery.trim() },
          headers: { 
            'Content-Type': 'application/json'
          },
          timeout: 10000
        })
        
        console.log('Location search response:', response.data)
        
        if (Array.isArray(response.data)) {
          // Add price_per_hour if missing by fetching from parking lots
          for (let lot of response.data) {
            if (!lot.price_per_hour) {
              try {
                const lotDetailsResponse = await axios.get(`${this.baseURL}/admin/parking-lots`)
                const fullLot = lotDetailsResponse.data.find(l => l.id === lot.id)
                if (fullLot) {
                  lot.price_per_hour = fullLot.price_per_hour
                }
              } catch (err) {
                console.warn(`Could not fetch price for lot ${lot.id}:`, err)
                lot.price_per_hour = 'N/A'
              }
            }
          }
          this.parkingLots = response.data
        } else {
          this.parkingLots = []
        }
      } catch (error) {
        console.error('Location search error:', error)
        throw error
      }
    },

    async searchVehicle() {
      try {
        const url = `${this.baseURL}/admin/api/search-vehicle`
        this.lastRequestURL = `${url}?vehicle_no=${this.searchQuery.trim().toUpperCase()}`
        
        console.log('Making request to:', this.lastRequestURL)
        
        const response = await axios.get(url, {
          params: { vehicle_no: this.searchQuery.trim().toUpperCase() },
          headers: { 
            'Content-Type': 'application/json'
          },
          timeout: 10000
        })
        
        console.log('Response:', response.data)
        this.vehicleResults = Array.isArray(response.data) ? response.data : []
      } catch (error) {
        console.error('Vehicle search error:', error)
        // If vehicle search endpoint doesn't exist, show appropriate error
        if (error.response?.status === 404) {
          this.error = 'Vehicle search endpoint not implemented yet'
        } else {
          throw error
        }
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return new Date(dateString).toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return 'Invalid date'
      }
    },

    // Test backend connection
    async testBackendConnection() {
      try {
        const response = await axios.get(`${this.baseURL}/admin/parking-lots`)
        console.log('Backend connection test successful')
        return true
      } catch (error) {
        console.error('Backend connection failed:', error)
        return false
      }
    }
  },

  async mounted() {
    // Test backend connection on component mount
    const isConnected = await this.testBackendConnection()
    if (!isConnected) {
      this.error = 'Cannot connect to backend server. Please ensure the server is running on port 5000.'
    }
  }
}
</script>

<style scoped>
/* Base Styles */
.admin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 10px;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.welcome-text {
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 30px;
  font-size: 1.1rem;
}

/* Navigation */
.top-nav {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.nav-content {
  padding: 15px 30px;
}

.nav-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.nav-links a {
  text-decoration: none;
  color: #64748b;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
  background: transparent;
}

.nav-links a:hover,
.nav-links a.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-danger {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #ff5252, #d32f2f);
  transform: translateY(-2px);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a67d8, #6b46c1);
  transform: translateY(-2px);
}

.btn-outline-primary {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline-primary:hover {
  background: #667eea;
  color: white;
}

.btn-outline-secondary {
  background: transparent;
  color: #64748b;
  border: 2px solid #64748b;
}

.btn-outline-secondary:hover {
  background: #64748b;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.875rem;
}

/* Search Card */
.search-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.search-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-title i {
  font-size: 1.5rem;
  color: #667eea;
}

.search-title h4 {
  margin: 0;
  color: #1e293b;
  font-size: 1.5rem;
  font-weight: 700;
}

.search-actions {
  display: flex;
  gap: 10px;
}

/* Search Type Selector */
.search-type-selector {
  margin-bottom: 25px;
}

.type-tabs {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.type-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  color: #64748b;
}

.type-tab:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
}

.type-tab.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* Search Input */
.search-input-section {
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  align-items: center;
  max-width: 600px;
  margin: 0 auto;
  border: 2px solid #e2e8f0;
  border-radius: 15px;
  background: white;
  overflow: hidden;
  transition: border-color 0.3s ease;
}

.input-group:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-icon {
  padding: 15px;
  color: #667eea;
  background: #f8fafc;
}

.search-input {
  flex: 1;
  padding: 15px;
  border: none;
  font-size: 1rem;
  outline: none;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-btn {
  padding: 15px 25px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a67d8, #6b46c1);
}

.search-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

/* Advanced Options */
.advanced-options {
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
  margin-top: 20px;
}

.advanced-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.option-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-inputs span {
  color: #64748b;
  font-weight: 500;
}

.form-control {
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
}

/* Status Messages */
.status-message {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.status-message.error {
  background: rgba(254, 226, 226, 0.95);
  color: #dc2626;
  border: 1px solid #fecaca;
}

.spinner, .spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-sm {
  width: 16px;
  height: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

.retry-btn:hover {
  background: rgba(220, 38, 38, 0.1);
}

/* Results Section */
.results-section {
  margin-top: 30px;
}

.results-container {
  margin-bottom: 30px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 5px;
}

.results-header h4 {
  margin: 0;
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

.result-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

/* User Results */
.user-result-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 25px;
}

.user-avatar {
  font-size: 4rem;
  color: #667eea;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 5px;
}

.user-email {
  color: #64748b;
  margin-bottom: 15px;
}

.user-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.9rem;
}

.meta-item i {
  color: #667eea;
}

.user-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Location Results */
.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.location-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.location-card:hover {
  transform: translateY(-5px);
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.location-header h5 {
  margin: 0;
  color: #1e293b;
  font-size: 1.3rem;
  font-weight: 700;
}

.occupancy-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.occupancy-badge.low {
  background: #dcfce7;
  color: #166534;
}

.occupancy-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.occupancy-badge.high {
  background: #fed7aa;
  color: #c2410c;
}

.occupancy-badge.critical {
  background: #fecaca;
  color: #dc2626;
}

.location-address {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  margin-bottom: 15px;
}

.location-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
  font-weight: 600;
}

.stat-item i {
  color: #667eea;
}

/* Spot Visualization */
.spot-visualization {
  margin: 20px 0;
}

.spot-legend {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #64748b;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-item.available .legend-color {
  background: #10b981;
}

.legend-item.occupied .legend-color {
  background: #ef4444;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 8px;
  max-width: 100%;
}

.spot-visual {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.spot-visual:hover {
  transform: scale(1.1);
}

.spot-visual.available {
  background: #dcfce7;
  color: #166534;
  border: 2px solid #10b981;
}

.spot-visual.occupied {
  background: #fecaca;
  color: #dc2626;
  border: 2px solid #ef4444;
}

.spot-visual.reserved {
  background: #dbeafe;
  color: #1d4ed8;
  border: 2px solid #3b82f6;
}

.spot-visual.unknown {
  background: #f1f5f9;
  color: #64748b;
  border: 2px solid #94a3b8;
}

.location-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Vehicle Results */
.vehicles-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.vehicle-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.3s ease;
}

.vehicle-card:hover {
  transform: translateY(-2px);
}

.vehicle-icon {
  font-size: 2.5rem;
  color: #667eea;
}

.vehicle-info {
  flex: 1;
}

.vehicle-number {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.vehicle-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 0.9rem;
}

.detail-item i {
  color: #667eea;
}

.vehicle-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.occupied {
  background: #fecaca;
  color: #dc2626;
}

.status-badge.available {
  background: #dcfce7;
  color: #166534;
}

.status-badge.reserved {
  background: #dbeafe;
  color: #1d4ed8;
}

/* No Results */
.no-results {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.no-results-icon {
  font-size: 4rem;
  color: #94a3b8;
  margin-bottom: 20px;
}

.no-results h4 {
  color: #374151;
  margin-bottom: 10px;
}

.no-results p {
  color: #64748b;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.no-results-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-container {
    padding: 15px;
  }

  .header {
    font-size: 2rem;
  }

  .nav-links {
    justify-content: center;
    gap: 10px;
  }

  .nav-links a,
  .btn {
    padding: 8px 15px;
    font-size: 0.9rem;
  }

  .search-card {
    padding: 20px;
  }

  .search-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .type-tabs {
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 5px;
  }

  .input-group {
    flex-direction: column;
    max-width: none;
  }

  .search-btn {
    border-radius: 0 0 15px 15px;
    justify-content: center;
  }

  .advanced-grid {
    grid-template-columns: 1fr;
  }

  .date-inputs {
    flex-direction: column;
    align-items: stretch;
  }

  .user-result-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .user-actions {
    flex-direction: row;
    justify-content: center;
  }

  .locations-grid {
    grid-template-columns: 1fr;
  }

  .location-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .location-stats {
    flex-direction: column;
    gap: 10px;
  }

  .user-meta {
    justify-content: center;
  }

  .vehicle-card {
    flex-direction: column;
    text-align: center;
  }

  .vehicle-details {
    justify-content: center;
  }

  .spots-grid {
    grid-template-columns: repeat(auto-fill, minmax(35px, 1fr));
  }

  .spot-visual {
    width: 35px;
    height: 35px;
    font-size: 0.7rem;
  }

  .no-results {
    padding: 40px 20px;
  }

  .no-results-actions {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .search-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }

  .search-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .type-tabs {
    gap: 5px;
  }

  .type-tab {
    padding: 10px 15px;
    font-size: 0.9rem;
  }
}
</style>
