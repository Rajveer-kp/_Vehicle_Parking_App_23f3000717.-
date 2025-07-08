<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title">Login</h2>
      <form @submit.prevent="login" novalidate>
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter username"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter password"
            required
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <p class="message" v-if="message">{{ message }}</p>

      <p class="register-text">
        Don't have an account?
        <router-link to="/register">Register here</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import authService from '../services/auth.js'

export default {
  data() {
    return {
      username: '',
      password: '',
      message: '',
      loading: false
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.message = ''
      
      try {
        const result = await authService.login(this.username, this.password)

        if (result.success) {
          // Login successful, redirect based on role
          const redirectPath = result.user.role === 'admin' ? '/admin' : '/user'
          this.$router.push(redirectPath)
        } else {
          this.message = result.error || 'Login failed'
        }
      } catch (err) {
        this.message = 'An unexpected error occurred. Please try again.'
        console.error('Login error:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
  padding: 1rem;
}

.login-card {
  background: white;
  padding: 2rem 2.5rem;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgb(0 0 0 / 0.1);
  max-width: 400px;
  width: 100%;
  box-sizing: border-box;
}

.title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #007bff;
  font-weight: 700;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.25rem;
}

label {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

input[type='text'],
input[type='password'] {
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  border: 1.5px solid #ccc;
  border-radius: 5px;
  transition: border-color 0.3s ease;
}

input[type='text']:focus,
input[type='password']:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 5px #007bffaa;
}

.btn-primary {
  width: 100%;
  padding: 0.6rem;
  font-size: 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #007bff88;
  cursor: not-allowed;
}

.message {
  margin-top: 1rem;
  text-align: center;
  color: red;
}

.register-text {
  margin-top: 1rem;
  text-align: center;
  color: #555;
}
</style>
