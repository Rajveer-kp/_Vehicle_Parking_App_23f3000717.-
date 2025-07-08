/**
 * Utility to clear old authentication data that might not have tokens
 * This helps migrate from the old auth system to the new JWT-based system
 */

export function clearOldAuthData() {
  const userId = localStorage.getItem('userId');
  const token = localStorage.getItem('token');
  
  // If we have userId but no token, this is old auth data
  if (userId && !token) {
    console.log('Clearing old authentication data...');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    localStorage.removeItem('fullname');
    localStorage.removeItem('token');
    return true;
  }
  
  return false;
}

// Auto-clear on import
clearOldAuthData();
