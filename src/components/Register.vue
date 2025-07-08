<template>
  <div class="container mt-5">
    <h2 class="text-primary">User Signup</h2>
    <form @submit.prevent="register">
      <div class="form-group mb-3">
        <label>Email ID (Username)</label>
        <input v-model="username" type="email" class="form-control" required />
      </div>

      <div class="form-group mb-3">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>

      <div class="form-group mb-3">
        <label>Full Name</label>
        <input v-model="fullname" type="text" class="form-control" required />
      </div>

      <div class="form-group mb-3">
        <label>Address</label>
        <textarea v-model="address" class="form-control" rows="3" required></textarea>
      </div>

      <div class="form-group mb-3">
        <label>Pin Code</label>
        <input v-model="pincode" type="text" class="form-control" maxlength="6" pattern="[0-9]{6}" required />
      </div>

      <button type="submit" class="btn btn-primary">Register</button>

      <p class="mt-3">
        <router-link to="/">Login here!</router-link>
      </p>

      <p class="mt-3 text-success" v-if="successMessage">{{ successMessage }}</p>
      <p class="mt-3 text-danger" v-if="errorMessage">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      password: '',
      fullname: '',
      address: '',
      pincode: '',
      successMessage: '',
      errorMessage: ''
    }
  },
  methods: {
    async register() {
      try {
        await axios.post('http://127.0.0.1:5000/auth/register', {
          username: this.username,
          password: this.password,
          fullname: this.fullname,
          address: this.address,
          pincode: this.pincode
        })
        this.successMessage = 'Registration successful! You can now log in.'
        this.errorMessage = ''
        this.username = this.password = this.fullname = this.address = this.pincode = ''
      } catch (error) {
        this.errorMessage = 'Registration failed. Try a different username.'
        this.successMessage = ''
      }
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 450px;
  background: #f8f9fa;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin: 50px auto;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  font-weight: 600;
}

.form-group label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 8px;
}

.form-control {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 12px 15px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.btn-primary {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border: none;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 123, 255, 0.3);
}

.text-success {
  background: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #c3e6cb;
}

.text-danger {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
}

a {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

a:hover {
  text-decoration: underline;
}
</style>
