<template>
  <nav class="navbar">
    <div class="nav-brand">
      <router-link to="/">🏔️ TrailBliss</router-link>
    </div>
    
    
    <div class="search-container" v-if="showSearch">
      <span class="search-icon">🔍</span>
      <input 
        type="text" 
        v-model="searchQuery" 
        @input="handleSearch" 
        placeholder="Search users, treks, or bookings..." 
        class="search-input"
      />
    </div>

    <div class="nav-links">
      <template v-if="!authStore.isAuthenticated">
        <router-link to="/login" class="nav-item">Log In</router-link>
        <router-link to="/register" class="btn btn-primary">Sign Up</router-link>
      </template>
      <template v-else>
        
        <button class="nav-item" @click="handleLogout">Log Out</button>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, watch, computed } from 'vue'; // Added computed
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore()
const route = useRoute();
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
const searchQuery = ref(route.query.search || '');

const handleSearch = () => {
  router.replace({ 
    query: { ...route.query, search: searchQuery.value || undefined } 
  });
};


watch(() => route.query.search, (newSearch) => {
  searchQuery.value = newSearch || '';
});


const showSearch = computed(() => {
  
  return route.path !== '/admin/reports';
});
</script>

<style scoped>
/* Basic styling for the search bar */
.admin-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}
.search-container {
  position: relative;
  width: 100%;
  max-width: 400px;
}
.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  color: #94a3b8;
}
.search-input {
  width: 100%;
  padding: 0.6rem 1rem 0.6rem 2.2rem;
  border: 1px solid #cbd5e1;
  border-radius: 99px; /* Pill shape */
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
}
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 5%;
  background: white;
  border-bottom: 1px solid var(--border);
}
.nav-brand a {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-main);
  text-decoration: none;
}
.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}
.nav-item {
  text-decoration: none;
  color: var(--text-main);
  font-weight: 600;
  cursor: pointer;
  background: none;
  border: none;
  font-size: 1rem;
}
.nav-item:hover {
  color: var(--primary);
}
</style>