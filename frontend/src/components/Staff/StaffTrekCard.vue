<template>
  <div class="trek-card">
    
    <div class="card-header">
      <h2 class="trek-title">{{ trek.name }}</h2>
      <span :class="['status-badge', normalizedStatus]">
        {{ trek.status || 'Pending' }}
      </span>
    </div>
    
    <p class="location">📍 {{ trek.location }}</p>
    
    <div class="stats-row">
      <div class="stat-box">
        <span class="label">Dates</span>
        <span class="value date-text">
          {{ formattedStartDate }} - {{ formattedEndDate }}
        </span>
      </div>
      <div class="stat-box">
        <span class="label">Booked Slots</span>
        <span class="value highlight-text">{{ trek.total_trekkers_booked }} Users</span>
      </div>
    </div>

    <div class="card-footer">
      <router-link :to="`/staff/treks/${trek.trek_id}/manage`" class="btn btn-primary">
        Manage Trek & Participants ➔
      </router-link>
    </div>
    
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  trek: {
    type: Object,
    required: true
  }
});


const normalizedStatus = computed(() => {
  return (props.trek.status || 'Pending').toLowerCase().replace(' ', '-');
});

// Format dates 
const formatDate = (dateString) => {
  if (!dateString || dateString === 'N/A') return 'N/A';
  return new Date(dateString).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
};

const formattedStartDate = computed(() => formatDate(props.trek.start_date));
const formattedEndDate = computed(() => formatDate(props.trek.end_date));
</script>

<style scoped>
.trek-card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; overflow: hidden; transition: transform 0.2s, box-shadow 0.2s; height: 100%; }
.trek-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }

.card-header { padding: 1.5rem 1.5rem 0.5rem; display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.trek-title { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; line-height: 1.3; }
.location { padding: 0 1.5rem; color: #64748b; font-size: 0.95rem; margin-bottom: 1.5rem; }

/* Stats Row */
.stats-row { display: flex; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; background: #f8fafc; }
.stat-box { flex: 1; padding: 1rem; display: flex; flex-direction: column; gap: 0.25rem; border-right: 1px solid #f1f5f9; text-align: center; }
.stat-box:last-child { border-right: none; }
.stat-box .label { font-size: 0.75rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.stat-box .value { font-size: 0.95rem; font-weight: 600; color: #334155; }
.date-text { font-size: 0.85rem !important; }
.highlight-text { color: #4f46e5 !important; } 

/* Footer & Buttons */
.card-footer { padding: 1.5rem; background: #ffffff; margin-top: auto; }
.btn { display: block; width: 100%; text-align: center; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; text-decoration: none; border: none; }
.btn-primary { background-color: #4f46e5; color: white; }
.btn-primary:hover { background-color: #4338ca; }

/* Badges */
.status-badge { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; white-space: nowrap; }
.status-badge.active, .status-badge.open { background-color: #dcfce3; color: #166534; }
.status-badge.in-progress, .status-badge.started { background-color: #dbeafe; color: #1e40af; }
.status-badge.completed, .status-badge.closed { background-color: #e2e8f0; color: #475569; }
.status-badge.pending { background-color: #fef08a; color: #854d0e; }
.status-badge.cancelled { background-color: #fee2e2; color: #991b1b; }
</style>