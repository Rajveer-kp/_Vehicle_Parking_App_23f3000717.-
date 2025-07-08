<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h4 class="modal-title">🚪 Release Parking Spot</h4>
        <button class="close-btn" @click="$emit('close')" type="button">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- Parking Details -->
      <div class="parking-info">
        <div class="info-header">
          <i class="bi bi-car-front-fill"></i>
          <strong>Parking Details</strong>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Location:</span>
            <span class="info-value">{{ history.location || 'Unknown Location' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Vehicle:</span>
            <span class="info-value vehicle-badge">{{ history.vehicle_no }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Spot:</span>
            <span class="info-value spot-badge">#{{ history.spot_id }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Status:</span>
            <span class="info-value status-badge">{{ history.status }}</span>
          </div>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="error-alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        <span>{{ error }}</span>
        <button @click="clearError" class="error-close">×</button>
      </div>

      <!-- Success Alert -->
      <div v-if="success" class="success-alert">
        <i class="bi bi-check-circle-fill"></i>
        <span>{{ success }}</span>
      </div>

      <!-- Loading State -->
      <div v-if="calculatingCost" class="loading-state">
        <div class="spinner"></div>
        <p>Calculating parking cost...</p>
      </div>

      <form @submit.prevent="releaseSpot" class="release-form">
        <div class="form-grid">
          <div class="input-group">
            <label class="label">
              <i class="bi bi-calendar-check"></i>
              Entry Time
            </label>
            <input 
              type="text" 
              class="input-field disabled" 
              :value="formatDateTime(history.entry_time || history.timestamp)" 
              disabled 
            />
          </div>

          <div class="input-group">
            <label class="label">
              <i class="bi bi-calendar-x"></i>
              Release Time
              <span class="live-indicator">🔴 LIVE</span>
            </label>
            <input 
              type="text" 
              class="input-field disabled live-time" 
              :value="releaseTime" 
              disabled 
            />
          </div>
        </div>

        <div class="input-group">
          <label class="label">
            <i class="bi bi-clock"></i>
            Parking Duration
            <span class="live-indicator">⏱️ LIVE</span>
          </label>
          <input 
            type="text" 
            class="input-field disabled duration-field live-time" 
            :value="parkingDuration" 
            disabled 
          />
        </div>

        <!-- Cost Breakdown -->
        <div class="cost-breakdown">
          <h6>💰 Real-Time Cost Breakdown</h6>
          <div class="cost-row">
            <span>Hourly Rate:</span>
            <span>₹{{ hourlyRate }}/hour</span>
          </div>
          <div class="cost-row">
            <span>Duration:</span>
            <span>{{ formattedHoursParked }}</span>
          </div>
          <div class="cost-row">
            <span>Base Cost:</span>
            <span class="live-cost">₹{{ baseCost }}</span>
          </div>
          <div v-if="additionalCharges > 0" class="cost-row">
            <span>Additional Charges:</span>
            <span class="live-cost">₹{{ additionalCharges }}</span>
          </div>
          <div class="cost-row total-cost">
            <span>Total Amount:</span>
            <span class="live-cost pulse">₹{{ totalCost }}</span>
          </div>
          <div class="real-time-note">
            <i class="bi bi-info-circle"></i>
            Cost updates automatically every minute
          </div>
        </div>

        <div class="button-group">
          <button 
            type="submit" 
            class="btn release-btn" 
            :disabled="loading || calculatingCost"
          >
            <span v-if="loading">
              <i class="bi bi-arrow-clockwise spinning"></i>
              Releasing...
            </span>
            <span v-else>
              <i class="bi bi-box-arrow-right"></i>
              Release & Pay ₹{{ totalCost }}
              <small class="live-badge">LIVE</small>
            </span>
          </button>
          <button 
            type="button" 
            class="btn cancel-btn" 
            @click="$emit('close')"
            :disabled="loading"
          >
            <i class="bi bi-x-circle"></i>
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Release',
  props: {
    history: {
      type: Object,
      required: true
    },
    userId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      currentTime: new Date(),
      loading: false,
      calculatingCost: false,
      error: '',
      success: '',
      hourlyRate: 50,
      hoursParked: 1,
      baseCost: 0,
      additionalCharges: 0,
      totalCost: 0,
      realTimeInterval: null,
      costUpdateInterval: null
    }
  },
  computed: {
    releaseTime() {
      return this.currentTime.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    parkingDuration() {
      const start = new Date(this.history.entry_time || this.history.timestamp);
      const end = this.currentTime;
      const diffMs = end - start;
      
      if (diffMs < 0) return '0 minutes';
      
      const totalMinutes = Math.floor(diffMs / (1000 * 60));
      const hours = Math.floor(totalMinutes / 60);
      const minutes = totalMinutes % 60;
      const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
      
      if (hours === 0 && minutes === 0) {
        return `${seconds} second(s)`;
      } else if (hours === 0) {
        return `${minutes} minute(s) ${seconds} second(s)`;
      } else {
        return `${hours} hour(s) ${minutes} minute(s)`;
      }
    },
    exactHoursParked() {
      const start = new Date(this.history.entry_time || this.history.timestamp);
      const end = this.currentTime;
      const diffMs = Math.max(0, end - start);
      return diffMs / (1000 * 60 * 60);
    },
    formattedHoursParked() {
      const exact = this.exactHoursParked;
      if (exact < 1) {
        const minutes = Math.ceil(exact * 60);
        return `${minutes} minute(s) (billed as 1 hour)`;
      }
      return `${exact.toFixed(2)} hour(s)`;
    }
  },
  async mounted() {
    // Start real-time clock updates
    this.startRealTimeUpdates();
    
    // Initial cost calculation
    await this.calculateCost();
    
    // Update cost every 30 seconds for real-time pricing
    this.costUpdateInterval = setInterval(() => {
      this.calculateCost();
    }, 30000);
  },

  beforeUnmount() {
    this.stopRealTimeUpdates();
    if (this.costUpdateInterval) {
      clearInterval(this.costUpdateInterval);
    }
  },
  methods: {
    async releaseSpot() {
      this.loading = true;
      this.error = '';
      this.success = '';

      try {
        console.log('Releasing spot with data:', {
          historyId: this.history.id,
          userId: this.userId,
          totalCost: this.totalCost
        });

        // Fixed API endpoint to match backend routes
        const response = await axios.post('http://localhost:5000/user/release-spot', {
          historyId: this.history.id,
          releaseTime: this.currentTime.toISOString(),
          totalCost: this.totalCost,
          duration: this.parkingDuration,
          hoursParked: this.hoursParked
        }, {
          headers: {
            'X-User-ID': this.userId,
            'Content-Type': 'application/json'
          },
          timeout: 10000
        });

        console.log('Release response:', response.data);

        this.success = response.data.message || 'Parking spot released successfully!';
        
        // Emit success with release details
        this.$emit('success', {
          message: this.success,
          releaseId: response.data.release_id,
          totalCost: this.totalCost,
          duration: this.parkingDuration,
          vehicleNo: this.history.vehicle_no
        });

        // Close modal after 2 seconds
        setTimeout(() => {
          this.$emit('close');
        }, 2000);

      } catch (error) {
        console.error('Release error:', error);
        
        if (error.response) {
          // Server responded with error
          this.error = error.response.data?.error || `Error: ${error.response.status}`;
        } else if (error.request) {
          // Request made but no response
          this.error = 'No response from server. Please check your connection.';
        } else {
          // Something else happened
          this.error = error.message || 'An unexpected error occurred';
        }
      } finally {
        this.loading = false;
      }
    },

    async calculateCost() {
      try {
        // Get parking lot details for accurate pricing
        const lotResponse = await axios.get(`http://localhost:5000/user/parking-lot/${this.history.lot_id}`, {
          headers: {
            'X-User-ID': this.userId,
            'Content-Type': 'application/json'
          }
        });
        
        this.hourlyRate = lotResponse.data.price_per_hour || 50;
        
      } catch (error) {
        console.warn('Could not fetch lot details, using default rate:', error);
        this.hourlyRate = 50; // Default rate
      }

      // Calculate parking duration using current time
      const exactHours = this.exactHoursParked;
      
      // Calculate hours (minimum 1 hour, round up to next hour)
      this.hoursParked = Math.max(1, Math.ceil(exactHours));
      
      // Calculate costs
      this.baseCost = this.hoursParked * this.hourlyRate;
      
      // Add additional charges for extended parking (more than 12 hours)
      if (this.hoursParked > 12) {
        this.additionalCharges = Math.floor((this.hoursParked - 12) / 12) * 100;
      } else {
        this.additionalCharges = 0;
      }
      
      this.totalCost = this.baseCost + this.additionalCharges;
    },

    startRealTimeUpdates() {
      // Update current time every second for real-time display
      this.realTimeInterval = setInterval(() => {
        this.currentTime = new Date();
        // Recalculate cost every minute
        if (this.currentTime.getSeconds() === 0) {
          this.calculateCost();
        }
      }, 1000);
    },

    stopRealTimeUpdates() {
      if (this.realTimeInterval) {
        clearInterval(this.realTimeInterval);
        this.realTimeInterval = null;
      }
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

    clearError() {
      this.error = '';
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 650px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes slideIn {
  from {
    transform: translateY(-50px) scale(0.9);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 40px 20px;
  border-bottom: 2px solid #f1f3f4;
}

.modal-title {
  margin: 0;
  font-size: 26px;
  color: #333;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #6c757d;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #dc3545;
}

.parking-info {
  padding: 20px 40px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  color: #495057;
  font-weight: 600;
}

.info-header i {
  font-size: 18px;
  color: #007bff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.info-label {
  color: #6c757d;
  font-size: 13px;
  font-weight: 500;
}

.info-value {
  color: #495057;
  font-weight: 600;
}

.vehicle-badge {
  background: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.spot-badge {
  background: #17a2b8;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge {
  background: #dc3545;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.error-alert {
  background: linear-gradient(45deg, #dc3545, #c82333);
  color: white;
  padding: 15px 20px;
  margin: 20px 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.success-alert {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
  padding: 15px 20px;
  margin: 20px 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.error-close {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  margin-left: auto;
  padding: 0;
  width: 20px;
  height: 20px;
}

.loading-state {
  text-align: center;
  padding: 30px 20px;
  color: #6c757d;
  margin: 20px 40px;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.release-form {
  padding: 30px 40px 40px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

.input-group {
  margin-bottom: 25px;
}

.label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: 600;
  color: #495057;
  font-size: 15px;
}

.live-indicator {
  font-size: 10px;
  color: #dc3545;
  font-weight: 700;
  animation: pulse 2s infinite;
  margin-left: auto;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.input-field {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  box-sizing: border-box;
  background: white;
}

.input-field.disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.live-time {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
  color: #1976d2 !important;
  font-weight: 600;
  border: 2px solid #2196f3 !important;
}

.duration-field {
  font-weight: 600;
  color: #007bff;
  text-align: center;
}

.cost-breakdown {
  background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
  padding: 25px;
  border-radius: 15px;
  margin-bottom: 30px;
  border: 2px solid #28a745;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.1);
}

.cost-breakdown h6 {
  margin: 0 0 20px 0;
  color: #28a745;
  font-weight: 700;
  font-size: 18px;
  text-align: center;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 15px;
}

.cost-row span:first-child {
  color: #495057;
  font-weight: 500;
}

.cost-row span:last-child {
  color: #28a745;
  font-weight: 600;
}

.total-cost {
  border-top: 2px solid #28a745;
  padding-top: 15px;
  margin-top: 15px;
  font-size: 18px;
  font-weight: 700;
}

.total-cost span {
  color: #28a745;
}

.live-cost {
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.pulse {
  animation: pulse 2s infinite;
}

.real-time-note {
  text-align: center;
  margin-top: 15px;
  font-size: 12px;
  color: #6c757d;
  font-style: italic;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.button-group {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.btn {
  flex: 1;
  padding: 16px 24px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.release-btn {
  background: linear-gradient(45deg, #dc3545, #c82333);
  color: white;
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.release-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #c82333, #a71e2a);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
}

.release-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background: linear-gradient(45deg, #6c757d, #5a6268);
  color: white;
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.cancel-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #5a6268, #495057);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.4);
}

.spinning {
  animation: spin 1s linear infinite;
}

.live-badge {
  background: #ff4444;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  margin-left: 8px;
  animation: pulse 2s infinite;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-content {
    margin: 10px;
    max-width: calc(100vw - 20px);
  }
  
  .modal-header,
  .parking-info,
  .release-form {
    padding-left: 25px;
    padding-right: 25px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .button-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .btn {
    padding: 14px 20px;
    font-size: 15px;
  }
  
  .cost-breakdown {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .modal-title {
    font-size: 22px;
  }
  
  .input-field {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .cost-breakdown {
    padding: 15px;
  }
  
  .cost-row {
    font-size: 14px;
  }
  
  .total-cost {
    font-size: 16px;
  }
}
</style>