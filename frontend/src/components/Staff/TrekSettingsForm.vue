<template>
  <div class="card">
    <div class="card-header">
      <h2>Trek Settings</h2>
    </div>
    
    <form @submit.prevent="handleSubmit" class="settings-form">
      
      <div class="input-group">
        <label>Update Trek Status</label>
        <select v-model="localSettings.status" class="form-select" :disabled="isLocked">
          <option value="Active">Active</option>
          <option value="Started">Started</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </div>

      <div class="input-group">
        <label>Add Extra Slots (Optional)</label>
        <input 
          type="number" 
          v-model="localSettings.add_slots" 
          min="0" 
          placeholder="0" 
          class="form-input" 
          :disabled="isLocked"
        />
        <small class="help-text">Only use this if you need to increase capacity.</small>
      </div>

      <button type="submit" class="btn btn-primary" :disabled="isUpdatingSettings || isLocked">
        {{ isLocked ? 'Trek Locked' : (isUpdatingSettings ? 'Saving...' : 'Save Settings') }} 
      </button>
      
    </form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  dbTrekStatus: {
    type: String,
    required: true
  },
  isUpdatingSettings: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update-settings']);

const localSettings = ref({
  status: 'Open',
  add_slots: 0
});

// Lock the form if the trek is completed or cancelled
const isLocked = computed(() => {
  return ['Completed', 'Cancelled'].includes(props.dbTrekStatus);
});

// Watch the actual DB status from the parent to set the dropdown initially
watch(() => props.dbTrekStatus, (newVal) => {
  if (newVal) localSettings.value.status = newVal;
}, { immediate: true });

const handleSubmit = () => {
  // Emit the data up to the parent
  emit('update-settings', {
    status: localSettings.value.status,
    add_slots: localSettings.value.add_slots
  });
  
  // Reset the slots input back to 0 locally after emitting
  localSettings.value.add_slots = 0;
};
</script>

<style scoped>
/* Card Base */
.card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); overflow: hidden; height: 100%;}
.card-header { padding: 1.25rem 1.5rem; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.card-header h2 { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; }

/* Settings Form */
.settings-form { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.input-group label { font-size: 0.85rem; font-weight: 600; color: #475569; }
.form-select, .form-input { padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; width: 100%; outline: none; }
.form-select:focus, .form-input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
.form-select:disabled, .form-input:disabled { background: #f8fafc; color: #94a3b8; cursor: not-allowed; }
.help-text { font-size: 0.75rem; color: #64748b; }

/* Buttons */
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; border: none; transition: 0.2s; }
.btn-primary { background-color: #4f46e5; color: white; width: 100%; }
.btn-primary:hover:not(:disabled) { background-color: #4338ca; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
</style>