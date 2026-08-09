<template>
  <div class="card">
    <div class="card-header">
      <h2>Participant Roster ({{ participants.length }})</h2>
    </div>
    
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Trekker Info</th>
            <th>Slots Booked</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in participants" :key="user.booking_id">
            <td>
              <div class="user-info">
                <strong :class="{ 'text-strike': user.booking_status === 'Cancelled' }">
                  {{ user.trekker_name }}
                </strong>
                <span class="user-email">{{ user.trekker_email }}</span>
              </div>
            </td>
            <td>{{ user.booked_slots }} Person(s)</td>
            
            <!-- ACTIONS COLUMN -->
            <td>
              <!-- Show Remove button ONLY if the trek is active or started -->
              <button 
                v-if="!isLocked" 
                class="btn-icon text-red" 
                @click="$emit('remove-participant', user)"
              > 
                Remove 
              </button>

              <!-- Show static text if the Trek is locked -->
              <span v-else class="text-muted" style="font-size: 0.85rem; font-style: italic;">Locked</span>
            </td>
          </tr>
          
          <tr v-if="participants.length === 0">
            <td colspan="3" class="empty-state">No trekkers have booked this trek yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  participants: {
    type: Array,
    required: true
  },
  dbTrekStatus: {
    type: String,
    required: true
  }
});

defineEmits(['remove-participant']);

const isLocked = computed(() => {
  return ['Completed', 'Cancelled'].includes(props.dbTrekStatus);
});
</script>

<style scoped>
/* Card Base */
.card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 1.25rem 1.5rem; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.card-header h2 { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; }

.empty-state { text-align: center; padding: 3rem; color: #64748b; }

/* Roster Table */
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; }
.data-table th, .data-table td { padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0; }
.data-table th { background-color: #ffffff; color: #64748b; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

.user-info { display: flex; flex-direction: column; gap: 0.25rem; }
.user-info strong { color: #0f172a; font-size: 0.95rem; }
.user-email { color: #64748b; font-size: 0.85rem; }
.text-strike { text-decoration: line-through; opacity: 0.6; }

/* Buttons */
.btn-icon { background: none; border: none; font-weight: 600; cursor: pointer; padding: 0.5rem; }
.text-red { color: #e11d48; }
.text-red:hover { text-decoration: underline; color: #be123c; }
.text-muted { color: #94a3b8; }
</style>