<template>
  <div class="charts-wrapper">
    
    <!-- LEFT: Popular Treks Bar Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h2>Most Popular Treks</h2>
      </div>
      <div class="chart-container">
        <Bar v-if="popularTreks.length > 0" :data="barChartData" :options="barOptions" />
        <div v-else class="empty-state">No booking data available yet.</div>
      </div>
    </div>

    <!-- RIGHT: Booking Status Doughnut Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h2>Booking Status Breakdown</h2>
      </div>
      <div class="chart-container">
        <Doughnut v-if="hasStatusData" :data="doughnutChartData" :options="doughnutOptions" />
        <div v-else class="empty-state">No booking statuses available.</div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Bar, Doughnut } from 'vue-chartjs';
import { 
  Chart as ChartJS, Title, Tooltip, Legend, BarElement, 
  CategoryScale, LinearScale, ArcElement 
} from 'chart.js';

// Register ChartJS components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement);

const props = defineProps({
  popularTreks: {
    type: Array,
    required: true
  },
  statusBreakdown: {
    type: Object,
    required: true
  }
});

// --- Bar Chart Logic ---
const barChartData = computed(() => ({
  labels: props.popularTreks.map(t => t.name),
  datasets: [{
    label: 'Total Bookings',
    backgroundColor: '#f59e0b', // Indigo
    borderRadius: 10,
    data: props.popularTreks.map(t => t.bookings)
  }]
}));

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: true } },
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1 } }
  }
};

// --- Doughnut Chart Logic ---
const hasStatusData = computed(() => {
  return Object.values(props.statusBreakdown).some(val => val > 0);
});

const doughnutChartData = computed(() => ({
  labels: ['Confirmed', 'Cancelled'],
  datasets: [{
    backgroundColor: ['#16a34a', '#ef4444'], // Green, Amber, Red
    borderWidth: 3,
    borderRadius:7,
    data: [
      props.statusBreakdown.Confirmed || 0,
      props.statusBreakdown.Cancelled || 0
    ]
  }]
}));

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' }
  },
  cutout: '65%' // Makes it a doughnut instead of a pie
};
</script>

<style scoped>
.charts-wrapper {
  display: grid;
  grid-template-columns: 2fr 1fr; /* Bar chart gets more space than Doughnut */
  gap: 1.5rem;
  margin-top: 1.5rem;
}

@media (max-width: 900px) {
  .charts-wrapper { grid-template-columns: 1fr; } /* Stack on mobile */
}

.chart-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}
.card-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.chart-container {
  padding: 1.5rem;
  height: 300px; /* Fixed height is required for ChartJS responsive mode */
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  color: #94a3b8;
  font-style: italic;
  font-size: 0.95rem;
}
</style>