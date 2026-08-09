<template>
  <div class="dashboard">
    <header class="page-header">
      <div>
        <h1>{{ isSearchMode ? 'Search Results' : 'Dashboard Overview' }}</h1>
        <p v-if="!isSearchMode">Welcome back, Admin.</p>
        <p v-else>Showing results for: <strong>"{{ searchQuery }}"</strong></p>
      </div>
    </header>

    <!-- DEFAULT STATE: Stats Grid -->
    <div v-if="!isSearchMode">
      <div v-if="loadingStats" class="loading-state">Loading stats...</div>
      
      <!-- 🌟 Use Stat Card Components 🌟 -->
      <div v-else class="stats-grid">
        <DashboardStatCard title="Total Trekkers" :value="stats.total_trekkers" />
        <DashboardStatCard title="Total Staff" :value="stats.total_staff" />
        <DashboardStatCard title="Total Treks" :value="stats.active_treks" />
        <DashboardStatCard title="Total Bookings" :value="stats.total_bookings" highlight />
      </div>
    </div>

    <!-- SEARCH STATE: Global Search Results Component 🌟 -->
    <DashboardSearchResults 
      v-else 
      :results="searchResults" 
      :isSearching="isSearching" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

// Import Child Components
import DashboardStatCard from '@/components/Admin/DashboardStatCard.vue';
import DashboardSearchResults from '@/components/Admin/DashboardSearchResults.vue';

const route = useRoute();

// --- Stats State ---
const stats = ref({ total_trekkers: 0, total_staff: 0, active_treks: 0, total_bookings: 0 });
const loadingStats = ref(true);

// --- Search State ---
const searchQuery = ref(route.query.search || '');
const isSearching = ref(false);
const searchResults = ref({ users: [], treks: [], bookings: [] });

// Check if we should show stats or search results
const isSearchMode = computed(() => {
  return searchQuery.value.trim().length > 0;
});

// --- API Calls ---
const fetchStats = async () => {
  try {
    const response = await axios.get('/api/admin/dashboard-stats');
    stats.value = response.data;
  } catch (error) {
    console.error("Failed to load stats:", error);
  } finally {
    loadingStats.value = false;
  }
};

const performGlobalSearch = async (query) => {
  isSearching.value = true;
  try {
    // 1. Fetch Users
    const usersRes = await axios.get(`/admin/users?search=${query}`);
    searchResults.value.users = usersRes.data.users || [];

    // 2. Fetch Treks
    const treksRes = await axios.get(`/api/admin/treks?search=${query}`); 
    searchResults.value.treks = treksRes.data.treks || treksRes.data || [];

    // 3. Fetch Bookings
    const bookingsRes = await axios.get(`/api/admin/bookings?search=${query}`);
    searchResults.value.bookings = bookingsRes.data.bookings || [];
  } catch (error) {
    console.error("Failed during global search:", error);
  } finally {
    isSearching.value = false;
  }
};

// --- Lifecycle ---
watch(() => route.query.search, (newSearch) => {
  searchQuery.value = newSearch || '';
  
  if (isSearchMode.value) {
    performGlobalSearch(searchQuery.value);
  } else {
    fetchStats(); 
  }
});

onMounted(() => {
  if (isSearchMode.value) {
    performGlobalSearch(searchQuery.value);
  } else {
    fetchStats();
  }
});
</script>

<style scoped>
/* Only structural macro-layout CSS remains here */
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 2rem; color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;}
.page-header p { color: #64748b; }
.loading-state { text-align: center; padding: 3rem; color: #64748b; font-size: 1.1rem; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; }
</style>