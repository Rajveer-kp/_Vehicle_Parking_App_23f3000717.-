<template>
  <div class="admin-container">
    <h2 class="header">Admin Dashboard</h2>
    <p class="welcome-text">Welcome to Admin</p>

    <!-- Navigation -->
    <nav class="top-nav">
      <div class="nav-content">
        <div class="nav-links">
          <router-link to="/admin">Home</router-link>
          <router-link to="/admin/registered-users" class="nav-link">Users</router-link>
          <router-link to="/admin/search">Search</router-link>
          <router-link to="/admin/summary">Summary</router-link>
          <button @click="logout" class="btn btn-danger">Logout</button>
        </div>
        
      </div>
    </nav>

    <!-- Quick Stats -->
    <div class="stats-container">
      <div class="stat-card">
        <h3>{{ totalLots }}</h3>
        <p>Total Lots</p>
      </div>
      <div class="stat-card">
        <h3>{{ totalSpots }}</h3>
        <p>Total Spots</p>
      </div>
      <div class="stat-card">
        <h3>{{ occupiedSpots }}</h3>
        <p>Occupied</p>
      </div>
      <div class="stat-card">
        <h3>{{ availableSpots }}</h3>
        <p>Available</p>
      </div>
    </div>

    <!-- Refresh Button -->
    <div class="action-bar">
      <button @click="refreshData" class="btn btn-primary" :disabled="loading">
        <span v-if="loading">Refreshing...</span>
        <span v-else>🔄 Refresh Data</span>
      </button>
    </div>

    <!-- Status Messages -->
    <div v-if="loading" class="status-message">
      <div class="spinner"></div>
      Loading parking lots...
    </div>
    <div v-else-if="error" class="status-message error">
      {{ error }}
      <button @click="refreshData" class="retry-btn">Retry</button>
    </div>

    <!-- Parking Lots Section -->
    <h4 class="section-title">Parking Lots Management</h4>
    <div v-if="!loading && parkingLots.length === 0" class="no-lots">
      <div class="empty-state">
        <h3>No parking lots found</h3>
        <p>Start by adding your first parking lot</p>
        <router-link to="/admin/add-lot" class="btn btn-success">+ Add First Lot</router-link>
      </div>
    </div>

    <div class="lots-container" v-else>
      <div v-for="lot in parkingLots" :key="lot.id" class="lot-card">
        <div class="lot-header">
          <div class="lot-title-section">
            <h5 class="lot-name">{{ lot.name }}</h5>
            <span class="lot-address">{{ lot.address }}</span>
          </div>
          <div class="lot-actions">
            
            <button @click="editLot(lot.id)" class="edit-btn">Edit</button>
            <button 
              @click="deleteLot(lot.id)" 
              class="delete-btn"
              :disabled="getOccupiedCount(lot) > 0"
              :title="getOccupiedCount(lot) > 0 ? 'Cannot delete: Parking lot has occupied spots' : 'Delete parking lot'"
            >
              Delete
            </button>
          </div>
        </div>

        <div class="lot-info">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">Price/Hour:</span>
              <span class="value">₹{{ lot.price_per_hour }}</span>
            </div>
            <div class="info-item">
              <span class="label">Total Spots:</span>
              <span class="value">{{ lot.max_spots }}</span>
            </div>
            <div class="info-item">
              <span class="label">Occupied:</span>
              <span class="value occupied-count">{{ getOccupiedCount(lot) }}</span>
            </div>
            <div class="info-item">
              <span class="label">Available:</span>
              <span class="value available-count">{{ getAvailableCount(lot) }}</span>
            </div>
          </div>
        </div>

        <!-- Occupancy Bar -->
        <div class="occupancy-bar">
          <div 
            class="occupancy-fill" 
            :style="{ width: getOccupancyPercentage(lot) + '%' }"
          ></div>
        </div>
        <p class="occupancy-text">{{ getOccupancyPercentage(lot) }}% Occupied</p>

        <!-- Spot Grid -->
        <div class="spot-grid">
          <button
            v-for="spot in (lot.spots || [])"
            :key="spot.spot_id"
            :class="['spot-button', getStatusClass(spot.status)]"
            @click="openSpotDetails(spot.spot_id, lot.id, spot.status)"
            :title="`Spot ${spot.spot_id} - ${getStatusLabel(spot.status)}`"
          >
            <div class="spot-number">{{ spot.spot_id }}</div>
            <div class="spot-status">{{ getStatusLabel(spot.status) }}</div>
          </button>
        </div>
      </div>
    </div>

    <!-- Add Lot Button -->
    <div class="add-lot-section">
      <router-link to="/admin/add-lot" class="add-lot-btn">
        <span>+</span>
        Add New Parking Lot
      </router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import authService from '../services/auth.js';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      parkingLots: [],
      loading: false,
      error: '',
      refreshInterval: null
    };
  },
  computed: {
    totalLots() {
      return this.parkingLots.length;
    },
    totalSpots() {
      return this.parkingLots.reduce((sum, lot) => sum + (lot.max_spots || 0), 0);
    },
    occupiedSpots() {
      return this.parkingLots.reduce((sum, lot) => sum + this.getOccupiedCount(lot), 0);
    },
    availableSpots() {
      return this.totalSpots - this.occupiedSpots;
    }
  },
  methods: {
    async logout() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      await authService.logout();
      this.$router.push('/login');
    },

    async refreshData() {
      await this.fetchParkingLots();
    },

    async fetchParkingLots() {
      this.loading = true;
      this.error = '';
      
      try {
        // Fetch parking lots
        const { data: lots } = await axios.get('http://localhost:5000/admin/parking-lots');
        
        if (!lots || !Array.isArray(lots)) {
          throw new Error('Invalid parking lots data received');
        }

        // Fetch spots for each lot with better error handling
        const lotsWithSpots = await Promise.allSettled(
          lots.map(async (lot) => {
            try {
              const { data } = await axios.get(`http://localhost:5000/admin/parking-lots/${lot.id}/spots`);
              return {
                ...lot,
                spots: data.spots || []
              };
            } catch (err) {
              console.error(`Failed to load spots for lot ${lot.id}:`, err);
              // Return lot with empty spots array instead of failing
              return {
                ...lot,
                spots: []
              };
            }
          })
        );

        // Extract successful results
        this.parkingLots = lotsWithSpots
          .filter(result => result.status === 'fulfilled')
          .map(result => result.value);

        // Log any failed requests
        const failedLots = lotsWithSpots.filter(result => result.status === 'rejected');
        if (failedLots.length > 0) {
          console.warn(`Failed to load ${failedLots.length} parking lots`);
        }

      } catch (err) {
        this.error = 'Failed to fetch parking lots. Please try again.';
        console.error('Fetch parking lots error:', err);
      } finally {
        this.loading = false;
      }
    },

    async deleteLot(lotId) {
      // Find the lot to check for occupied spots
      const lot = this.parkingLots.find(l => l.id === lotId);
      if (!lot) {
        alert('Parking lot not found.');
        return;
      }

      // Check if there are any occupied spots
      const occupiedCount = this.getOccupiedCount(lot);
      if (occupiedCount > 0) {
        alert(`Cannot delete parking lot "${lot.name}". There are ${occupiedCount} occupied spot(s). Please ensure all spots are available before deleting.`);
        return;
      }

      if (!confirm(`Are you sure you want to delete parking lot "${lot.name}"? This action cannot be undone.`)) {
        return;
      }

      try {
        await axios.delete(`http://localhost:5000/admin/delete-parking-lot/${lotId}`);
        this.parkingLots = this.parkingLots.filter(lot => lot.id !== lotId);
        this.$toast?.success?.('Parking lot deleted successfully');
      } catch (err) {
        const errorMsg = err.response?.data?.error || 'Failed to delete parking lot.';
        this.$toast?.error?.(errorMsg) || alert(errorMsg);
        console.error('Delete lot error:', err);
      }
    },

    openSpotDetails(spotId, lotId, status) {
      this.$router.push({
        name: 'SpotDetails',
        params: {
          lotId: String(lotId),
          spotId: String(spotId)
        },
        query: { status }
      });
    },

    editLot(lotId) {
      this.$router.push(`/admin/edit-lot/${lotId}`);
    },

    viewLotDetails(lotId) {
      this.$router.push(`/admin/lot/${lotId}`);
    },

    // Fixed status classification logic
    getStatusClass(status) {
      if (!status) return 'unknown';
      
      const normalized = status.toString().toUpperCase().trim();
      
      // More comprehensive status checking
      if (['OCCUPIED', 'PARKED', 'BOOKED', 'TAKEN', 'BUSY', 'O'].includes(normalized)) {
        return 'occupied';
      }
      if (['AVAILABLE', 'FREE', 'EMPTY', 'VACANT', 'OPEN', 'A'].includes(normalized)) {
        return 'available';
      }
      if (['RESERVED', 'RESERVED_SPOT', 'HOLD', 'R'].includes(normalized)) {
        return 'reserved';
      }
      if (['MAINTENANCE', 'OUT_OF_ORDER', 'BLOCKED', 'M'].includes(normalized)) {
        return 'maintenance';
      }
      
      return 'unknown';
    },

    getStatusLabel(status) {
      if (!status) return 'Unknown';
      
      const normalized = status.toString().toUpperCase().trim();
      
      if (['OCCUPIED', 'PARKED', 'BOOKED', 'TAKEN', 'BUSY', 'O'].includes(normalized)) {
        return 'Occupied';
      }
      if (['AVAILABLE', 'FREE', 'EMPTY', 'VACANT', 'OPEN', 'A'].includes(normalized)) {
        return 'Available';
      }
      if (['RESERVED', 'RESERVED_SPOT', 'HOLD', 'R'].includes(normalized)) {
        return 'Reserved';
      }
      if (['MAINTENANCE', 'OUT_OF_ORDER', 'BLOCKED', 'M'].includes(normalized)) {
        return 'Maintenance';
      }
      
      return 'Unknown';
    },

    getOccupiedCount(lot) {
      if (!lot.spots || !Array.isArray(lot.spots)) return 0;
      return lot.spots.filter(spot => this.getStatusClass(spot.status) === 'occupied').length;
    },

    getAvailableCount(lot) {
      if (!lot.spots || !Array.isArray(lot.spots)) return lot.max_spots || 0;
      const occupied = this.getOccupiedCount(lot);
      return Math.max(0, (lot.max_spots || 0) - occupied);
    },

    getOccupancyPercentage(lot) {
      if (!lot.max_spots) return 0;
      const occupied = this.getOccupiedCount(lot);
      return Math.round((occupied / lot.max_spots) * 100);
    }
  },

  async created() {
    await this.fetchParkingLots();
    
    // Auto-refresh every 30 seconds
    this.refreshInterval = setInterval(() => {
      if (!this.loading) {
        this.fetchParkingLots();
      }
    }, 30000);
  },

  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },

  watch: {
    '$route'(to, from) {
      if (to.path.startsWith('/admin') && to.path !== from.path) {
        this.fetchParkingLots();
      }
    }
  }
};
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

.btn-success {
  background-color: #28a745;
  color: white;
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
  justify-content: center;
  margin-bottom: 20px;
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

.section-title {
  color: #333;
  margin-bottom: 25px;
  font-size: 1.8em;
  text-align: center;
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

.lots-container {
  display: grid;
  gap: 25px;
  margin-bottom: 40px;
}

.lot-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  border: 1px solid #e9ecef;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.lot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.lot-title-section {
  flex: 1;
}

.lot-name {
  color: #333;
  margin: 0 0 5px 0;
  font-size: 1.4em;
  font-weight: 600;
}

.lot-address {
  color: #666;
  font-size: 0.9em;
}

.lot-actions {
  display: flex;
  gap: 8px;
}

.view-btn, .edit-btn, .delete-btn {
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.view-btn {
  background-color: #17a2b8;
  color: white;
}

.view-btn:hover {
  background-color: #138496;
}

.edit-btn {
  background-color: #007bff;
  color: white;
}

.edit-btn:hover {
  background-color: #0056b3;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover:not(:disabled) {
  background-color: #c82333;
}

.delete-btn:disabled {
  background-color: #6c757d;
  color: #adb5bd;
  cursor: not-allowed;
  opacity: 0.6;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.label {
  font-size: 0.85em;
  color: #666;
  font-weight: 500;
}

.value {
  font-size: 1.1em;
  font-weight: 600;
  color: #333;
}

.occupied-count {
  color: #dc3545;
}

.available-count {
  color: #28a745;
}

.occupancy-bar {
  width: 100%;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.occupancy-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745 0%, #ffc107 50%, #dc3545 100%);
  transition: width 0.3s ease;
}

.occupancy-text {
  text-align: center;
  font-size: 0.9em;
  color: #666;
  margin-bottom: 20px;
}

.spot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.spot-button {
  padding: 12px 8px;
  border: 2px solid;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 12px;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-height: 70px;
}

.spot-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.spot-number {
  font-weight: 700;
  font-size: 14px;
}

.spot-status {
  font-size: 10px;
  text-transform: uppercase;
}

.spot-button.available {
  background-color: #d4edda;
  border-color: #28a745;
  color: #155724;
}

.spot-button.available:hover {
  background-color: #28a745;
  color: white;
}

.spot-button.occupied {
  background-color: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
}

.spot-button.occupied:hover {
  background-color: #dc3545;
  color: white;
}

.spot-button.reserved {
  background-color: #fff3cd;
  border-color: #ffc107;
  color: #856404;
}

.spot-button.reserved:hover {
  background-color: #ffc107;
  color: white;
}

.spot-button.maintenance {
  background-color: #f4f4f4;
  border-color: #6c757d;
  color: #495057;
}

.spot-button.maintenance:hover {
  background-color: #6c757d;
  color: white;
}

.spot-button.unknown {
  background-color: #e2e3e5;
  border-color: #6c757d;
  color: #495057;
}

.add-lot-section {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.add-lot-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 18px 35px;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1.1em;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.add-lot-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
  text-decoration: none;
  color: white;
}

.add-lot-btn span {
  font-size: 1.3em;
  font-weight: 700;
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
  
  .lot-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .lot-actions {
    justify-content: center;
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .spot-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}
</style>