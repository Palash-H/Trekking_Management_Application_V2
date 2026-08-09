import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

import PublicLayout from '@/layouts/PublicLayout.vue';
import HomeView from '@/views/public/HomeView.vue';
import LoginView from '@/views/public/LoginView.vue';
import RegisterView from '@/views/public/RegisterView.vue';
import ManageTreks from '@/views/admin/ManageTreks.vue';

// Admin Imports
import AdminLayout from '@/layouts/AdminLayout.vue';
import AdminDashboard from '@/views/admin/AdminDashboard.vue';
import CreateTrek from '@/views/admin/CreateTrek.vue';
import ManageUsers from '@/views/admin/ManageUsers.vue';
import ManageBookings from '../views/admin/ManageBookings.vue';
import AdminReports from '../views/admin/AdminReports.vue';
import StaffDashboard from '../views/staff/StaffDashboard.vue';
import ManageTrekStaff from '../views/staff/ManageTrekStaff.vue';
import ExploreTreks from '../views/trekker/ExploreTreks.vue';
import UserDashboard from '../views/trekker/UserDashboard.vue';
import UserProfile from '../views/trekker/UserProfile.vue';
// ...

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: PublicLayout,
      children: [
        { path: '', name: 'home', component: HomeView },
        { path: 'login', name: 'login', component: LoginView },
        { path: 'register', name: 'register', component: RegisterView },
        { path: 'staff/dashboard', name:'staffdashboard', component: StaffDashboard},
        {path: '/staff/treks/:id/manage', name: 'ManageTrekStaff', component: ManageTrekStaff},
        {path: '/trekker/explore', name: 'ExploreTreks', component: ExploreTreks, meta:{requiresAuth:true, role:"trekker"} },
        {path: '/trekker/dashboard', name: 'TrekkerDashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'trekker' }},
        {path: '/me', name: 'TrekkerProfile', component: UserProfile, meta:{requiresAuth: true, role:'trekker'}}
      ]
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: 'dashboard', name: 'adminDashboard', component: AdminDashboard },
        // We will add Manage Treks here later!
        { path: 'treks', name: 'adminTreks', component: ManageTreks },
        { path: 'users', name: 'adminUsers', component: ManageUsers },
        { path: 'treks/create', name: 'createTrek', component: CreateTrek },
        { path: '/admin/bookings', name: 'ManageBookings', component: ManageBookings },
        { path: '/admin/reports', name: 'AdminReports', component: AdminReports }
        
      ]
    }
    
  ]
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  authStore.initAuth();

  // If the route requires authentication and user is not logged in
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } 
  // If the route requires admin but the user is not an admin
  else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/'); // Kick them to home page
  } 
  else {
    next();
  }
});

export default router;