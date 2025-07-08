/**
 * Authentication Service
 * Handles token validation, session management, and auth state
 */

const API_BASE = 'http://localhost:5000/auth';

class AuthService {
  constructor() {
    this.isValidating = false;
    this.validationPromise = null;
  }

  /**
   * Check if user appears to be logged in (has localStorage data)
   * Requires both userId and token to be considered logged in
   */
  hasLocalAuth() {
    const userId = localStorage.getItem('userId');
    const token = localStorage.getItem('token');
    return !!(userId && token);
  }

  /**
   * Get current user data from localStorage
   */
  getCurrentUser() {
    if (!this.hasLocalAuth()) {
      return null;
    }

    return {
      userId: localStorage.getItem('userId'),
      username: localStorage.getItem('username'),
      role: localStorage.getItem('role'),
      token: localStorage.getItem('token')
    };
  }

  /**
   * Validate current session with backend
   * Returns: { valid: boolean, user?: object, error?: string }
   */
  async validateSession() {
    // Prevent multiple simultaneous validation calls
    if (this.isValidating && this.validationPromise) {
      return await this.validationPromise;
    }

    this.isValidating = true;
    this.validationPromise = this._performValidation();

    try {
      const result = await this.validationPromise;
      return result;
    } finally {
      this.isValidating = false;
      this.validationPromise = null;
    }
  }

  async _performValidation() {
    const user = this.getCurrentUser();
    
    if (!user || !user.token) {
      return { valid: false, error: 'No token found' };
    }

    try {
      const response = await fetch(`${API_BASE}/check-session`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        return { 
          valid: true, 
          user: {
            userId: data.user_id,
            username: data.username,
            role: data.role
          }
        };
      } else if (response.status === 401) {
        // Token expired or invalid
        return { valid: false, error: 'Session expired' };
      } else {
        // Other error
        const errorData = await response.json().catch(() => ({}));
        return { valid: false, error: errorData.message || 'Session validation failed' };
      }
    } catch (error) {
      // Network error or backend down
      console.warn('Session validation failed:', error.message);
      return { valid: false, error: 'Cannot reach server' };
    }
  }

  /**
   * Login user and store auth data
   */
  async login(username, password) {
    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        // Store auth data
        localStorage.setItem('userId', data.user_id);
        localStorage.setItem('username', data.username);
        localStorage.setItem('role', data.role);
        localStorage.setItem('token', data.token);

        return { success: true, user: data };
      } else {
        return { success: false, error: data.message || 'Login failed' };
      }
    } catch (error) {
      return { success: false, error: 'Network error: ' + error.message };
    }
  }

  /**
   * Logout user
   */
  async logout() {
    const user = this.getCurrentUser();
    
    // Call backend logout if we have a token
    if (user && user.token) {
      try {
        await fetch(`${API_BASE}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json'
          }
        });
      } catch (error) {
        console.warn('Logout request failed:', error.message);
      }
    }

    // Clear local storage
    this.clearAuthData();
  }

  /**
   * Clear authentication data from localStorage
   */
  clearAuthData() {
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    localStorage.removeItem('token');
  }

  /**
   * Check if current user has specific role
   */
  hasRole(role) {
    const user = this.getCurrentUser();
    return user && user.role === role;
  }

  /**
   * Get authorization header for API requests
   */
  getAuthHeader() {
    const user = this.getCurrentUser();
    return user && user.token ? { 'Authorization': `Bearer ${user.token}` } : {};
  }
}

// Export singleton instance
export default new AuthService();
