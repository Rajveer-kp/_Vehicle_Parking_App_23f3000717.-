<template>
  <div class="profile-overlay" @click="closeIfClickedOutside">
    <div class="profile-modal" @click.stop>
      <!-- Header -->
      <div class="profile-header">
        <h2>
          <i class="bi bi-person-circle"></i>
          User Profile
        </h2>
        <button @click="$emit('close')" class="close-btn">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- Error/Success Messages -->
      <div v-if="error" class="alert error-alert">
        <i class="bi bi-exclamation-triangle-fill"></i>
        {{ error }}
        <button @click="error = ''" class="alert-close">×</button>
      </div>

      <div v-if="successMessage" class="alert success-alert">
        <i class="bi bi-check-circle-fill"></i>
        {{ successMessage }}
        <button @click="successMessage = ''" class="alert-close">×</button>
      </div>

      <!-- Profile Content -->
      <div class="profile-content">
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading profile...</p>
        </div>

        <!-- Profile Form -->
        <div v-else class="profile-form">
          <!-- Basic Info Section -->
          <div class="form-section">
            <h3>
              <i class="bi bi-person"></i>
              Basic Information
            </h3>
            
            <div class="form-group">
              <label for="fullname">Full Name</label>
              <input
                id="fullname"
                v-model="profile.fullname"
                type="text"
                class="form-input"
                placeholder="Enter your full name"
                :disabled="!editMode"
              />
            </div>

            <div class="form-group">
              <label for="username">Username</label>
              <input
                id="username"
                v-model="profile.username"
                type="text"
                class="form-input"
                placeholder="Enter username"
                :disabled="!editMode"
              />
            </div>

            <div class="form-group">
              <label for="email">Email</label>
              <input
                id="email"
                v-model="profile.email"
                type="email"
                class="form-input"
                placeholder="Enter email address"
                :disabled="!editMode"
              />
            </div>

            <div class="form-group">
              <label for="phone">Phone Number</label>
              <input
                id="phone"
                v-model="profile.phone"
                type="tel"
                class="form-input"
                placeholder="Enter phone number"
                :disabled="!editMode"
              />
            </div>
          </div>

          <!-- Profile Actions -->
          <div class="profile-actions">
            <button
              v-if="!editMode"
              @click="enableEditMode"
              class="btn edit-btn"
            >
              <i class="bi bi-pencil"></i>
              Edit Profile
            </button>

            <div v-else class="edit-actions">
              <button
                @click="saveProfile"
                class="btn save-btn"
                :disabled="saving"
              >
                <i class="bi bi-check-lg"></i>
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
              <button
                @click="cancelEdit"
                class="btn cancel-btn"
                :disabled="saving"
              >
                <i class="bi bi-x-lg"></i>
                Cancel
              </button>
            </div>
          </div>

          <!-- Data Export Section -->
          <div class="form-section">
            <h3>
              <i class="bi bi-download"></i>
              Export Parking History
            </h3>
            
            <div class="export-info">
              <p>Download your complete parking history as a CSV file. This includes:</p>
              <ul>
                <li>Parking slot and spot details</li>
                <li>Entry and exit timestamps</li>
                <li>Duration and costs</li>
                <li>Location information</li>
                <li>Booking status and remarks</li>
              </ul>
            </div>

            <div v-if="exportStatus" class="export-status" :class="exportStatus.type">
              <i :class="getExportStatusIcon()"></i>
              {{ exportStatus.message }}
            </div>

            <button
              @click="requestCsvExport"
              class="btn export-btn"
              :disabled="exportLoading"
            >
              <i class="bi bi-file-earmark-spreadsheet"></i>
              {{ exportLoading ? 'Processing...' : 'Export to CSV' }}
            </button>
          </div>


        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserProfile',
  emits: ['close'],
  data() {
    return {
      profile: {
        fullname: '',
        username: '',
        email: '',
        phone: ''
      },
      originalProfile: {},
      editMode: false,
      loading: true,
      saving: false,
      exportLoading: false,
      exportStatus: null,
      error: '',
      successMessage: ''
    }
  },

  methods: {
    async fetchProfile() {
      this.loading = true
      this.error = ''
      
      try {
        const userId = localStorage.getItem('userId')
        const response = await axios.get('http://localhost:5000/user/profile', {
          headers: {
            'X-User-ID': userId,
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          }
        })
        
        this.profile = { ...response.data }
        this.originalProfile = { ...response.data }
        
      } catch (error) {
        console.error('Error fetching profile:', error)
        this.handleError(error, 'Failed to load profile')
      } finally {
        this.loading = false
      }
    },

    enableEditMode() {
      this.editMode = true
      this.originalProfile = { ...this.profile }
    },

    cancelEdit() {
      this.profile = { ...this.originalProfile }
      this.editMode = false
    },

    async saveProfile() {
      this.saving = true
      this.error = ''
      
      try {
        const userId = localStorage.getItem('userId')
        const profileData = {
          fullname: this.profile.fullname,
          username: this.profile.username,
          email: this.profile.email,
          phone: this.profile.phone
        }

        await axios.put('http://localhost:5000/user/profile', profileData, {
          headers: {
            'X-User-ID': userId,
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          }
        })
        
        // Update localStorage if username changed
        if (profileData.username !== this.originalProfile.username) {
          localStorage.setItem('username', profileData.username)
        }
        if (profileData.fullname !== this.originalProfile.fullname) {
          localStorage.setItem('fullname', profileData.fullname)
        }
        
        this.successMessage = 'Profile updated successfully!'
        this.editMode = false
        this.originalProfile = { ...this.profile }
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.successMessage = ''
        }, 3000)
        
      } catch (error) {
        console.error('Error updating profile:', error)
        this.handleError(error, 'Failed to update profile')
      } finally {
        this.saving = false
      }
    },

    async requestCsvExport() {
      this.exportLoading = true
      this.exportStatus = null
      this.error = ''
      
      try {
        const userId = localStorage.getItem('userId')
        const response = await axios.post('http://localhost:5000/user/export-csv', {}, {
          headers: {
            'X-User-ID': userId,
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          },
          responseType: 'blob' // Important for file downloads
        })
        
        // Create download link for the CSV file
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Get filename from response headers or create default
        const contentDisposition = response.headers['content-disposition']
        let filename = `parking-history-${new Date().toISOString().split('T')[0]}.csv`
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }
        
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        this.exportStatus = {
          type: 'success',
          message: 'CSV export completed successfully! Check your downloads folder.'
        }
        
      } catch (error) {
        console.error('Error requesting CSV export:', error)
        
        let errorMessage = 'Failed to export CSV. Please try again.'
        
        // Better error handling for different response types
        if (error.response) {
          if (error.response.data instanceof Blob) {
            // If response is a blob, try to read it as text to get error message
            try {
              const text = await error.response.data.text()
              const errorData = JSON.parse(text)
              errorMessage = errorData.error || errorData.message || errorMessage
            } catch (parseError) {
              console.error('Could not parse error blob:', parseError)
            }
          } else if (error.response.data && typeof error.response.data === 'object') {
            errorMessage = error.response.data.error || error.response.data.message || errorMessage
          } else if (typeof error.response.data === 'string') {
            errorMessage = error.response.data
          }
        } else if (error.message) {
          errorMessage = error.message
        }
        
        this.exportStatus = {
          type: 'error', 
          message: errorMessage
        }
        this.error = errorMessage
      } finally {
        this.exportLoading = false
      }
    },

    getExportStatusIcon() {
      if (!this.exportStatus) return ''
      return this.exportStatus.type === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-exclamation-triangle-fill'
    },

    handleError(error, defaultMessage) {
      let errorMessage = defaultMessage
      
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.message) {
        errorMessage = error.message
      }
      
      this.error = errorMessage
      
      // Auto-clear error after 5 seconds
      setTimeout(() => {
        this.error = ''
      }, 5000)
    },

    closeIfClickedOutside(event) {
      if (event.target === event.currentTarget) {
        this.$emit('close')
      }
    }
  },

  async mounted() {
    await this.fetchProfile()
  }
}
</script>

<style scoped>
/* Profile Overlay */
.profile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.profile-modal {
  background: white;
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  position: relative;
}

/* Header */
.profile-header {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 25px 30px;
  border-radius: 20px 20px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
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

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* Alerts */
.alert {
  margin: 20px 30px;
  padding: 15px 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.error-alert {
  background: linear-gradient(45deg, #dc3545, #c82333);
  color: white;
}

.success-alert {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
}

.alert-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 18px;
  cursor: pointer;
  margin-left: auto;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Content */
.profile-content {
  padding: 30px;
}

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

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Form Sections */
.form-section {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 1px solid #e9ecef;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.form-section h3 {
  color: #495057;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
}

.form-section h3 i {
  color: #007bff;
  font-size: 20px;
}

/* Form Groups */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #495057;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-input:disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

/* Buttons */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  text-decoration: none;
}

.edit-btn {
  background: linear-gradient(45deg, #17a2b8, #138496);
  color: white;
}

.edit-btn:hover {
  background: linear-gradient(45deg, #138496, #117a8b);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);
}

.save-btn {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #20c997, #1e7e34);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.cancel-btn {
  background: linear-gradient(45deg, #6c757d, #5a6268);
  color: white;
  margin-left: 10px;
}

.cancel-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #5a6268, #495057);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
}

.export-btn {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
}

.export-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #20c997, #17a2b8);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

/* Export Section Styles */
.export-info {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.export-info p {
  margin: 0 0 15px 0;
  color: #495057;
  font-weight: 500;
}

.export-info ul {
  margin: 0;
  padding-left: 20px;
  color: #6c757d;
}

.export-info li {
  margin-bottom: 8px;
}

.export-status {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.export-status.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.export-status.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.export-status i {
  font-size: 16px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Profile Actions */
.profile-actions {
  margin-bottom: 30px;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-overlay {
    padding: 10px;
  }
  
  .profile-modal {
    max-height: 95vh;
  }
  
  .profile-header {
    padding: 20px;
  }
  
  .profile-header h2 {
    font-size: 20px;
  }
  
  .profile-content {
    padding: 20px;
  }
  
  .edit-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .profile-header {
    padding: 15px;
  }
  
  .profile-content {
    padding: 15px;
  }
  
  .form-input {
    font-size: 14px;
  }
  
  .btn {
    padding: 10px 16px;
    font-size: 13px;
  }
}
</style>
