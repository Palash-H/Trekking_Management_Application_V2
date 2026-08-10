<template>
  <nav class="navbar">
    <!-- 1. Logo / Brand -->
    <div class="nav-brand">
      <router-link to="/">🏔️ TrekApp</router-link>
    </div>
    

    <!-- 3. Navigation Links -->
    <div class="nav-links">
      <!-- LOGGED OUT STATE -->
      <template v-if="!isAuthenticated">
        <router-link to="/login" class="nav-item">Log In</router-link>
        <router-link to="/register" class="btn-primary">Sign Up</router-link>
      </template>
    
      <!-- LOGGED IN STATE -->
      <template v-else>
        <router-link to="/me" v-if="isTrekker" class="nav-item">Profile</router-link>
        <!-- Explore is ONLY for Trekkers -->
        <router-link to="/trekker/explore" v-if="isTrekker" class="nav-item">Explore</router-link>
        
        <!-- Dashboard dynamically routes based on exact role -->
        <router-link :to="dashboardRoute" class="nav-item">My Dashboard</router-link>
        
        <button class="nav-item btn-logout" @click="handleLogout">Log Out</button>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// --- Authentication State ---
const isAuthenticated = ref(false);
const userRole = ref('');


const checkAuth = () => {
  isAuthenticated.value = !!localStorage.getItem('token');
  userRole.value = localStorage.getItem('role');
};

watch(() => route.path, () => {
  checkAuth();
});

onMounted(() => {
  checkAuth();
});

// --- Role Helpers ---
const isTrekker = computed(() => userRole.value === 'trekker');


const dashboardRoute = computed(() => {
  if (userRole.value === 'admin') return '/admin/dashboard';
  if (userRole.value === 'trekstaff') return '/staff/dashboard';
  return '/trekker/dashboard'; // Default to trekker dashboard
});

// --- Search Logic (For Trekkers Only) ---
const searchQuery = ref(route.query.search || '');

const handleSearch = () => {
  if (route.path !== '/explore') {
    router.push({ path: '/explore', query: { search: searchQuery.value } });
  } else {
    router.replace({ query: { ...route.query, search: searchQuery.value || undefined } });
  }
};

watch(() => route.query.search, (newSearch) => {
  searchQuery.value = newSearch || '';
});

// --- Logout Logic ---
const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('userRole');
  checkAuth(); 
  
  router.push('/login');
};
</script>

<style scoped>

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 5%;
  background: rgba(255, 255, 255, 0.85); 
  backdrop-filter: blur(12px); 
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.nav-brand a {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main);
  text-decoration: none;
  letter-spacing: -0.02em;
  transition: opacity 0.2s;
}

.nav-brand a:hover {
  opacity: 0.8;
}

/* --- Premium Search Bar --- */
.search-container {
  flex: 1;
  max-width: 420px;
  position: relative;
  margin: 0 2.5rem;
}

.search-icon { 
  position: absolute; 
  left: 16px; 
  top: 50%; 
  transform: translateY(-50%); 
  font-size: 1.1rem;
  opacity: 0.4; 
  pointer-events: none; /* Prevents icon from blocking clicks */
}

.search-input {
  width: 100%; 
  padding: 0.75rem 1.2rem 0.75rem 2.8rem;
  border: 1px solid var(--border); 
  border-radius: 50px; /* Fully rounded pill shape */
  font-size: 0.95rem; 
  color: var(--text-main);
  outline: none; 
  background: #f8fafc; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-input::placeholder {
  color: var(--text-muted);
  font-weight: 500;
}

.search-input:focus { 
  background: #ffffff; 
  border-color: var(--primary); 
  box-shadow: 0 0 0 4px rgba(46, 125, 50, 0.15); 
}


.nav-links { 
  display: flex; 
  align-items: center; 
  gap: 1rem; 
}


.nav-item {
  color: var(--text-muted); 
  text-decoration: none; 
  font-weight: 600; 
  font-size: 0.95rem;
  background: transparent; 
  border: none; 
  cursor: pointer; 
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-item:hover { 
  color: var(--text-main); 
  background: rgba(15, 23, 42, 0.04); /* Subtle grey background on hover */
}


.btn-logout { color: #ef4444; }
.btn-logout:hover { 
  background: rgba(239, 68, 68, 0.1); /* Soft red background instead of underline */
  color: #dc2626; 
}


.btn-primary {
  background-color: var(--primary); 
  color: white; 
  padding: 0.7rem 1.5rem;
  border-radius: 50px; 
  text-decoration: none; 
  font-weight: 600; 
  font-size: 0.95rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
}

.btn-primary:hover { 
  background-color: var(--primary-hover); 
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(46, 125, 50, 0.3);
}

.btn-primary:active {
  transform: translateY(0) scale(0.97);
}


@media (max-width: 768px) {
  .search-container { display: none; }
  .navbar { padding: 1rem 1.5rem; }
  .nav-links { gap: 0.5rem; }
  .btn-primary { padding: 0.6rem 1.2rem; }
}
</style>