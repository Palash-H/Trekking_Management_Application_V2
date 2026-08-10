<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-card">
      <div class="modal-header">
        <h2>Book: {{ trek.name }}</h2>
        <button class="btn-close" @click="handleClose">&times;</button>
      </div>
      
      <div class="modal-body">
        <p class="price-summary">Price per person: <strong>₹{{ trek.trek_fee }}</strong></p>
        
        <form @submit.prevent="handleSubmit">
          <div class="input-group">
            <label>How many slots do you need?</label>
            <input 
              type="number" 
              v-model="slotsRequested" 
              min="1" 
              :max="trek.available_slots" 
              required
            />
            <small>Max available: {{ trek.available_slots }}</small>
          </div>
          
          <div class="total-calc">
            Total Cost: ₹{{ totalCost }}
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="handleClose">Cancel</button>
            <button type="submit" class="btn btn-green" :disabled="isBooking">
              {{ isBooking ? 'Processing...' : 'Confirm Booking' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  trek: {
    type: Object,
    required: true
  },
  isBooking: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'submit-booking']);


const slotsRequested = ref(1);

const totalCost = computed(() => {
  return props.trek.trek_fee * slotsRequested.value;
});

const handleClose = () => {
  emit('close');
};

const handleSubmit = () => {
  
  emit('submit-booking', { slots_requested: slotsRequested.value });
};
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15,23,42,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
.modal-card { background: white; width: 100%; max-width: 400px; border-radius: 12px; overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; }
.modal-header h2 { font-size: 1.1rem; font-weight: 700; margin: 0; }
.btn-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; }
.modal-body { padding: 1.5rem; }
.price-summary { margin-bottom: 1.5rem; font-size: 1.1rem; color: #334155; }
.input-group { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.5rem; }
.input-group input { padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; outline: none; }
.input-group input:focus { border-color: #4f46e5; }
.total-calc { font-size: 1.25rem; font-weight: 700; color: #4f46e5; text-align: right; margin-bottom: 1.5rem; }
.modal-footer { display: flex; gap: 1rem; }
.btn { padding: 0.75rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: 0.2s; flex: 1; }
.btn-green { background: #16a34a; color: white; }
.btn-green:hover:not(:disabled) { background: #15803d; }
.btn-secondary { background: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1;}
</style>