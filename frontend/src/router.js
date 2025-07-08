import { createRouter, createWebHistory } from 'vue-router'
import authService from './services/auth.js'

// Component imports
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import AddParkingLot from './components/AddParkingLot.vue'
import EditParking from './components/EditParking.vue'
import SpotDetails from './components/SpotDetails.vue'
import UserDashboard from './components/UserDashboard.vue'
import AdminUsers from './components/AdminUsers.vue'
import AdminSearch from './components/AdminSearch.vue'
import AdminSummary from './components/AdminSummary.vue'
import UserSummary from './components/UserSummary.vue'
// import NotFound from './components/NotFound.vue'

const routes = [
  // Guest Routes
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    redirect: '/login'
  },

  // Admin Routes
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/add-lot',
    name: 'AddParkingLot',
    component: AddParkingLot,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/edit-lot/:lotId',
    name: 'EditLot',
    component: EditParking,
    props: true,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
  path: '/admin/lot/:lotId/spot/:spotId',
  name: 'SpotDetails',
  component: SpotDetails,
  props: route => ({
    lotId: Number(route.params.lotId),
    spotId: Number(route.params.spotId)
  }),
  meta: { requiresAuth: true, role: 'admin' }
}
,

  // User Routes
  {
    path: '/user',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, role: 'user' }
  },
  {path: '/admin/registered-users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {path: '/admin/Search',
    name: 'Search',
    component: AdminSearch,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {path: '/user/summary',
    name: 'UserSummary',
    component: UserSummary,
    meta: { requiresAuth: true, role: 'user' }},
  {path: '/admin/summary',
    name: 'AdminSummary',
    component: AdminSummary,
    meta: { requiresAuth: true, role: 'admin' }},

  // Catch-all route (404 Not Found)
  {
    path: '/:catchAll(.*)',
    redirect: '/'
    // or use: component: NotFound
  }
]

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes
})

// ✅ Global Navigation Guard with Backend Session Validation
router.beforeEach(async (to, from, next) => {
  // Check if user appears to be logged in locally
  const hasLocalAuth = authService.hasLocalAuth();

  // If route requires authentication
  if (to.meta.requiresAuth) {
    if (!hasLocalAuth) {
      // No local auth data, redirect to login
      return next('/login');
    }

    // Validate session with backend
    const sessionResult = await authService.validateSession();
    
    if (!sessionResult.valid) {
      // Session invalid - clear local auth and redirect to login
      console.warn('Session validation failed:', sessionResult.error);
      authService.clearAuthData();
      return next('/login');
    }

    // Check role requirements
    if (to.meta.role && sessionResult.user.role !== to.meta.role) {
      console.warn('Role mismatch. Required:', to.meta.role, 'User role:', sessionResult.user.role);
      return next('/login');
    }

    // Session valid and role matches, proceed
    return next();
  }

  // If guest-only route (login/register) but user appears to be logged in
  if (to.meta.requiresGuest && hasLocalAuth) {
    // Only validate session if we have a token - if no token, just clear old data
    const currentUser = authService.getCurrentUser();
    if (!currentUser || !currentUser.token) {
      // No token, clear stale localStorage data and allow access to guest route
      authService.clearAuthData();
      return next();
    }

    // We have a token, validate the session
    const sessionResult = await authService.validateSession();
    
    if (sessionResult.valid) {
      // Valid session, redirect to appropriate dashboard
      const redirectPath = sessionResult.user.role === 'admin' ? '/admin' : '/user';
      return next(redirectPath);
    } else {
      // Invalid session, clear auth data and allow access to guest route
      authService.clearAuthData();
      return next();
    }
  }

  // No auth requirements or guest route with no local auth
  next();
})

export default router
