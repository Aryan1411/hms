import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import LoginAdmin from '../views/LoginAdmin.vue'
import LoginDoctor from '../views/LoginDoctor.vue'
import LoginPatient from '../views/LoginPatient.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import DoctorDashboard from '../views/DoctorDashboard.vue'
import PatientDashboard from '../views/PatientDashboard.vue'
import PatientHistory from '../views/PatientHistory.vue'
import PatientProfile from '../views/PatientProfile.vue'
import DoctorPatientHistory from '../views/DoctorPatientHistory.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login/admin', component: LoginAdmin },
  { path: '/login/doctor', component: LoginDoctor },
  { path: '/login/patient', component: LoginPatient },
  { path: '/register', component: Register },
  {
    path: '/admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/doctor',
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/patient',
    component: PatientDashboard,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/patient/history',
    component: PatientHistory,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/patient/profile',
    component: PatientProfile,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/doctor/patient-history/:id',
    component: DoctorPatientHistory,
    meta: { requiresAuth: true, role: 'doctor' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('token')
  const role = sessionStorage.getItem('role')

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!token) {
      // No token, redirect to home
      next('/')
    } else {
      // Check if role matches
      if (to.meta.role && to.meta.role !== role) {
        // Wrong role, redirect to appropriate dashboard or home
        if (role === 'admin') next('/admin')
        else if (role === 'doctor') next('/doctor')
        else if (role === 'patient') next('/patient')
        else next('/')
      } else {
        // Token exists and role matches, allow access
        next()
      }
    }
  } else {
    // Route doesn't require auth, allow access
    next()
  }
})

export default router
