<template>
  <div class="booking-card" :class="{ 'is-cancelled': booking.booking_status === 'Cancelled' || booking.trek_status === 'Cancelled' }">
    
    <div class="card-header">
      <div class="header-content">
        <h3 class="trek-title">{{ booking.trek_name }}</h3>
        <p class="location">📍 {{ booking.location }}</p>
      </div>
      <div class="badges">
        <!-- Badge colors dynamically change based on status -->
        <span :class="['status-badge', booking.booking_status.toLowerCase()]">
          {{ booking.booking_status }}
        </span>
      </div>
    </div>
    
    <div class="card-body">
      <div class="info-row">
        <span class="label">Date:</span>
        <span class="value">{{ formattedDate }}</span>
      </div>
      <div class="info-row">
        <span class="label">Slots Booked:</span>
        <span class="value">{{ booking.booked_slots }} Person(s)</span>
      </div>
      <div class="info-row">
        <span class="label">Trek Status:</span>
        <span class="value">{{ booking.trek_status }}</span>
      </div>
    </div>

    <div class="card-footer">
      <!-- CANCEL BUTTON: Hide if Booking is Cancelled OR Trek is Completed/Cancelled -->
      <button 
        v-if="booking.booking_status !== 'Cancelled' && !['Completed', 'Cancelled'].includes(booking.trek_status)" 
        class="btn-cancel" 
        @click="handleCancel"
        :disabled="isCancelling === booking.booking_id"
      >
        {{ isCancelling === booking.booking_id ? 'Cancelling...' : 'Cancel Booking' }}
      </button>
      
      <!-- Admin Cancelled Message -->
      <span v-else-if="booking.trek_status === 'Cancelled'" class="text-alert">
        🚨 Trek Cancelled by Organizer
      </span>
      
      <!-- User Cancelled Message -->
      <span v-else-if="booking.booking_status === 'Cancelled'" class="text-muted">
        Booking Cancelled
      </span>
      
      <!-- Completed Message -->
      <span v-else class="text-muted">
        Trek Completed
      </span>
    </div>
    
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Accept data from the Parent Dashboard
const props = defineProps({
  booking: {
    type: Object,
    required: true
  },
  isCancelling: {
    type: Number,
    default: null
  }
});

// Define events to send back to the Parent
const emit = defineEmits(['cancel']);

// Trigger the cancel event
const handleCancel = () => {
  emit('cancel', props.booking.booking_id, props.booking.trek_name);
};

// Format the date specifically for this card
const formattedDate = computed(() => {
  const dateString = props.booking.start_date;
  if (!dateString || dateString === 'N/A') return 'TBD';
  return new Date(dateString).toLocaleDateString(undefined, { 
    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' 
  });
});
</script>

<style scoped>
/* Refined Card Styling */
.booking-card { 
  background: #ffffff; 
  border-radius: 12px; 
  border: 1px solid #e2e8f0; 
  overflow: hidden; 
  display: flex; 
  flex-direction: column; 
  transition: all 0.25s ease; 
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); 
  height: 100%; /* Ensures all cards in a grid row stretch evenly */
}
.booking-card:hover { 
  transform: translateY(-4px); 
  box-shadow: 0 12px 20px -3px rgba(0,0,0,0.08); 
}
.booking-card.is-cancelled { 
  opacity: 0.75; 
  background: #f8fafc; 
}

/* Header */
.card-header { 
  padding: 1.25rem; 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-start; 
  border-bottom: 1px solid #f1f5f9; 
  gap: 1rem;
}
.header-content { flex: 1; }
.trek-title { font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0 0 0.35rem 0; line-height: 1.3;}
.location { color: #64748b; font-size: 0.85rem; margin: 0; font-weight: 500;}

/* Badges */
.status-badge { 
  padding: 0.35rem 0.75rem; 
  border-radius: 999px; 
  font-size: 0.75rem; 
  font-weight: 700; 
  text-transform: uppercase; 
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.status-badge.confirmed, .status-badge.checked-in { background: #dcfce3; color: #166534; }
.status-badge.completed { background: #e2e8f0; color: #475569; }
.status-badge.pending { background: #fef08a; color: #854d0e; }
.status-badge.cancelled, .status-badge.no-show { background: #fee2e2; color: #991b1b; }

/* Body */
.card-body { 
  padding: 1.25rem; 
  display: flex; 
  flex-direction: column; 
  gap: 0.85rem; 
  flex: 1; 
}
.info-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.95rem; }
.info-row .label { color: #64748b; font-weight: 500; }
.info-row .value { color: #0f172a; font-weight: 600; text-align: right; }

/* Footer & Buttons */
.card-footer { 
  padding: 1rem 1.25rem; 
  background: #f8fafc; 
  border-top: 1px solid #f1f5f9; 
  display: flex; 
  justify-content: flex-end; 
  align-items: center; 
  min-height: 64px; /* Ensures footers align nicely */
}
.btn-cancel { 
  background: #ffffff; 
  color: #e11d48; 
  border: 1px solid #fecdd3; 
  padding: 0.5rem 1rem; 
  border-radius: 6px; 
  font-weight: 600; 
  font-size: 0.85rem; 
  cursor: pointer; 
  transition: all 0.2s ease; 
}
.btn-cancel:hover:not(:disabled) { background: #fff1f2; border-color: #fda4af; }
.btn-cancel:disabled { opacity: 0.5; cursor: not-allowed; }

.text-muted { color: #94a3b8; font-size: 0.85rem; font-weight: 500; font-style: italic; }
.text-alert { color: #e11d48; font-size: 0.85rem; font-weight: 600; }
</style>