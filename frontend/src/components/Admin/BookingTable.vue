<template>
  <div>
    <div v-if="loading" class="loading-state">Loading bookings...</div>
    
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Booking ID</th>
            <th>Trekker Name</th>
            <th>Trek Route</th>
            <th>Date Booked</th>
            <th>Participants</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="booking in bookings" :key="booking.id">
            <td>#{{ booking.id }}</td>
            <td class="font-medium">{{ booking.user_name }}</td>
            <td>{{ booking.trek_name }}</td>
            <td>{{ booking.booking_date }}</td>
            <td>{{ booking.participants }} Person(s)</td>
            <td>
              <span :class="['status-badge', booking.status.toLowerCase()]">
                {{ booking.status }}
              </span>
            </td>
          </tr>
          <tr v-if="bookings.length === 0">
            <td colspan="6" class="text-center empty-state">
              No bookings found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  bookings: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: true
  }
});
</script>

<style scoped>
.loading-state { text-align: center; color: #64748b; padding: 3rem; }
.empty-state { padding: 3rem; color: #64748b; text-align: center; }

.table-container {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
}
.data-table { width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; }
.data-table th, .data-table td { padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0; }
.data-table th { background-color: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
.data-table tbody tr:hover { background-color: #f8fafc; }
.data-table tbody tr:last-child td { border-bottom: none; }
.font-medium { font-weight: 600; color: #0f172a; }

/* Status Badges */
.status-badge {
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
.status-badge.confirmed { background-color: #dcfce3; color: #166534; }
.status-badge.pending { background-color: #fef3c7; color: #b45309; }
.status-badge.cancelled { background-color: #fee2e2; color: #b91c1c; }
</style>