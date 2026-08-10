<template>
  <div class="dashboard">
    <header class="page-header">
      <div>
        <h1>{{ isSearchMode ? 'Search Results' : 'Dashboard Overview' }}</h1>
        <p v-if="!isSearchMode">Welcome back, Admin.</p>
        <p v-else>Showing results for: <strong>"{{ searchQuery }}"</strong></p>
      </div>
    </header>

    
    <div v-if="!isSearchMode">
      <div v-if="loadingStats" class="loading-state">Loading dashboard data...</div>
      
      <div v-else>
        
        <div class="stats-grid">
          <DashboardStatCard title="Total Revenue" :value="'₹' + (stats.total_revenue || 0).toLocaleString()" highlight />
          <DashboardStatCard title="Total Bookings" :value="stats.total_bookings" />
          <DashboardStatCard title="Total Trekkers" :value="stats.total_trekkers" />
          <DashboardStatCard title="Total Staff" :value="stats.total_staff" />
          <DashboardStatCard title="Active Treks" :value="stats.active_treks" />
        </div>

        
        <DashboardCharts 
          :popularTreks="chartData.popularTreks" 
          :statusBreakdown="chartData.statusBreakdown" 
        />
      </div>
    </div>

    <!-- SEARCH STATE: Global Search Results Component -->
    <DashboardSearchResults 
      v-else 
      :results="searchResults" 
      :isSearching="isSearching" 
    />

  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

// Import Child Components
import DashboardStatCard from '@/components/Admin/DashboardStatCard.vue';
import DashboardSearchResults from '@/components/Admin/DashboardSearchResults.vue';
import DashboardCharts from '@/components/Admin/DashboardCharts.vue'; // <-- 🌟 NEW IMPORT

const route = useRoute();

// --- Data State ---
const stats = ref({ total_trekkers: 0, total_staff: 0, active_treks: 0, total_bookings: 0, total_revenue: 0 });
const chartData = ref({ popularTreks: [], statusBreakdown: {} }); // <-- 🌟 NEW STATE FOR CHARTS
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


const fetchDashboardData = async () => {
  loadingStats.value = true;
  try {
    const [statsRes, chartsRes] = await Promise.all([
      axios.get('/api/admin/dashboard-stats'),
      axios.get('/api/admin/statistics') 
    ]);
    
    stats.value = statsRes.data;
    chartData.value = {
      popularTreks: chartsRes.data.popular_treks || [],
      statusBreakdown: chartsRes.data.status_breakdown || {}
    };
  } catch (error) {
    console.error("Failed to load dashboard data:", error);
  } finally {
    loadingStats.value = false;
  }
};

const performGlobalSearch = async (query) => {
  isSearching.value = true;
  try {
    
    const usersRes = await axios.get(`/admin/users?search=${query}`);
    searchResults.value.users = usersRes.data.users || [];

    const treksRes = await axios.get(`/api/admin/treks?search=${query}`); 
    searchResults.value.treks = treksRes.data.treks || treksRes.data || [];

    const bookingsRes = await axios.get(`/api/admin/bookings?search=${query}`);
    searchResults.value.bookings = bookingsRes.data.bookings || [];
  } catch (error) {
    console.error("Failed during global search:", error);
  } finally {
    isSearching.value = false;
  }
};


let searchTimeout = null;


watch(() => route.query.search, (newSearch) => {
  searchQuery.value = newSearch || '';
  
  if (searchTimeout) clearTimeout(searchTimeout);
  
  searchTimeout = setTimeout(() => {
    if (isSearchMode.value) {
      performGlobalSearch(searchQuery.value);
    } else {
      fetchDashboardData(); 
    }
  }, 500); 

}, { immediate: true }); 
</script>

<style scoped>

.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 2rem; color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;}
.page-header p { color: #64748b; }

.loading-state { text-align: center; padding: 3rem; color: #64748b; font-size: 1.1rem; }


.stats-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
  gap: 1.5rem; 
}
</style>