// charts.js - Enhanced Chart Components for Admin & User Dashboards
import { defineComponent, h, ref, onMounted, onUnmounted } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  PieElement,
  RadialLinearScale,
  Filler
} from 'chart.js'
import { Doughnut, Bar, Line, Pie, PolarArea } from 'vue-chartjs'

// Register necessary Chart.js components globally
ChartJS.register(
  Title, 
  Tooltip, 
  Legend, 
  ArcElement, 
  CategoryScale, 
  LinearScale, 
  BarElement,
  LineElement,
  PointElement,
  PieElement,
  RadialLinearScale,
  Filler
)

// ✅ Admin Section - Doughnut Chart Component
export const AdminDoughnutChart = defineComponent({
  name: 'AdminDoughnutChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              font: {
                size: 12,
                weight: '600'
              },
              color: '#374151'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              label: function(context) {
                if (!context.dataset.data || context.dataset.data.length === 0) {
                  return `${context.label}: 0 (0%)`
                }
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                if (total === 0) {
                  return `${context.label}: 0 (0%)`
                }
                const percentage = ((context.parsed / total) * 100).toFixed(1)
                return `${context.label}: ${context.parsed} (${percentage}%)`
              }
            }
          }
        },
        cutout: '65%',
        animation: {
          animateRotate: true,
          duration: 1500
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    onMounted(() => {
      // Ensure chart is properly initialized
      if (chartRef.value) {
        console.log('AdminDoughnutChart mounted successfully')
      }
    })
    
    onUnmounted(() => {
      // Cleanup if needed
      if (chartRef.value) {
        chartRef.value.destroy?.()
      }
    })
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(Doughnut, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ Admin Section - Advanced Bar Chart Component
export const AdminBarChart = defineComponent({
  name: 'AdminBarChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return `${context.label}: ${context.parsed.y} spots`
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
                size: 12,
                weight: '500'
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
        },
        animation: {
          duration: 1200,
          easing: 'easeInOutQuart'
        },
        elements: {
          bar: {
            borderRadius: 8,
            borderSkipped: false
          }
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(Bar, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ User Section - Personal Bar Chart Component (For UserSummary)
export const UserPersonalBarChart = defineComponent({
  name: 'UserPersonalBarChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(45, 55, 72, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            cornerRadius: 8,
            displayColors: false,
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
              color: '#4A5568',
              font: {
                size: 12,
                weight: '500'
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(160, 174, 192, 0.2)'
            },
            ticks: {
              stepSize: 1,
              color: '#4A5568',
              font: {
                size: 11
              }
            }
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeInOutQuart'
        },
        elements: {
          bar: {
            borderRadius: 8,
            borderSkipped: false
          }
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(Bar, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ User Section - Simple Doughnut Chart Component
export const UserDoughnutChart = defineComponent({
  name: 'UserDoughnutChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              padding: 15,
              usePointStyle: true,
              font: {
                size: 11,
                weight: '500'
              },
              color: '#374151',
              generateLabels: function(chart) {
                const data = chart.data
                if (data.labels.length && data.datasets.length) {
                  return data.labels.map((label, i) => {
                    const dataset = data.datasets[0]
                    const backgroundColor = dataset.backgroundColor[i]
                    const value = dataset.data[i]
                    const total = dataset.data.reduce((a, b) => a + b, 0)
                    const percentage = total > 0 ? ((value / total) * 100).toFixed(0) : 0
                    
                    return {
                      text: `${label}: ${percentage}%`,
                      fillStyle: backgroundColor,
                      index: i
                    }
                  })
                }
                return []
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(45, 55, 72, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            cornerRadius: 6,
            displayColors: false,
            callbacks: {
              label: function(context) {
                if (!context.dataset.data || context.dataset.data.length === 0) {
                  return '0 spots (0%)'
                }
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                if (total === 0) {
                  return '0 spots (0%)'
                }
                const percentage = ((context.parsed / total) * 100).toFixed(1)
                return `${context.parsed} spots (${percentage}%)`
              }
            }
          }
        },
        cutout: '70%',
        animation: {
          animateRotate: true,
          duration: 1000
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(Doughnut, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ User Section - Simple Bar Chart Component
export const UserBarChart = defineComponent({
  name: 'UserBarChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(45, 55, 72, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            cornerRadius: 6,
            displayColors: false,
            callbacks: {
              title: function(context) {
                return context[0].label
              },
              label: function(context) {
                return `${context.parsed.y} spots available`
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
              color: '#4A5568',
              font: {
                size: 11,
                weight: '500'
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(160, 174, 192, 0.2)'
            },
            ticks: {
              stepSize: 5,
              color: '#4A5568',
              font: {
                size: 10
              }
            }
          }
        },
        animation: {
          duration: 800,
          easing: 'easeOutCubic'
        },
        elements: {
          bar: {
            borderRadius: 6,
            borderSkipped: false
          }
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(Bar, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ User Section - Line Chart for Trends
export const UserLineChart = defineComponent({
  name: 'UserLineChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                size: 11,
                weight: '500'
              },
              color: '#374151'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(45, 55, 72, 0.9)',
            titleColor: 'white',
            bodyColor: 'white',
            cornerRadius: 6,
            displayColors: true,
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(160, 174, 192, 0.1)'
            },
            ticks: {
              color: '#4A5568',
              font: {
                size: 10
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(160, 174, 192, 0.2)'
            },
            ticks: {
              color: '#4A5568',
              font: {
                size: 10
              }
            }
          }
        },
        elements: {
          line: {
            tension: 0.4,
            borderWidth: 3
          },
          point: {
            radius: 4,
            hoverRadius: 6,
            borderWidth: 2
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeInOutCubic'
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(Line, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ Admin Section - Pie Chart Component
export const AdminPieChart = defineComponent({
  name: 'AdminPieChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              font: {
                size: 12,
                weight: '600'
              },
              color: '#374151'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                if (!context.dataset.data || context.dataset.data.length === 0) {
                  return `${context.label}: 0 (0%)`
                }
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                if (total === 0) {
                  return `${context.label}: 0 (0%)`
                }
                const percentage = ((context.parsed / total) * 100).toFixed(1)
                return `${context.label}: ${context.parsed} (${percentage}%)`
              }
            }
          }
        },
        animation: {
          animateRotate: true,
          duration: 1500
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(Pie, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ Admin Section - Polar Area Chart Component
export const AdminPolarChart = defineComponent({
  name: 'AdminPolarChart',
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (data) => {
        return data && data.labels && data.datasets && data.datasets.length > 0
      }
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 15,
              usePointStyle: true,
              font: {
                size: 11,
                weight: '500'
              },
              color: '#374151'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            cornerRadius: 8
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            grid: {
              color: 'rgba(160, 174, 192, 0.2)'
            },
            angleLines: {
              color: 'rgba(160, 174, 192, 0.2)'
            },
            ticks: {
              color: '#4A5568',
              font: {
                size: 10
              }
            }
          }
        },
        animation: {
          duration: 1200,
          easing: 'easeInOutQuart'
        }
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    
    return () => {
      if (!props.chartData || !props.chartData.labels || !props.chartData.datasets) {
        return h('div', { class: 'chart-error' }, 'No data available for chart')
      }
      
      return h(PolarArea, {
        ref: chartRef,
        data: props.chartData,
        options: props.chartOptions
      })
    }
  }
})

// ✅ Utility Functions for Chart Data Generation

// Generate chart colors
export const generateChartColors = (count) => {
  const colors = [
    'rgba(59, 130, 246, 0.8)',   // Blue
    'rgba(34, 197, 94, 0.8)',    // Green
    'rgba(239, 68, 68, 0.8)',    // Red
    'rgba(245, 158, 11, 0.8)',   // Yellow
    'rgba(139, 92, 246, 0.8)',   // Purple
    'rgba(236, 72, 153, 0.8)',   // Pink
    'rgba(6, 182, 212, 0.8)',    // Cyan
    'rgba(34, 197, 94, 0.8)',    // Emerald
    'rgba(251, 146, 60, 0.8)',   // Orange
    'rgba(156, 163, 175, 0.8)'   // Gray
  ]
  
  return Array.from({length: count}, (_, i) => colors[i % colors.length])
}

// Generate border colors
export const generateBorderColors = (count) => {
  const borderColors = [
    'rgba(59, 130, 246, 1)',
    'rgba(34, 197, 94, 1)',
    'rgba(239, 68, 68, 1)',
    'rgba(245, 158, 11, 1)',
    'rgba(139, 92, 246, 1)',
    'rgba(236, 72, 153, 1)',
    'rgba(6, 182, 212, 1)',
    'rgba(34, 197, 94, 1)',
    'rgba(251, 146, 60, 1)',
    'rgba(156, 163, 175, 1)'
  ]
  
  return Array.from({length: count}, (_, i) => borderColors[i % borderColors.length])
}

// ✅ Chart Data Helpers for Parking System

// Admin parking overview data
export const createAdminParkingData = (summaryData) => {
  if (!summaryData) {
    return {
      labels: ['Available Spots', 'Occupied Spots', 'Reserved Spots'],
      datasets: [{
        label: 'Parking Distribution',
        data: [0, 0, 0],
        backgroundColor: [
          'rgba(40, 167, 69, 0.8)',
          'rgba(220, 53, 69, 0.8)',
          'rgba(255, 193, 7, 0.8)'
        ],
        borderColor: [
          'rgba(40, 167, 69, 1)',
          'rgba(220, 53, 69, 1)',
          'rgba(255, 193, 7, 1)'
        ],
        borderWidth: 2
      }]
    }
  }
  
  return {
    labels: ['Available Spots', 'Occupied Spots', 'Reserved Spots'],
    datasets: [{
      label: 'Parking Distribution',
      data: [
        summaryData.free_spots || 0,
        summaryData.used_spots || 0,
        summaryData.reserved_spots || 0
      ],
      backgroundColor: [
        'rgba(40, 167, 69, 0.8)',   // Green for available
        'rgba(220, 53, 69, 0.8)',   // Red for occupied
        'rgba(255, 193, 7, 0.8)'    // Yellow for reserved
      ],
      borderColor: [
        'rgba(40, 167, 69, 1)',
        'rgba(220, 53, 69, 1)',
        'rgba(255, 193, 7, 1)'
      ],
      borderWidth: 2
    }]
  }
}

// User parking status data (simplified)
export const createUserParkingData = (summaryData) => {
  if (!summaryData) {
    return {
      labels: ['Available', 'Occupied'],
      datasets: [{
        label: 'Parking Status',
        data: [0, 0],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 2
      }]
    }
  }
  
  return {
    labels: ['Available', 'Occupied'],
    datasets: [{
      label: 'Parking Status',
      data: [
        summaryData.free_spots || 0,
        summaryData.used_spots || 0
      ],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',   // Green for available
        'rgba(239, 68, 68, 0.8)'    // Red for occupied
      ],
      borderColor: [
        'rgba(34, 197, 94, 1)',
        'rgba(239, 68, 68, 1)'
      ],
      borderWidth: 2
    }]
  }
}

// User personal parking data for UserSummary
export const createUserPersonalData = (userData) => {
  if (!userData) {
    return {
      labels: ['Total Bookings', 'Active', 'Completed', 'Cancelled'],
      datasets: [{
        label: 'My Parking Statistics',
        data: [0, 0, 0, 0],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(34, 197, 94, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(239, 68, 68, 1)'
        ],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false
      }]
    }
  }
  
  return {
    labels: ['Total Bookings', 'Active', 'Completed', 'Cancelled'],
    datasets: [{
      label: 'My Parking Statistics',
      data: [
        userData.total_bookings || 0,
        userData.active_bookings || 0,
        userData.completed_bookings || 0,
        userData.cancelled_bookings || 0
      ],
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',   // Blue for total
        'rgba(34, 197, 94, 0.8)',    // Green for active
        'rgba(16, 185, 129, 0.8)',   // Teal for completed
        'rgba(239, 68, 68, 0.8)'     // Red for cancelled
      ],
      borderColor: [
        'rgba(59, 130, 246, 1)',
        'rgba(34, 197, 94, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(239, 68, 68, 1)'
      ],
      borderWidth: 2,
      borderRadius: 8,
      borderSkipped: false
    }]
  }
}

// Usage trend data (for line charts)
export const createUsageTrendData = (trendData) => {
  if (!trendData || !Array.isArray(trendData) || trendData.length === 0) {
    return {
      labels: ['No Data'],
      datasets: [{
        label: 'Occupancy Rate',
        data: [0],
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4
      }]
    }
  }
  
  return {
    labels: trendData.map(item => item.time || item.label),
    datasets: [{
      label: 'Occupancy Rate',
      data: trendData.map(item => item.occupancy || item.value),
      borderColor: 'rgba(59, 130, 246, 1)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 3,
      fill: true,
      tension: 0.4
    }]
  }
}

// Parking lot specific data
export const createParkingLotData = (lotData) => {
  if (!lotData || !Array.isArray(lotData) || lotData.length === 0) {
    return {
      labels: ['No Parking Lots'],
      datasets: [{
        label: 'Parking Lot Occupancy',
        data: [0],
        backgroundColor: generateChartColors(1),
        borderColor: generateBorderColors(1),
        borderWidth: 2
      }]
    }
  }
  
  return {
    labels: lotData.map(lot => lot.name || `Lot ${lot.id}`),
    datasets: [{
      label: 'Parking Lot Occupancy',
      data: lotData.map(lot => lot.occupancy || 0),
      backgroundColor: generateChartColors(lotData.length),
      borderColor: generateBorderColors(lotData.length),
      borderWidth: 2
    }]
  }
}

// ✅ Chart Error Handling
export const ChartErrorBoundary = defineComponent({
  name: 'ChartErrorBoundary',
  props: {
    fallback: {
      type: String,
      default: 'Chart could not be loaded'
    }
  },
  setup(props, { slots }) {
    return () => {
      try {
        return slots.default?.()
      } catch (error) {
        console.error('Chart Error:', error)
        return h('div', { 
          class: 'chart-error',
          style: {
            padding: '2rem',
            textAlign: 'center',
            color: '#666',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            minHeight: '200px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }
        }, props.fallback)
      }
    }
  }
})

// ✅ Export all components as default for easy importing
export default {
  AdminDoughnutChart,
  AdminBarChart,
  AdminPieChart,
  AdminPolarChart,
  UserDoughnutChart,
  UserBarChart,
  UserPersonalBarChart,
  UserLineChart,
  ChartErrorBoundary,
  generateChartColors,
  generateBorderColors,
  createAdminParkingData,
  createUserParkingData,
  createUserPersonalData,
  createUsageTrendData,
  createParkingLotData
}
