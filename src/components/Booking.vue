<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h4 class="modal-title">🅿️ Book Parking Spot</h4>
        <button class="close-btn" @click="$emit('close')" type="button">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- Lot Information -->
      <div class="lot-info">
        <div class="lot-details">
          <h5>{{ lot.name || 'Parking Lot' }}</h5>
          <p class="lot-address">{{ lot.address }}</p>
          <div class="lot-stats">
            <span class="price">₹{{ lot.price_per_hour }}/hr</span>
            <span class="availability">{{ lot.availability }} spots available</span>
          </div>
        </div>
      </div>

      <!-- Existing Bookings Info (Optional Display) -->
      <div v-if="activeBookings.length > 0" class="info-alert">
        <i class="bi bi-info-circle-fill"></i>
        <div class="info-content">
          <strong>Your Active Bookings ({{ activeBookings.length }})</strong>
          <div class="existing-bookings">
            <div v-for="booking in activeBookings.slice(0, 2)" :key="booking.id" class="booking-item">
              <small>
                <strong>{{ booking.location }}</strong> - Spot #{{ booking.spot_id }} ({{ booking.vehicle_no }})
              </small>
            </div>
            <small v-if="activeBookings.length > 2" class="more-bookings">
              +{{ activeBookings.length - 2 }} more bookings...
            </small>
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
       
      <form @submit.prevent="bookSpot" class="booking-form">
        <div class="form-grid">
          <div class="input-group">
            <label class="label">
              <i class="bi bi-hash"></i>
              Lot ID
            </label>
            <input 
              type="text" 
              class="input-field disabled" 
              :value="lot.id" 
              disabled 
            />
          </div>
           
          <div class="input-group">
            <label class="label">
              <i class="bi bi-person-fill"></i>
              User ID
            </label>
            <input 
              type="text" 
              class="input-field disabled" 
              :value="userId" 
              disabled 
            />
          </div>
        </div>
         
        <div class="input-group">
          <label class="label">
            <i class="bi bi-car-front-fill"></i>
            Vehicle Number *
          </label>
          <input 
            type="text" 
            class="input-field" 
            v-model="vehicleNo" 
            placeholder="Enter vehicle number (e.g., MH01AB1234)"
            required 
            :disabled="loading"
            @input="validateVehicleNumber"
            @blur="formatVehicleNumber"
          />
          <small class="input-help">
            {{ activeBookings.length > 0 ? 'You can book multiple parking spots with different vehicles' : 'Enter your vehicle registration number' }}
          </small>
        </div>

        <!-- Multiple Vehicle Warning -->
        <div v-if="isVehicleAlreadyParked" class="warning-alert">
          <i class="bi bi-exclamation-triangle-fill"></i>
          <div class="warning-content">
            <strong>Vehicle Already Parked!</strong>
            <p>This vehicle ({{ vehicleNo }}) is already parked in another location. Each vehicle can only be parked in one spot at a time.</p>
          </div>
        </div>

        <!-- Booking Summary -->
        <div class="booking-summary">
          <h6>Booking Summary</h6>
          <div class="summary-row">
            <span>Location:</span>
            <span>{{ lot.name }}</span>
          </div>
          <div class="summary-row">
            <span>Rate:</span>
            <span>₹{{ lot.price_per_hour }}/hour</span>
          </div>
          <div class="summary-row">
            <span>Vehicle:</span>
            <span>{{ vehicleNo || 'Not entered' }}</span>
          </div>
          <div class="summary-row">
            <span>Your Active Bookings:</span>
            <span>{{ activeBookings.length }} spot(s)</span>
          </div>
          <div class="summary-row total">
            <span>Entry Fee:</span>
            <span>₹0 (Pay on exit)</span>
          </div>
        </div>
         
        <div class="button-group">
          <button 
            type="submit" 
            class="btn reserve-btn" 
            :disabled="loading || !vehicleNo.trim() || isVehicleAlreadyParked || checkingActiveBookings"
          >
            <span v-if="checkingActiveBookings">
              <i class="bi bi-arrow-clockwise spinning"></i>
              Checking...
            </span>
            <span v-else-if="loading">
              <i class="bi bi-arrow-clockwise spinning"></i>
              Booking...
            </span>
            <span v-else-if="isVehicleAlreadyParked">
              <i class="bi bi-x-circle"></i>
              Vehicle Already Parked
            </span>
            <span v-else>
              <i class="bi bi-check-circle"></i>
              {{ activeBookings.length > 0 ? 'Book Another Spot' : 'Confirm Booking' }}
            </span>
          </button>
          <button 
            type="button" 
            class="btn cancel-btn" 
            @click="$emit('close')"
            :disabled="loading || checkingActiveBookings"
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
  name: 'Booking',
  props: {
    lot: {
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
      vehicleNo: '',
      loading: false,
      error: '',
      success: '',
      activeBookings: [],
      checkingActiveBookings: false
    }
  },
  computed: {
    isVehicleAlreadyParked() {
      if (!this.vehicleNo.trim()) return false;
      return this.activeBookings.some(booking => 
        booking.vehicle_no && 
        booking.vehicle_no.toUpperCase() === this.vehicleNo.trim().toUpperCase()
      );
    }
  },
  async mounted() {
    // Check for active bookings when component mounts (for informational purposes)
    await this.checkActiveBookings();
    
    // Focus on vehicle number input
    this.$nextTick(() => {
      const input = this.$el.querySelector('input[type="text"]:not([disabled])');
      if (input) {
        input.focus();
      }
    });
  },
  methods: {
    async checkActiveBookings() {
      this.checkingActiveBookings = true;
      try {
        console.log('Checking active bookings for user:', this.userId);
        
        const response = await axios.get('http://localhost:5000/user/parking-history', {
          headers: {
            'X-User-ID': this.userId,
            'Content-Type': 'application/json'
          },
          timeout: 5000
        });

        // Get all active bookings (status: 'Parked')
        this.activeBookings = response.data.filter(booking => booking.status === 'Parked');
        
        console.log('Active bookings found:', this.activeBookings.length);

      } catch (error) {
        console.error('Error checking active bookings:', error);
        // Don't block booking if we can't check
        this.activeBookings = [];
        console.warn('Could not fetch active bookings, proceeding without check');
      } finally {
        this.checkingActiveBookings = false;
      }
    },

    async bookSpot() {
      // Only prevent booking if the same vehicle is already parked
      if (this.isVehicleAlreadyParked) {
        this.error = 'This vehicle is already parked. Each vehicle can only be parked in one spot at a time.';
        return;
      }

      if (!this.vehicleNo.trim()) {
        this.error = 'Please enter a vehicle number';
        return;
      }

      this.loading = true;
      this.error = '';
      this.success = '';

      try {
        console.log('Booking spot with data:', {
          lotId: this.lot.id,
          userId: this.userId,
          vehicleNo: this.vehicleNo,
          existingBookings: this.activeBookings.length
        });

        const response = await axios.post('http://localhost:5000/user/book-spot', {
          lotId: this.lot.id,
          vehicleNo: this.vehicleNo.trim().toUpperCase()
        }, {
          headers: {
            'X-User-ID': this.userId,
            'Content-Type': 'application/json'
          },
          timeout: 10000
        });

        console.log('Booking response:', response.data);

        this.success = response.data.message || 'Parking spot booked successfully!';
        
        // Emit success with booking details
        this.$emit('success', {
          message: this.success,
          bookingId: response.data.booking_id,
          spotNumber: response.data.spot_number,
          entryTime: response.data.entry_time
        });

        // Close modal after 2 seconds
        setTimeout(() => {
          this.$emit('close');
        }, 2000);

      } catch (error) {
        console.error('Booking error:', error);
        
        if (error.response) {
          // Server responded with error
          const errorMessage = error.response.data?.error || `Error: ${error.response.status}`;
          this.error = errorMessage;
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

    validateVehicleNumber() {
      const value = this.vehicleNo.trim();
      if (value && value.length < 6) {
        this.error = 'Vehicle number seems too short';
      } else if (this.isVehicleAlreadyParked) {
        this.error = 'This vehicle is already parked elsewhere';
      } else {
        this.error = '';
      }
    },

    formatVehicleNumber() {
      // Remove spaces and convert to uppercase
      this.vehicleNo = this.vehicleNo.replace(/\s+/g, '').toUpperCase();
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
  max-width: 600px;
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

.lot-info {
  padding: 20px 40px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
}

.lot-details h5 {
  margin: 0 0 8px 0;
  color: #495057;
  font-weight: 600;
  font-size: 18px;
}

.lot-address {
  margin: 0 0 12px 0;
  color: #6c757d;
  font-size: 14px;
}

.lot-stats {
  display: flex;
  gap: 20px;
}

.price {
  background: #28a745;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.availability {
  background: #007bff;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.info-alert {
  background: linear-gradient(45deg, #17a2b8, #138496);
  color: white;
  padding: 15px 20px;
  margin: 20px 40px;
  border-radius: 12px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);
}

.info-alert i {
  font-size: 20px;
  margin-top: 2px;
}

.info-content {
  flex: 1;
}

.info-content strong {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
}

.existing-bookings {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.booking-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
}

.more-bookings {
  font-style: italic;
  opacity: 0.8;
  margin-top: 4px;
}

.warning-alert {
  background: linear-gradient(45deg, #ffc107, #e0a800);
  color: #212529;
  padding: 20px;
  margin: 20px 40px;
  border-radius: 12px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
  border: 1px solid #ffeaa7;
}

.warning-alert i {
  font-size: 24px;
  margin-top: 2px;
  color: #856404;
}

.warning-content {
  flex: 1;
}

.warning-content strong {
  display: block;
  margin-bottom: 8px;
  font-size: 16px;
  color: #856404;
}

.warning-content p {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
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

.booking-form {
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

.input-field:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 4px rgba(0, 123, 255, 0.1);
  transform: translateY(-2px);
}

.input-field.disabled,
.input-field:disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
  border-color: #dee2e6;
}

.input-field::placeholder {
  color: #adb5bd;
}

.input-help {
  display: block;
  margin-top: 6px;
  color: #6c757d;
  font-size: 13px;
}

.booking-summary {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;
}

.booking-summary h6 {
  margin: 0 0 15px 0;
  color: #495057;
  font-weight: 600;
  font-size: 16px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.summary-row span:first-child {
  color: #6c757d;
}

.summary-row span:last-child {
  color: #495057;
  font-weight: 500;
}

.summary-row.total {
  border-top: 1px solid #dee2e6;
  padding-top: 10px;
  margin-top: 10px;
  font-weight: 600;
}

.summary-row.total span {
  color: #495057;
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

.reserve-btn {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.reserve-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #218838, #1ca085);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
}

.reserve-btn:disabled {
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

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .modal-content {
    margin: 10px;
    max-width: calc(100vw - 20px);
  }
  
  .modal-header,
  .lot-info,
  .booking-form,
  .info-alert,
  .warning-alert,
  .error-alert,
  .success-alert {
    margin-left: 15px;
    margin-right: 15px;
    padding-left: 20px;
    padding-right: 20px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .button-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .btn {
    padding: 14px 20px;
    font-size: 15px;
  }
  
  .lot-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .price,
  .availability {
    display: inline-block;
    width: fit-content;
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
  
  .booking-summary {
    padding: 15px;
  }
}
</style>