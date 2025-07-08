<template>
  <div class="user-summary">
    <!-- Navigation Menu -->
    <nav class="header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🚗</span>
          <span class="logo-text">Welcome {{ username || 'User' }}</span>
        </div>
        <div class="nav-buttons">
          <router-link to="/user/dashboard" class="nav-btn">
            <i class="icon">🏠</i>
            Dashboard
          </router-link>
          <router-link to="/user/summary" class="nav-btn active">
            <i class="icon">📊</i>
            My Summary
          </router-link>
          
          
          <button @click="logout" class="nav-btn logout-btn">
            <i class="icon">🚪</i>
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Debug Information (Remove this after testing) -->
    <div class="debug-info" v-if="showDebug">
      <h4>🔍 Debug Information:</h4>
      <p><strong>Loading:</strong> {{ loading }}</p>
      <p><strong>Error:</strong> {{ error }}</p>
      <p><strong>User ID:</strong> {{ userId }}</p>
      <p><strong>Has Data:</strong> {{ !!userParkingData }}</p>
      <p><strong>Chart Data:</strong> {{ JSON.stringify(chartData, null, 2) }}</p>
      <p><strong>Canvas Ref:</strong> {{ !!$refs.barChart }}</p>
    </div>

    <!-- Main Content -->
    <div class="summary-container">
      <!-- Page Header -->
      <div class="summary-header">
        <h2>📊 My Parking Summary</h2>
        <div class="header-actions">
          
          <button @click="refreshData" class="refresh-btn" :disabled="loading">
            <span v-if="loading">🔄 Refreshing...</span>
            <span v-else>🔄 Refresh</span>
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="error-container">
        <div class="error-message">
          <h3>⚠️ Error Loading Data</h3>
          <p>{{ error }}</p>
          <button @click="refreshData" class="retry-btn">Try Again</button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>📊 Loading your parking data...</p>
      </div>

      <!-- Data Display -->
      <div v-else-if="userParkingData" class="content">
        <!-- Personal Stats Cards -->
        <div class="stats-grid">
          <div class="stat-card total-bookings">
            <div class="stat-icon">📋</div>
            <div class="stat-info">
              <h3>{{ userParkingData.total_bookings || 0 }}</h3>
              <p>Total Bookings</p>
            </div>
          </div>
          
          <div class="stat-card active-bookings">
            <div class="stat-icon">🚗</div>
            <div class="stat-info">
              <h3>{{ userParkingData.active_bookings || 0 }}</h3>
              <p>Active Parking</p>
            </div>
          </div>
          
          <div class="stat-card completed">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <h3>{{ userParkingData.completed_bookings || 0 }}</h3>
              <p>Completed</p>
            </div>
          </div>
          
          <div class="stat-card total-spent">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <h3>₹{{ userParkingData.total_amount_spent || 0 }}</h3>
              <p>Total Spent</p>
            </div>
          </div>
        </div>

        <!-- Bar Chart Section -->
        <div class="chart-section">
          <div class="chart-container">
            <h3>📊 My Parking Activity</h3>
            <div class="chart-debug" v-if="showDebug">
              <p><strong>Chart Data Valid:</strong> {{ !!chartData }}</p>
              <p><strong>Canvas Element:</strong> {{ !!$refs.barChart }}</p>
              <p><strong>Chart Instance:</strong> {{ !!barChart }}</p>
              <button @click="forceRecreateChart" class="debug-btn">Force Recreate Chart</button>
              <button @click="createTestData" class="debug-btn">Load Test Data</button>
            </div>
            <div class="chart-wrapper">
              <canvas 
                ref="barChart" 
                class="chart"
                width="800" 
                height="400"
              ></canvas>
            </div>
          </div>
        </div>

        <!-- Current Status -->
        <div class="current-status-section" v-if="userParkingData.current_parking">
          <h3>🎯 Current Parking Status</h3>
          <div class="current-parking-card">
            <div class="parking-info">
              <p><strong>Vehicle:</strong> {{ userParkingData.current_parking.vehicle_no }}</p>
              <p><strong>Location:</strong> {{ userParkingData.current_parking.location }}</p>
              <p><strong>Spot:</strong> {{ userParkingData.current_parking.spot_id }}</p>
              <p><strong>Entry Time:</strong> {{ formatTimestamp(userParkingData.current_parking.entry_time) }}</p>
              <p><strong>Duration:</strong> {{ calculateDuration(userParkingData.current_parking.entry_time) }}</p>
            </div>
            <div class="parking-actions">
              <button @click="exitParking" class="exit-btn">Exit Parking</button>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="recent-activity-section" v-if="userParkingData.recent_bookings">
          <h3>📋 Recent Activity</h3>
          <div class="activity-list">
            <div 
              v-for="booking in userParkingData.recent_bookings.slice(0, 5)" 
              :key="booking.id" 
              class="activity-item"
            >
              <div class="activity-icon">
                <span v-if="booking.status === 'active'">🅿️</span>
                <span v-else-if="booking.status === 'completed'">✅</span>
                <span v-else>❌</span>
              </div>
              <div class="activity-details">
                <h4>{{ booking.location || 'Unknown Location' }}</h4>
                <p>{{ booking.vehicle_no }} - Spot {{ booking.spot_id }}</p>
                <p class="activity-time">{{ formatTimestamp(booking.entry_time) }}</p>
              </div>
              <div class="activity-amount">
                <span class="amount">₹{{ booking.amount || 0 }}</span>
                <span class="status" :class="booking.status">{{ booking.status }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Info -->
        <div class="info-section">
          <div class="info-card">
            <h4>🕐 Last Updated</h4>
            <p>{{ formatTimestamp(userParkingData.last_updated) }}</p>
          </div>
          
          
          
          <div class="info-card">
            <h4>⭐ Status</h4>
            <p class="status-active">{{ userParkingData.membership_status || 'Active' }}</p>
          </div>
        </div>
      </div>

      <!-- No Data State -->
      <div v-else class="no-data">
        <div class="no-data-content">
          <h3>📊 No Parking Data</h3>
          <p>You haven't made any parking bookings yet.</p>
          <button @click="goToBooking" class="book-now-btn">Book Parking Now</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// filepath: c:\Users\rajve\Downloads\vehical_parking_system-main\vehical_parking_system-main\frontend\src\components\UserSummary.vue
import axios from 'axios'

export default {
  name: 'UserSummary',
  data() {
    return {
      userParkingData: null,
      loading: false,
      error: null,
      username: '',
      barChart: null,
      refreshInterval: null,
      userId: null,
      showDebug: false,
      isCreatingChart: false,
      Chart: null,
      chartCreationAttempts: 0, // Track attempts to prevent infinite loops
      maxChartAttempts: 3
    }
  },
  
  computed: {
    chartData() {
      if (!this.userParkingData) {
        return null
      }
      
      return {
        labels: ['Total Bookings', 'Active', 'Completed'],
        datasets: [{
          label: 'My Parking Statistics',
          data: [
            this.userParkingData.total_bookings || 0,
            this.userParkingData.active_bookings || 0,
            this.userParkingData.completed_bookings || 0
          ],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(34, 197, 94, 0.8)',
            'rgba(16, 185, 129, 0.8)'
          ],
          borderColor: [
            'rgba(59, 130, 246, 1)',
            'rgba(34, 197, 94, 1)',
            'rgba(16, 185, 129, 1)'
          ],
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false
        }]
      }
    }
  },
  
  methods: {
    // Load Chart.js dynamically with error handling
    async loadChartJS() {
      try {
        if (this.Chart) {
          return this.Chart
        }
        
        console.log('Loading Chart.js dynamically...')
        const ChartModule = await import('chart.js/auto')
        this.Chart = ChartModule.default
        console.log('✅ Chart.js loaded successfully:', !!this.Chart)
        return this.Chart
      } catch (error) {
        console.error('❌ Failed to load Chart.js:', error)
        this.error = 'Failed to load Chart.js library'
        return null
      }
    },

    async fetchUserParkingData() {
      this.loading = true
      this.error = null
      
      try {
        const userId = localStorage.getItem('userId') || localStorage.getItem('user_id') || '5'
        console.log('Fetching data for user:', userId)
        
        const response = await axios.get(`http://localhost:5000/user/my-parking-summary`, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
            'X-User-ID': userId
          },
          params: {
            user_id: userId
          },
          timeout: 10000
        })
        
        this.userParkingData = response.data
        console.log('✅ Data loaded successfully:', this.userParkingData)
        
        // Reset chart creation attempts
        this.chartCreationAttempts = 0
        
        // Create chart with proper timing
        this.safeCreateChart()
        
      } catch (error) {
        console.error('❌ Error fetching user parking data:', error)
        
        if (error.code === 'ERR_NETWORK') {
          this.error = 'Server is not running. Please check backend connection.'
        } else if (error.response?.status === 404) {
          console.log('API endpoint not found, creating test data...')
          this.createTestData()
        } else {
          this.error = error.response?.data?.error || error.message || 'Failed to load your parking data'
        }
      } finally {
        this.loading = false
      }
    },

    createTestData() {
      console.log('Creating test data...')
      this.userParkingData = {
        total_bookings: 12,
        active_bookings: 1,
        completed_bookings: 10,
        total_amount_spent: 450,
        current_parking: {
          id: 1,
          vehicle_no: 'MH12AB1234',
          location: 'City Mall Parking',
          spot_id: 'A-15',
          entry_time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        },
        recent_bookings: [
          {
            id: 1,
            location: 'City Mall Parking',
            vehicle_no: 'MH12AB1234',
            spot_id: 'A-15',
            entry_time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            status: 'active',
            amount: 50
          },
          {
            id: 2,
            location: 'Metro Station',
            vehicle_no: 'MH12AB1234',
            spot_id: 'B-08',
            entry_time: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            status: 'completed',
            amount: 30
          }
        ],
        last_updated: new Date().toISOString(),
        member_since: '2024-01-15',
        membership_status: 'Active'
      }
      
      this.error = null
      this.chartCreationAttempts = 0
      console.log('✅ Test data created, creating chart...')
      this.safeCreateChart()
    },

    // Safe chart creation with proper error handling
    async safeCreateChart() {
      // Prevent multiple simultaneous attempts
      if (this.isCreatingChart) {
        console.log('Chart creation already in progress, skipping...')
        return
      }

      // Check attempt limit
      if (this.chartCreationAttempts >= this.maxChartAttempts) {
        console.log('Max chart creation attempts reached, using fallback')
        this.createBasicChart()
        return
      }

      this.isCreatingChart = true
      this.chartCreationAttempts++
      
      try {
        console.log(`=== Chart Creation Attempt ${this.chartCreationAttempts} ===`)
        
        // Wait for DOM to be ready
        await this.$nextTick()
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // Check if we have chart data
        if (!this.chartData) {
          console.error('❌ No chart data available')
          this.error = 'No chart data available'
          return
        }

        // Load Chart.js
        const Chart = await this.loadChartJS()
        if (!Chart) {
          console.error('❌ Chart.js not loaded')
          return
        }

        // Wait for canvas element
        const canvas = await this.waitForCanvas()
        if (!canvas) {
          console.error('❌ Canvas element not found')
          this.createBasicChart() // Fallback to basic chart
          return
        }

        // Destroy existing chart
        this.destroyExistingChart()

        // Get canvas context
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          console.error('❌ Failed to get canvas context')
          return
        }

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        // Create chart with minimal configuration to avoid recursion
        const config = {
          type: 'bar',
          data: this.chartData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Disable animations to prevent issues
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                enabled: true,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: 'white',
                bodyColor: 'white',
                cornerRadius: 8,
                callbacks: {
                  label: function(context) {
                    return `${context.label}: ${context.parsed.y} bookings`
                  }
                }
              }
            },
            scales: {
              x: {
                grid: {
                  display: false
                },
                ticks: {
                  color: '#666',
                  font: {
                    size: 12
                  }
                }
              },
              y: {
                beginAtZero: true,
                grid: {
                  color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                  stepSize: 1,
                  color: '#666',
                  font: {
                    size: 12
                  }
                }
              }
            }
          }
        }

        console.log('Creating chart with config...')
        
        // Create the chart
        this.barChart = new Chart(ctx, config)
        
        if (this.barChart) {
          console.log('✅ Chart created successfully')
          this.error = null // Clear any previous errors
        } else {
          throw new Error('Chart instance not created')
        }
        
      } catch (chartError) {
        console.error('❌ Error creating chart:', chartError)
        
        // If we haven't reached max attempts, try fallback
        if (this.chartCreationAttempts < this.maxChartAttempts) {
          console.log('Trying basic chart fallback...')
          this.createBasicChart()
        } else {
          this.error = `Chart creation failed after ${this.maxChartAttempts} attempts`
        }
      } finally {
        this.isCreatingChart = false
        console.log('=== Chart Creation Complete ===')
      }
    },

    // Wait for canvas element with timeout
    waitForCanvas(maxWait = 3000) {
      return new Promise((resolve) => {
        const startTime = Date.now()
        let attempts = 0
        const maxAttempts = 30
        
        const checkCanvas = () => {
          attempts++
          const canvas = this.$refs.barChart
          const elapsed = Date.now() - startTime
          
          console.log(`Canvas check attempt ${attempts}: ${!!canvas}`)
          
          if (canvas && canvas.getContext) {
            console.log(`✅ Canvas found after ${elapsed}ms (${attempts} attempts)`)
            resolve(canvas)
          } else if (elapsed >= maxWait || attempts >= maxAttempts) {
            console.log(`❌ Canvas not found after ${elapsed}ms (${attempts} attempts)`)
            resolve(null)
          } else {
            setTimeout(checkCanvas, 100)
          }
        }
        
        checkCanvas()
      })
    },

    // Safely destroy existing chart
    destroyExistingChart() {
      if (this.barChart) {
        try {
          console.log('🗑️ Destroying existing chart...')
          this.barChart.destroy()
          this.barChart = null
          console.log('✅ Chart destroyed successfully')
        } catch (error) {
          console.warn('⚠️ Warning destroying chart:', error)
          this.barChart = null
        }
      }
    },

    // Create basic chart using HTML5 Canvas (fallback)
    createBasicChart() {
      console.log('Creating basic chart fallback...')
      
      const canvas = this.$refs.barChart
      if (!canvas) {
        console.error('❌ Canvas not found for basic chart')
        return
      }
      
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        console.error('❌ Canvas context not found')
        return
      }
      
      try {
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        
        // Get data
        const data = this.chartData.datasets[0].data
        const labels = this.chartData.labels
        const colors = this.chartData.datasets[0].backgroundColor
        
        // Chart dimensions
        const padding = 60
        const chartWidth = canvas.width - (padding * 2)
        const chartHeight = canvas.height - (padding * 2)
        const barWidth = Math.floor(chartWidth / data.length) - 20
        const maxValue = Math.max(...data) || 1
        
        // Draw bars
        data.forEach((value, index) => {
          const barHeight = (value / maxValue) * chartHeight * 0.8
          const x = padding + (index * (barWidth + 20)) + 10
          const y = canvas.height - padding - barHeight
          
          // Draw bar
          ctx.fillStyle = colors[index]
          ctx.fillRect(x, y, barWidth, barHeight)
          
          // Draw value on top of bar
          ctx.fillStyle = '#333'
          ctx.font = 'bold 14px Arial'
          ctx.textAlign = 'center'
          ctx.fillText(value.toString(), x + barWidth/2, y - 10)
          
          // Draw label at bottom
          ctx.font = '12px Arial'
          ctx.fillStyle = '#666'
          
          // Split long labels
          const words = labels[index].split(' ')
          const lineHeight = 15
          words.forEach((word, wordIndex) => {
            ctx.fillText(word, x + barWidth/2, canvas.height - padding + 15 + (wordIndex * lineHeight))
          })
        })
        
        // Draw title
        ctx.fillStyle = '#333'
        ctx.font = 'bold 16px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('My Parking Statistics', canvas.width/2, 30)
        
        console.log('✅ Basic chart created successfully')
        this.error = null // Clear error since fallback worked
        
      } catch (error) {
        console.error('❌ Error creating basic chart:', error)
        this.error = 'Failed to create chart visualization'
      }
    },

    async refreshData() {
      console.log('Refreshing data...')
      this.chartCreationAttempts = 0 // Reset attempts on manual refresh
      await this.fetchUserParkingData()
    },

    // Force recreate chart (for debugging)
    async forceRecreateChart() {
      console.log('🔄 Force recreating chart...')
      
      // Reset state
      this.isCreatingChart = false
      this.chartCreationAttempts = 0
      this.error = null
      
      // Destroy existing chart
      this.destroyExistingChart()
      
      // Wait a moment and recreate
      setTimeout(() => {
        this.safeCreateChart()
      }, 500)
    },

    calculateDuration(entryTime) {
      if (!entryTime) return 'Unknown'
      
      try {
        const entry = new Date(entryTime)
        const now = new Date()
        const diffMs = now - entry
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
        
        if (diffHours > 0) {
          return `${diffHours}h ${diffMinutes}m`
        } else {
          return `${diffMinutes}m`
        }
      } catch (error) {
        return 'Unknown'
      }
    },

    formatTimestamp(timestamp) {
      if (!timestamp) return 'Unknown'
      
      try {
        const date = new Date(timestamp)
        return date.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return 'Invalid date'
      }
    },

    formatMemberSince(dateString) {
      if (!dateString) return 'Unknown'
      
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long'
        })
      } catch (error) {
        return 'Unknown'
      }
    },

    async exitParking() {
      if (!this.userParkingData?.current_parking) return
      
      try {
        const response = await axios.post(`http://localhost:5000/user/exit-parking`, {
          user_id: this.userId,
          booking_id: this.userParkingData.current_parking.id
        }, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response.status === 200) {
          alert('Successfully exited parking!')
          this.refreshData()
        }
      } catch (error) {
        console.error('Exit parking error:', error)
        alert('Failed to exit parking. Please try again.')
      }
    },

    goToBooking() {
      this.$router.push('/user/book-parking')
    },

    logout() {
      // Cleanup
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
      }
      
      this.destroyExistingChart()
      
      // Clear storage
      localStorage.removeItem('userId')
      localStorage.removeItem('user_id')
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      
      this.$router.push('/login')
    }
  },

  async mounted() {
    console.log('🚀 UserSummary component mounted')
    
    // Set user info
    this.username = localStorage.getItem('username') || localStorage.getItem('fullname') || 'User'
    this.userId = localStorage.getItem('userId') || localStorage.getItem('user_id')
    
    console.log('👤 User info:', { username: this.username, userId: this.userId })
    
    // Initial data fetch
    await this.fetchUserParkingData()
  },

  beforeUnmount() {
    console.log('🧹 UserSummary component unmounting...')
    
    // Clear intervals
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
    
    // Destroy chart
    this.destroyExistingChart()
    
    // Reset flags
    this.isCreatingChart = false
    this.chartCreationAttempts = 0
  }
}
</script>

<style scoped>
.user-summary {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Navigation Header */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem 0;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
}

.logo-icon {
  font-size: 1.8rem;
}

.logo-text {
  font-size: 1.3rem;
  font-weight: 600;
}

.nav-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: rgba(255,255,255,0.1);
  color: white;
  text-decoration: none;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.nav-btn:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.nav-btn.active {
  background: rgba(255,255,255,0.25);
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.logout-btn {
  background: rgba(220, 53, 69, 0.8);
  border: 1px solid rgba(255,255,255,0.3);
}

.logout-btn:hover {
  background: rgba(220, 53, 69, 1);
}

.icon {
  font-size: 1rem;
}

/* Main Content */
.summary-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.summary-header h2 {
  color: #333;
  font-size: 1.8rem;
  margin: 0;
  font-weight: 600;
}

.refresh-btn {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(45deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.refresh-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Error & Loading States */
.error-container {
  text-align: center;
  padding: 3rem;
}

.error-message {
  background: linear-gradient(45deg, #f8d7da, #f5c6cb);
  color: #721c24;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #f5c6cb;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.loading-container {
  text-align: center;
  padding: 4rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}

.stat-icon {
  font-size: 2.5rem;
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
}

.stat-card.occupied .stat-icon {
  background: linear-gradient(135deg, #ffebee, #ffcdd2);
}

.stat-card.available .stat-icon {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
}

.stat-card.occupancy .stat-icon {
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
}

.stat-info h3 {
  font-size: 2.2rem;
  margin: 0;
  color: #333;
  font-weight: 700;
}

.stat-info p {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
  font-weight: 500;
}

/* Chart Section */
.chart-section {
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  border: 1px solid rgba(0,0,0,0.05);
}

.chart-container h3 {
  text-align: center;
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 600;
  font-size: 1.3rem;
}

.chart-wrapper {
  height: 350px;
  position: relative;
  width: 100%;
}

.chart {
  max-width: 100% !important;
  max-height: 100% !important;
}

/* Occupancy Section */
.occupancy-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  border: 1px solid rgba(0,0,0,0.05);
}

.occupancy-section h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
}

.occupancy-bar {
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  margin-bottom: 1rem;
}

.occupancy-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.8s ease;
  position: relative;
}

.occupancy-fill.low {
  background: linear-gradient(90deg, #28a745, #20c997);
}

.occupancy-fill.medium {
  background: linear-gradient(90deg, #ffc107, #fd7e14);
}

.occupancy-fill.high {
  background: linear-gradient(90deg, #dc3545, #e74c3c);
}

.occupancy-details {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-weight: 500;
}

/* Info Section */
.info-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  text-align: center;
  border: 1px solid rgba(0,0,0,0.05);
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: translateY(-3px);
}

.info-card h4 {
  color: #333;
  margin-bottom: 0.8rem;
  font-weight: 600;
}

.info-card p {
  color: #666;
  margin: 0;
  font-weight: 500;
}

.status-online {
  color: #28a745 !important;
  font-weight: 600 !important;
}

/* No Data State */
.no-data {
  text-align: center;
  padding: 4rem;
}

.no-data-content {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.retry-btn {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: linear-gradient(45deg, #218838, #17a2b8);
  transform: translateY(-2px);
}

/* Additional styles for new components */
.current-status-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  border: 1px solid rgba(0,0,0,0.05);
}

.current-status-section h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
}

.current-parking-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #e8f5e8, #d4edda);
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #28a745;
}

.parking-info p {
  margin: 0.5rem 0;
  color: #333;
  font-weight: 500;
}

.exit-btn {
  background: linear-gradient(45deg, #dc3545, #c82333);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.exit-btn:hover {
  background: linear-gradient(45deg, #c82333, #bd2130);
  transform: translateY(-2px);
}

.recent-activity-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  border: 1px solid rgba(0,0,0,0.05);
}

.recent-activity-section h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.activity-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.activity-details {
  flex: 1;
}

.activity-details h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
}

.activity-details p {
  margin: 0.25rem 0;
  color: #666;
  font-size: 0.9rem;
}

.activity-time {
  color: #999 !important;
  font-size: 0.8rem !important;
}

.activity-amount {
  text-align: right;
}

.amount {
  display: block;
  font-weight: 700;
  color: #333;
  font-size: 1.1rem;
}

.status {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-top: 0.25rem;
}

.status.active {
  background: #d1ecf1;
  color: #0c5460;
}

.status.completed {
  background: #d4edda;
  color: #155724;
}

.status.cancelled {
  background: #f8d7da;
  color: #721c24;
}

.book-now-btn {
  padding: 1rem 2rem;
  background: linear-gradient(45deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
}

.book-now-btn:hover {
  background: linear-gradient(45deg, #0056b3, #004085);
  transform: translateY(-2px);
}

.status-active {
  color: #28a745 !important;
  font-weight: 600 !important;
}

/* Debug styles */
.debug-info {
  background: #f0f0f0;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  border: 2px solid #ccc;
  font-family: monospace;
  font-size: 12px;
}

.debug-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.chart-debug {
  background: #e9ecef;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  font-size: 12px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    padding: 0 1rem;
  }

  .nav-buttons {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.3rem;
  }

  .nav-btn {
    padding: 0.5rem 0.8rem;
    font-size: 0.8rem;
  }

  .summary-container {
    padding: 1rem;
  }

  .summary-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .summary-header h2 {
    font-size: 1.5rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-wrapper {
    height: 300px;
  }

  .occupancy-details {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .stat-card {
    flex-direction: column;
    text-align: center;
    gap: 0.8rem;
  }

  .stat-icon {
    font-size: 2rem;
    width: 60px;
    height: 60px;
  }

  .stat-info h3 {
    font-size: 1.8rem;
  }

  .chart-wrapper {
    height: 250px;
  }
}
</style>