<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <h2>{{ isTrekLocked ? 'View Trek:' : 'Edit Trek:' }} {{ localForm.name }}</h2>
        <button class="btn-close" @click="$emit('close')">&times;</button>
      </div>
      
      <form @submit.prevent="handleSave">
        <div class="modal-body form-layout">
          
          <!-- WARNING BANNER IF LOCKED -->
          <div v-if="isTrekLocked" class="alert-warning">
            This trek is <strong>{{ originalStatus }}</strong>. It is locked and cannot be modified or deleted.
          </div>

          <div class="input-group">
            <label>Trek Name</label>
            <input type="text" v-model="localForm.name" required :disabled="isTrekLocked" />
          </div>
          
          <div class="input-group">
            <label>Description</label>
            <textarea v-model="localForm.desc" rows="3" :disabled="isTrekLocked"></textarea>
          </div>
          
          <div class="input-group">
            <label>Assigned Trek Staff</label>
            <select v-model="localForm.staff_id" class="form-select" :disabled="isTrekLocked">
              <option value="" disabled>-- Select a Staff Member --</option>
              <option 
                v-for="staff in staffMembers" 
                :key="staff.id" 
                :value="staff.id">
                {{ staff.name }} ({{ staff.email }})
              </option>
            </select>
          </div>

          <div class="form-row">
            <div class="input-group">
              <label>Start Date</label>
              <input type="date" v-model="localForm.start_date" required :min="today" :disabled="isTrekLocked" />
            </div>
            <div class="input-group">
              <label>Duration (Days)</label>
              <input type="number" v-model="localForm.time_duration" required min="1" :disabled="isTrekLocked" />
            </div>
            <div class="input-group">
              <label>Trek Fee (₹)</label>
              <input type="number" v-model="localForm.trek_fee" required min="0" :disabled="isTrekLocked" />
            </div>
          </div>

          <div class="form-row">
            <div class="input-group">
              <label>Difficulty</label>
              <select v-model="localForm.difficulty" class="form-select" :disabled="isTrekLocked">
                <option value="Easy">Easy</option>
                <option value="Moderate">Moderate</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
            
            <div class="input-group">
              <label>Status</label>
              <select v-model="localForm.status" class="form-select" :disabled="isTrekLocked">
                <option value="Active">Active</option>
                <option value="Started">Started</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer modal-footer-split">
          <!-- Delete Button (Disabled if Locked) -->
          <button 
            type="button" 
            class="btn btn-danger" 
            @click="$emit('delete', localForm)" 
            :disabled="isUpdating || isDeleting || isTrekLocked">
            {{ isDeleting ? 'Deleting...' : 'Delete Trek' }}
          </button>
          
          <!-- Cancel / Save Buttons (Disabled if Locked) -->
          <div class="footer-actions">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">Close</button>
            <button 
              type="submit" 
              class="btn btn-green" 
              :disabled="isUpdating || isDeleting || isTrekLocked">
              {{ isUpdating ? 'Saving...' : (isTrekLocked ? 'Locked' : 'Save Changes') }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  show: Boolean,
  trek: Object,
  staffMembers: Array,
  isUpdating: Boolean,
  isDeleting: Boolean
});

const emit = defineEmits(['close', 'save', 'delete']);

const localForm = ref({});
const originalStatus = ref('');

// Compute today's date for the :min attribute
const today = computed(() => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
});

// Check the ORIGINAL status, not the live form status
const isTrekLocked = computed(() => {
  return ['Completed', 'Cancelled'].includes(originalStatus.value);
});

// Watch for the modal opening and pre-fill the form cleanly
watch(() => props.trek, (newTrek) => {
  if (newTrek) {
    localForm.value = { ...newTrek };
    originalStatus.value = newTrek.status || 'Pending';

    // Format the date for the HTML input
    if (localForm.value.start_date) {
      const d = new Date(localForm.value.start_date);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      localForm.value.start_date = `${year}-${month}-${day}`;
    }
    
    // Ensure aliases map correctly
    localForm.value.time_duration = newTrek.time_duration || newTrek.duration || 1;
    localForm.value.staff_id = newTrek.assigned_staff || newTrek.staff_id || '';
  }
}, { immediate: true });

const handleSave = () => {
  if (isTrekLocked.value) return; 
  emit('save', localForm.value);
};
</script>

<style scoped>
/* NOTE: Removed backdrop-filter to prevent flickering! */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.65); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.15s ease-out;}
.modal-card { background: #ffffff; width: 100%; max-width: 550px; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);}
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; border-bottom: 1px solid #e2e8f0; }
.modal-header h2 { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; }
.btn-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b; transition: 0.2s;}
.btn-close:hover { color: #0f172a; }
.modal-body { padding: 1.5rem; }

.alert-warning { background-color: #fffbeb; color: #b45309; border: 1px solid #fde68a; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 0.9rem; }

.form-layout { display: flex; flex-direction: column; gap: 1.25rem; }
.form-row { display: flex; gap: 1rem; }
.form-row .input-group { flex: 1; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.input-group label { font-size: 0.85rem; font-weight: 600; color: #475569; }
.input-group input, .form-select, textarea { padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; width: 100%; font-family: inherit; }
.input-group input:focus, .form-select:focus, textarea:focus { outline: none; border-color: #16a34a; box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1); }
.input-group input:disabled, .form-select:disabled, textarea:disabled { background-color: #f8fafc; color: #94a3b8; cursor: not-allowed; border-color: #e2e8f0; }
textarea { resize: vertical; }

.modal-footer { padding: 1.25rem 1.5rem; background: #f8fafc; border-top: 1px solid #e2e8f0; }
.modal-footer-split { display: flex; justify-content: space-between; align-items: center; }
.footer-actions { display: flex; gap: 1rem; }

.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; border: none; text-decoration: none; }
.btn-green { background-color: #16a34a; color: white; box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.2); }
.btn-green:hover:not(:disabled) { background-color: #15803d; transform: translateY(-1px); }
.btn-secondary { background-color: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; }
.btn-secondary:hover { background-color: #f1f5f9; }
.btn-danger { background-color: #ef4444; color: white; }
.btn-danger:hover:not(:disabled) { background-color: #dc2626; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(15px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
</style>