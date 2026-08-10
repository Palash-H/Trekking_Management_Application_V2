<template>
  <div class="staff-dashboard">
    <header class="page-header">
      <div>
        <h1>Staff Dashboard</h1>
        <p>Welcome back! Here is an overview of your trekking assignments.</p>
      </div>
    </header>

    <div v-if="loading" class="loading-state">Loading your dashboard...</div>

    <div v-else>
      
      <div class="stats-grid">
        <StaffStatCard 
          title="Total Assigned" 
          :value="summary.total_assigned" 
        />
        <StaffStatCard 
          title="Active Treks" 
          :value="summary.active_treks" 
          highlightClass="highlight-blue" 
        />
        <StaffStatCard 
          title="Completed" 
          :value="summary.completed_treks" 
          highlightClass="highlight-green" 
        />
        <StaffStatCard 
          title="Total Trekkers" 
          :value="summary.total_participants_managed" 
          highlightClass="highlight-indigo" 
        />
      </div>

      <!-- Divider -->
      <div class="section-divider">
        <h2>My Assigned Treks</h2>
      </div>

      <div v-if="treks.length === 0" class="empty-state">
        <h3>No Treks Assigned</h3>
        <p>You have not been assigned to lead any treks yet. Check back later!</p>
      </div>

      
      <div v-else class="trek-grid">
        <StaffTrekCard 
          v-for="trek in treks" 
          :key="trek.trek_id" 
          :trek="trek" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
// Import child components
import StaffStatCard from '@/components/Staff/StaffStatCard.vue';
import StaffTrekCard from '@/components/Staff/StaffTrekCard.vue';

// --- State ---
const summary = ref({
  total_assigned: 0,
  active_treks: 0,
  completed_treks: 0,
  total_participants_managed: 0
});
const treks = ref([]);
const loading = ref(true);

// --- API Calls ---
const fetchDashboardData = async () => {
  try {
    const [summaryRes, treksRes] = await Promise.all([
      axios.get('/api/staff/dashboard/summary'),
      axios.get('/staff/my-assignments')
    ]);

    summary.value = summaryRes.data;
    treks.value = treksRes.data.assignments;
  } catch (error) {
    console.error("Failed to fetch staff dashboard data:", error);
    if (error.response?.status === 403) {
      alert("Unauthorized: Only Trek Staff can view this page.");
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<style scoped>

.staff-dashboard { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 2.25rem; color: #0f172a; font-weight: 700; margin-bottom: 0.5rem; }
.page-header p { color: #64748b; font-size: 1.1rem; }

.loading-state, .empty-state { text-align: center; padding: 4rem; color: #64748b; background: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1; }
.empty-state h3 { color: #0f172a; margin-bottom: 0.5rem; font-size: 1.25rem; }


.stats-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
  gap: 1.5rem; 
  margin-bottom: 3rem; 
}

.section-divider { 
  margin-bottom: 1.5rem; 
  border-bottom: 2px solid #e2e8f0; 
  padding-bottom: 0.5rem; 
}
.section-divider h2 { 
  font-size: 1.5rem; 
  color: #0f172a; 
  font-weight: 700; 
}

.trek-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
  gap: 2rem; 
  align-items: stretch; 
}
</style>