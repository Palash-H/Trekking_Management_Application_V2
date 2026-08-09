<template>
  <div class="trek-card" :class="{'sold-out-card': trek.is_sold_out}">
    <div class="card-header">
      <span :class="['difficulty-badge', (trek.difficulty || 'moderate').toLowerCase()]">{{ trek.difficulty }}</span>
      <span class="price">₹{{ trek.trek_fee }}</span>
    </div>
    
    <div class="card-body">
      <h2>{{ trek.name }}</h2>
      <p class="location">📍 {{ trek.location }}</p>
      <p class="desc">{{ trek.desc ? trek.desc.substring(0, 80) + '...' : 'No description available.' }}</p>
      
      <div class="trek-meta">
        <span>🗓️ {{ formattedDate }}</span>
        <span>⏱️ {{ trek.time_duration }} Days</span>
        <span :class="{'text-danger': trek.available_slots <= 5 && !trek.is_sold_out}">
          👥 {{ trek.is_sold_out ? 'Sold Out' : `${trek.available_slots} slots left` }}
        </span>
      </div>
    </div>
    
    <div class="card-footer">
      <button 
        class="btn btn-primary" 
        @click="handleBookClick" 
        :disabled="isBooked || trek.is_sold_out"
        :class="{'btn-booked': isBooked}">
        {{ isBooked ? '✓ Booked' : (trek.is_sold_out ? 'Sold Out' : 'Book Now') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// 1. Receive data from the parent
const props = defineProps({
  trek: {
    type: Object,
    required: true
  },
  isBooked: {
    type: Boolean,
    default: false
  }
});

// 2. Define the event to send back to the parent
const emit = defineEmits(['book']);

// 3. Emit the event with the selected trek data
const handleBookClick = () => {
  emit('book', props.trek);
};

// 4. Local formatting logic
const formattedDate = computed(() => {
  const dateString = props.trek.start_date;
  if (!dateString || dateString === 'N/A') return 'N/A';
  return new Date(dateString).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
});
</script>

<style scoped>
.trek-card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; height: 100%; }
.trek-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
.sold-out-card { opacity: 0.8; }

.card-header { padding: 1.25rem 1.5rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; background: #f8fafc; }
.price { font-weight: 700; color: #0f172a; font-size: 1.1rem; }

.difficulty-badge { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
.difficulty-badge.easy { background: #dcfce3; color: #166534; }
.difficulty-badge.moderate { background: #fef08a; color: #854d0e; }
.difficulty-badge.hard { background: #fee2e2; color: #991b1b; }

.card-body { padding: 1.5rem; flex: 1; }
.card-body h2 { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
.location { color: #64748b; font-size: 0.9rem; margin-bottom: 1rem; }
.desc { color: #475569; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem; }

.trek-meta { display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.85rem; color: #334155; font-weight: 500; }
.text-danger { color: #e11d48; } 

.card-footer { padding: 1.5rem; border-top: 1px solid #f1f5f9; }
.btn { width: 100%; padding: 0.75rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: 0.2s; }
.btn-primary { background: #4f46e5; color: white; }
.btn-primary:hover:not(:disabled) { background: #4338ca; }
.btn-primary:disabled { background: #94a3b8; cursor: not-allowed; }

.btn-booked {
  background-color: #f1f5f9 !important;
  color: #16a34a !important; 
  border: 1px solid #16a34a !important;
  opacity: 1 !important; 
  cursor: default !important;
}
</style>