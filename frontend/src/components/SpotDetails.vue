<template>
  <div class="spot-modal-overlay" @click.self="closeModal">
    <div class="spot-modal">
      <div class="modal-header">
        <h3>
          <i class="bi bi-p-square-fill"></i>
          Parking Spot Details
        </h3>
        <button @click="closeModal" class="close-btn">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <div class="modal-body">
        <!-- Spot ID Section -->
        <div class="info-section">
          <div class="info-item">
            <label>
              <i class="bi bi-hash"></i>
              Spot ID
            </label>
            <div class="spot-id-badge">{{ spotId }}</div>
          </div>
        </div>

        <!-- Status Section -->
        <div class="info-section">
          <div class="info-item">
            <label>
              <i class="bi bi-circle-fill"></i>
              Current Status
            </label>
            <div :class="['status-badge', statusClass]">
              <i :class="statusIcon"></i>
              {{ statusText }}
            </div>
          </div>
        </div>

        <!-- Last Updated Section -->
        <div class="info-section">
          <div class="info-item">
            <label>
              <i class="bi bi-clock-history"></i>
              Booked on
            </label>
            <div class="last-updated">{{ lastUpdated }}</div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="closeModal" class="btn btn-primary">
          <i class="bi bi-check-circle"></i>
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SpotDetails',
  props: {
    spotId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      status: ''
    };
  },
  computed: {
    normalizedStatus() {
      const val = (this.status || 'A').toUpperCase();
      
      if (val === 'OCCUPIED') return 'O';
      if (val === 'AVAILABLE') return 'A';
      if (val === 'RESERVED') return 'R';
      
      return val.length === 1 ? val : 'A';
    },
    
    statusText() {
      switch (this.normalizedStatus) {
        case 'A': return 'Available';
        case 'O': return 'Occupied';
        case 'R': return 'Reserved';
        default: return 'Unknown';
      }
    },
    
    statusClass() {
      switch (this.normalizedStatus) {
        case 'A': return 'status-available';
        case 'O': return 'status-occupied';
        case 'R': return 'status-reserved';
        default: return 'status-unknown';
      }
    },
    
    statusIcon() {
      switch (this.normalizedStatus) {
        case 'A': return 'bi bi-check-circle-fill';
        case 'O': return 'bi bi-x-circle-fill';
        case 'R': return 'bi bi-clock-fill';
        default: return 'bi bi-question-circle-fill';
      }
    },
    
    lastUpdated() {
      return new Date().toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  },
  
  created() {
    // Get status from route query
    this.status = this.$route.query.status || 'A';
  },
  
  methods: {
    closeModal() {
      this.$router.push('/admin');
    }
  }
};
</script>

<style scoped>
/* Modal Overlay */
.spot-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

/* Main Modal */
.spot-modal {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  width: 100%;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px 16px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #495057;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #6c757d;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(108, 117, 125, 0.1);
  color: #495057;
}

/* Modal Body */
.modal-body {
  padding: 25px;
}

.info-section {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item label {
  font-weight: 600;
  color: #495057;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  margin: 0;
}

/* Spot ID Badge */
.spot-id-badge {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 15px 20px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 24px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

/* Status Badge */
.status-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 16px;
}

.status-available {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
}

.status-occupied {
  background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
  color: white;
}

.status-reserved {
  background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
  color: #212529;
}

.status-unknown {
  background: linear-gradient(135deg, #6c757d 0%, #adb5bd 100%);
  color: white;
}

/* Last Updated */
.last-updated {
  background: #f8f9fa;
  color: #495057;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 500;
  border: 1px solid #e9ecef;
  text-align: center;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: center;
  padding: 20px 25px;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
  border-radius: 0 0 16px 16px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.btn-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
  .spot-modal {
    margin: 10px;
    max-width: calc(100vw - 20px);
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 15px 20px;
  }
  
  .spot-id-badge {
    font-size: 20px;
    padding: 12px 16px;
  }
  
  .modal-header h3 {
    font-size: 16px;
  }
}
</style>
