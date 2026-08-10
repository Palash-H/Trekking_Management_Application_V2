<template>
  <div class="table-container">
    <div v-if="loading" class="loading-state">Loading treks...</div>
    
    <table v-else class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Trek Name</th>
          <th>Location</th>
          <th>Date</th>
          <th>Slots</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trek in treks" :key="trek.id">
          <td>#{{ trek.id }}</td>
          <td class="font-bold">{{ trek.name }}</td>
          <td>{{ trek.location }}</td>
          
          <td>{{ formatDate(trek.start_date) }}</td>
          <td>{{ trek.available_slots }} / {{ trek.total_slots }}</td>
          
          <td>
            <span :class="['status-badge', (trek.status || 'Pending').toLowerCase()]">
              {{ trek.status || 'Pending' }}
            </span>
          </td>
          <td class="actions">
            
            <button class="btn-icon edit" @click="$emit('edit-trek', trek)">
              {{ ['Completed', 'Cancelled'].includes(trek.status) ? 'View' : 'Edit' }}
            </button>
          </td>
        </tr>
        <tr v-if="treks.length === 0">
          <td colspan="7" class="empty-state">No treks found in the database.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  treks: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: true
  }
});

defineEmits(['edit-trek']);

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};
</script>

<style scoped>
.table-container { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.loading-state, .empty-state { text-align: center; padding: 3rem; color: #64748b; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; }
.data-table th, .data-table td { padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0; }
.data-table th { background-color: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.data-table tr:hover { background-color: #f1f5f9; }
.font-bold { font-weight: 600; color: #0f172a; }

.status-badge { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; display: inline-block; }
.status-badge.active { background-color: #dcfce3; color: #166534; }
.status-badge.started { background-color: #dbeafe; color: #1e40af; } 
.status-badge.pending { background-color: #fef08a; color: #854d0e; }
.status-badge.completed { background-color: #e2e8f0; color: #475569; }
.status-badge.cancelled { background-color: #fee2e2; color: #991b1b; }

.btn-icon { background: none; border: none; font-weight: 600; cursor: pointer; padding: 0.5rem; }
.btn-icon.edit { color: #16a34a; }
.btn-icon.edit:hover { text-decoration: underline; }
</style>