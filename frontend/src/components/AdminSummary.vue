<template>
  <div class="admin-summary">
    <!-- Navigation Bar -->
    <nav class="header">
      <div class="header-left">Welcome Admin</div>
      <div class="header-center">
        <router-link to="/">Home</router-link> |
        <router-link to="/admin/registered-users">Users</router-link> |
        <router-link to="/admin/search">Search</router-link> |
        <router-link to="/admin/summary">Summary</router-link> |
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
      
    </nav>

    <h2 class="title">📊 Parking Lot Statistics</h2>

    <div v-if="revenueChartData && occupancyChartData" class="charts">
      <div class="chart-box">
        <h3>💰 Revenue by Lot</h3>
        <Bar :data="revenueChartData" :options="chartOptions('Revenue in ₹')" />
      </div>
      <div class="chart-box">
        <h3>🚘 Availability & Occupancy</h3>
        <Bar :data="occupancyChartData" :options="chartOptions('Available vs Occupied Spots')" />
      </div>
    </div>
    <p v-else class="loading">⏳ Loading summary data...</p>
  </div>
</template>

<script>
import axios from 'axios'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default {
  name: 'AdminSummary',
  components: { Bar },
  data() {
    return {
      summary: [],
      revenueChartData: null,
      occupancyChartData: null
    }
  },
  methods: {
    async fetchSummary() {
      try {
        const res = await axios.get('http://localhost:5000/admin/api/summary')
        this.summary = res.data
        this.prepareCharts()
      } catch (err) {
        console.error('❌ Error loading summary:', err)
      }
    },
    prepareCharts() {
      const labels = this.summary.map(lot => lot.lot_name)

      this.revenueChartData = {
        labels,
        datasets: [{
          label: 'Revenue (₹)',
          backgroundColor: '#4caf50',
          data: this.summary.map(lot => lot.revenue)
        }]
      }

      this.occupancyChartData = {
        labels,
        datasets: [
          {
            label: 'Available',
            backgroundColor: '#81c784',
            data: this.summary.map(lot => lot.available)
          },
          {
            label: 'Occupied',
            backgroundColor: '#e57373',
            data: this.summary.map(lot => lot.occupied)
          }
        ]
      }
    },
    chartOptions(title) {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          title: { display: true, text: title }
        }
      }
    },
    logout() {
      localStorage.clear()
      this.$router.push('/login')
    }
  },
  mounted() {
    this.fetchSummary()
  }
}
</script>

<style scoped>
.admin-summary {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  background: #f1f1f1;
  padding: 10px;
  border-radius: 8px;
}
.logout-btn {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
}
.title {
  margin-top: 20px;
  text-align: center;
}
.charts {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
  margin-top: 2rem;
}
.chart-box {
  width: 100%;
  max-width: 600px;
  height: 300px;
}
.loading {
  text-align: center;
  margin-top: 2rem;
}
</style>
