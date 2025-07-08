<template>
  <div class="edit-container">
    <div class="header-section">
      <h2>Edit Parking Lot</h2>
      <button @click="goBack" class="back-btn">← Back to Dashboard</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="status-message">
      <div class="spinner"></div>
      Loading parking lot data...
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="status-message error">
      {{ error }}
      <button @click="retryFetch" class="retry-btn">Retry</button>
    </div>

    <!-- Edit Form -->
    <form v-else @submit.prevent="updateLot" class="edit-form">
      <div class="form-group">
        <label for="name">Prime Location Name:</label>
        <input 
          id="name"
          v-model="lot.name" 
          type="text"
          required 
          placeholder="Enter location name"
        />
      </div>

      <div class="form-group">
        <label for="address">Address:</label>
        <textarea 
          id="address"
          v-model="lot.address" 
          required
          rows="3"
          placeholder="Enter full address"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="pincode">Pin Code:</label>
        <input 
          id="pincode"
          v-model="lot.pincode" 
          type="text"
          required 
          pattern="[0-9]{6}"
          placeholder="Enter 6-digit pin code"
        />
      </div>

      <div class="form-group">
        <label for="price">Price (per hour):</label>
        <input 
          id="price"
          v-model.number="lot.price_per_hour" 
          type="number"
          min="0"
          step="0.01"
          required 
          placeholder="Enter price per hour"
        />
      </div>

      <div class="form-group">
        <label for="spots">Maximum Spots:</label>
        <input 
          id="spots"
          v-model.number="lot.max_spots" 
          type="number"
          min="1"
          required 
          placeholder="Enter maximum number of spots"
        />
      </div>

      <div class="form-actions">
        <button type="submit" class="update-btn" :disabled="updating">
          <span v-if="updating">Updating...</span>
          <span v-else>Update Parking Lot</span>
        </button>
        <button type="button" @click="cancelEdit" class="cancel-btn">
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EditParking',
  data() {
    return {
      lot: {
        name: '',
        address: '',
        pincode: '',
        price_per_hour: 0,
        max_spots: 0
      },
      loading: false,
      updating: false,
      error: ''
    }
  },
  async mounted() {
    await this.fetchLotData()
  },
  methods: {
    async fetchLotData() {
      this.loading = true
      this.error = ''
      
      try {
        const lotId = this.$route.params.lotId
        
        if (!lotId) {
          throw new Error('No lot ID provided')
        }

        // Try different possible endpoints
        let response
        try {
          // First try the endpoint that matches your admin routes
          response = await axios.get(`http://localhost:5000/admin/parking-lots`)
          const lots = response.data
          const selectedLot = lots.find(lot => lot.id == lotId)
          
          if (!selectedLot) {
            throw new Error('Parking lot not found')
          }
          
          this.lot = { ...selectedLot }
        } catch (firstError) {
          // Fallback to other possible endpoints
          try {
            response = await axios.get(`http://localhost:5000/admin/parking-lot/${lotId}`)
            this.lot = { ...response.data }
          } catch (secondError) {
            // Another fallback
            try {
              response = await axios.get(`http://localhost:5000/admin/lot/${lotId}`)
              this.lot = { ...response.data }
            } catch (thirdError) {
              throw new Error('Unable to fetch parking lot data. Please check if the lot exists.')
            }
          }
        }

      } catch (error) {
        console.error('Fetch error:', error)
        this.error = error.message || 'Failed to load parking lot data'
      } finally {
        this.loading = false
      }
    },

    async retryFetch() {
      await this.fetchLotData()
    },

    async updateLot() {
      if (!this.validateForm()) {
        return
      }

      this.updating = true
      
      try {
        const lotId = this.$route.params.lotId
        
        // Prepare the update data
        const updateData = {
          name: this.lot.name.trim(),
          address: this.lot.address.trim(),
          pincode: this.lot.pincode.trim(),
          price: this.lot.price_per_hour,
          maxSpots: this.lot.max_spots
        }

        // Try the correct endpoint based on your admin routes
        await axios.put(`http://localhost:5000/admin/edit-parking-lot/${lotId}`, updateData)
        
        // Show success message
        this.$toast?.success?.('Parking lot updated successfully!') || 
        alert('Parking lot updated successfully!')
        
        // Navigate back to admin dashboard
        this.$router.push('/admin')
        
      } catch (error) {
        console.error('Update error:', error)
        const errorMessage = error.response?.data?.error || 
                           error.response?.data?.message || 
                           'Failed to update parking lot'
        
        this.$toast?.error?.(errorMessage) || alert(errorMessage)
      } finally {
        this.updating = false
      }
    },

    validateForm() {
      if (!this.lot.name.trim()) {
        alert('Please enter a location name')
        return false
      }
      
      if (!this.lot.address.trim()) {
        alert('Please enter an address')
        return false
      }
      
      if (!this.lot.pincode.trim() || !/^\d{6}$/.test(this.lot.pincode)) {
        alert('Please enter a valid 6-digit pin code')
        return false
      }
      
      if (this.lot.price_per_hour <= 0) {
        alert('Price per hour must be greater than 0')
        return false
      }
      
      if (this.lot.max_spots <= 0) {
        alert('Maximum spots must be greater than 0')
        return false
      }
      
      return true
    },

    cancelEdit() {
      if (confirm('Are you sure you want to cancel? All changes will be lost.')) {
        this.$router.push('/admin')
      }
    },

    goBack() {
      this.$router.push('/admin')
    }
  }
}
</script>

<style scoped>
.edit-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.header-section h2 {
  color: #333;
  margin: 0;
  font-size: 1.8rem;
}

.back-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.back-btn:hover {
  background-color: #5a6268;
}

.status-message {
  text-align: center;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
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

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.form-group input,
.form-group textarea {
  padding: 0.75rem;
  font-size: 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.update-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.update-btn:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-1px);
}

.update-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  transform: none;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.cancel-btn:hover {
  background-color: #5a6268;
  transform: translateY(-1px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .edit-container {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .header-section {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .update-btn,
  .cancel-btn {
    width: 100%;
  }
}
</style>
