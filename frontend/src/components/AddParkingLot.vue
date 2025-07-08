<template>
  <div class="container">
    <h3 class="title">New Parking Lot</h3>
    <form class="form" @submit.prevent="submitForm" novalidate>
      <div class="form-group">
        <label>Prime Location Name:</label>
        <input
          type="text"
          v-model.trim="lot.name"
          :class="{ invalid: errors.name }"
          required
          placeholder="Enter name"
        />
        <div class="invalid-feedback" v-if="errors.name">{{ errors.name }}</div>
      </div>

      <div class="form-group">
        <label>Address:</label>
        <textarea
          v-model.trim="lot.address"
          :class="{ invalid: errors.address }"
          required
          placeholder="Enter address"
        ></textarea>
        <div class="invalid-feedback" v-if="errors.address">{{ errors.address }}</div>
      </div>

      <div class="form-group">
        <label>Pin Code:</label>
        <input
          type="text"
          v-model.trim="lot.pincode"
          pattern="[0-9]{6}"
          :class="{ invalid: errors.pincode }"
          required
          placeholder="6-digit pincode"
        />
        <div class="invalid-feedback" v-if="errors.pincode">{{ errors.pincode }}</div>
      </div>

      <div class="form-group">
        <label>Price (per hour):</label>
        <input
          type="number"
          v-model.number="lot.price"
          min="0"
          step="0.01"
          :class="{ invalid: errors.price }"
          required
          placeholder="Enter price"
        />
        <div class="invalid-feedback" v-if="errors.price">{{ errors.price }}</div>
      </div>

      <div class="form-group">
        <label>Maximum Spots:</label>
        <input
          type="number"
          v-model.number="lot.maxSpots"
          min="1"
          :class="{ invalid: errors.maxSpots }"
          required
          placeholder="Enter max spots"
        />
        <div class="invalid-feedback" v-if="errors.maxSpots">{{ errors.maxSpots }}</div>
      </div>

      <div class="button-group">
        <button type="submit" :disabled="isLoading" class="btn-primary">
          {{ isLoading ? 'Adding...' : 'Add' }}
        </button>
        <router-link to="/admin" class="btn-secondary">Cancel</router-link>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AddParkingLot',
  data() {
    return {
      lot: {
        name: '',
        address: '',
        pincode: '',
        price: null,
        maxSpots: null
      },
      errors: {},
      isLoading: false
    };
  },
  methods: {
    validateForm() {
      this.errors = {};

      const price = parseFloat(this.lot.price);
      const maxSpots = parseInt(this.lot.maxSpots);

      if (!this.lot.name) this.errors.name = 'Name is required';
      if (!this.lot.address) this.errors.address = 'Address is required';
      if (!/^[0-9]{6}$/.test(this.lot.pincode)) this.errors.pincode = 'Enter valid 6-digit pincode';
      if (!(price > 0)) this.errors.price = 'Price must be greater than 0';
      if (!(maxSpots >= 1)) this.errors.maxSpots = 'Must have at least 1 spot';

      return Object.keys(this.errors).length === 0;
    },
    async submitForm() {
      if (!this.validateForm()) return;

      this.isLoading = true;

      const backendUrl = 'http://127.0.0.1:5000';

      // Try getting admin ID safely
      const adminId = (this.$store && this.$store.state && this.$store.state.user && this.$store.state.user.id) || 1;

      try {
        const response = await axios.post(`${backendUrl}/admin/add-parking-lot`, {
          name: this.lot.name,
          address: this.lot.address,
          pincode: this.lot.pincode,
          price: parseFloat(this.lot.price),
          maxSpots: parseInt(this.lot.maxSpots),
          adminId
        });

        // Show success toast if $toast is available
        if (this.$toast && typeof this.$toast.success === 'function') {
          this.$toast.success(response.data.message || 'Parking lot added successfully');
        } else {
          alert(response.data.message || 'Parking lot added successfully'); // fallback
        }

        // Redirect to /admin if router is available
        if (this.$router && typeof this.$router.push === 'function') {
          this.$router.push('/admin');
        }
      } catch (error) {
        console.error('Error adding parking lot:', error);

        const errMsg = error.response?.data?.error || 'Failed to add parking lot';

        if (this.$toast && typeof this.$toast.error === 'function') {
          this.$toast.error(errMsg);
        } else {
          alert(errMsg); // fallback
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 450px;
  margin: 3rem auto;
  padding: 1.5rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 6px 15px rgb(0 0 0 / 0.1);
  font-family: Arial, sans-serif;
}

.title {
  text-align: center;
  color: #007bff;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 0.4rem;
  font-weight: 600;
}

input,
textarea {
  padding: 0.5rem 0.7rem;
  font-size: 1rem;
  border: 1.8px solid #ccc;
  border-radius: 4px;
  transition: border-color 0.3s ease;
  font-family: inherit;
  resize: vertical;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #007bff;
}

.invalid {
  border-color: #dc3545 !important; /* red */
}

.invalid-feedback {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.button-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

button,
.btn-secondary {
  padding: 0.5rem 1.3rem;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  font-size: 1rem;
  user-select: none;
  text-decoration: none;
  text-align: center;
  display: inline-block;
  min-width: 100px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

button[disabled] {
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not([disabled]) {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style>
