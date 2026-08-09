<template>
  <div class="form-container">
    <form @submit.prevent="handleSubmit" class="trek-form">
      <div class="form-grid">
        <!-- Left Column -->
        <div class="input-group">
          <label>Trek Name</label>
          <input type="text" v-model="localForm.name" required placeholder="e.g. Rajmachi Fort" />
        </div>

        <div class="input-group">
          <label>Location</label>
          <input type="text" v-model="localForm.location" required placeholder="e.g. Lonavala, Maharashtra" />
        </div>

        <div class="input-group">
          <label>Difficulty</label>
          <select v-model="localForm.difficulty" required class="custom-select">
            <option value="Easy">Easy</option>
            <option value="Moderate">Moderate</option>
            <option value="Hard">Hard</option>
          </select>
        </div>

        <div class="input-group">
          <label>Trek Fee (₹)</label>
          <input type="number" v-model="localForm.fee" required min="0" placeholder="800" />
        </div>

        <!-- Right Column -->
        <div class="input-group">
          <label>Start Date</label>
          <input type="date" v-model="localForm.date" :min="today" required />
        </div>

        <div class="input-group">
          <label>Total Slots</label>
          <input type="number" v-model="localForm.slots" required min="1" placeholder="30" />
        </div>

        <div class="input-group">
          <label>Duration (Days)</label>
          <input type="number" v-model="localForm.time" required min="1" placeholder="2" />
        </div>
        
        <div class="input-group">
          <label>Assigned Staff</label>
          <select v-model="localForm.staff_id" required class="custom-select">
            <option value="" disabled>Select a Staff Member...</option>
            <option v-for="staff in staffList" :key="staff.id" :value="staff.id">
              {{ staff.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Full Width -->
      <div class="input-group full-width">
        <label>Description</label>
        <textarea v-model="localForm.desc" required rows="4" placeholder="Describe the trek experience..."></textarea>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-outline-dark" @click="$emit('cancel')">Cancel</button>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Creating...' : 'Create Trek' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  staffList: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  today: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['submit-form', 'cancel']);

// Local state for the form inputs
const localForm = ref({
  name: '',
  location: '',
  difficulty: 'Moderate',
  fee: '',
  date: '',
  slots: '',
  time: '',
  staff_id: '',
  desc: ''
});

const handleSubmit = () => {
  emit('submit-form', { ...localForm.value });
};
</script>

<style scoped>
.form-container {
  background: var(--card-bg, #ffffff); 
  padding: 2rem; 
  border-radius: 12px; 
  border: 1px solid var(--border, #e2e8f0); 
  box-shadow: 0 4px 6px rgba(0,0,0,0.02); 
  max-width: 900px;
}

.trek-form { display: flex; flex-direction: column; gap: 1.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }

.input-group label { display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-main, #0f172a); }
.input-group input, .input-group textarea, .custom-select {
  width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border, #cbd5e1); border-radius: 8px; font-size: 1rem;
}
.input-group input:focus, .input-group textarea:focus, .custom-select:focus {
  outline: none; border-color: var(--primary, #16a34a); box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
}
.full-width { grid-column: span 2; }
.custom-select { background-color: white; cursor: pointer; }

.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem; border-top: 1px solid var(--border, #e2e8f0); padding-top: 1.5rem; }

.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn-primary { background-color: #16a34a; color: white; box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.2); }
.btn-primary:hover:not(:disabled) { background-color: #15803d; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-outline-dark { background: transparent; border: 1px solid var(--border, #cbd5e1); color: var(--text-main, #0f172a); }
.btn-outline-dark:hover { background: #f1f5f9; }

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .full-width { grid-column: span 1; }
}
</style>