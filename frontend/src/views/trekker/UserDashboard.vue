<template>
  <div class="user-dashboard">
    <header class="page-header">
      <div>
        <h1>My Dashboard</h1>
        <p>Manage your upcoming adventures and view your trekking history.</p>
      </div>
      <router-link to="/trekker/explore" class="btn btn-primary">Find More Treks</router-link>
    </header>

    <div v-if="loading" class="loading-state">Loading your dashboard...</div>

    <div v-else>
      
      <div class="stats-grid">
        <div 
          class="stat-card" 
          :class="{ 'is-active': activeFilter === 'all' }" 
          @click="activeFilter = 'all'"
        >
          <h3>Total Bookings</h3>
          <p class="stat-number">{{ summary.total_bookings }}</p>
        </div>
        
        <div 
          class="stat-card highlight-indigo" 
          :class="{ 'is-active': activeFilter === 'upcoming' }" 
          @click="activeFilter = 'upcoming'"
        >
          <h3>Upcoming Treks</h3>
          <p class="stat-number">{{ summary.upcoming_treks }}</p>
        </div>
        
        <div 
          class="stat-card highlight-green" 
          :class="{ 'is-active': activeFilter === 'completed' }" 
          @click="activeFilter = 'completed'"
        >
          <h3>Completed</h3>
          <p class="stat-number">{{ summary.completed_treks }}</p>
        </div>
        
        <div 
          class="stat-card highlight-red" 
          :class="{ 'is-active': activeFilter === 'cancelled' }" 
          @click="activeFilter = 'cancelled'"
        >
          <h3>Cancelled</h3>
          <p class="stat-number">{{ summary.cancelled_bookings }}</p>
        </div>
      </div>

      <!-- Dynamic Title based on filter -->
      <div class="section-divider">
        <h2>{{ filterTitle }}</h2>
      </div>


      <div v-if="filteredBookings.length === 0" class="empty-state">
        <h3 v-if="activeFilter === 'all'">No Bookings Yet</h3>
        <h3 v-else>No {{ activeFilter }} bookings found</h3>
        
        <p v-if="activeFilter === 'all'">You haven't booked any treks. Click "Find More Treks" to get started!</p>
        <p v-else>You don't have any treks in this category at the moment.</p>
        
        <button v-if="activeFilter !== 'all'" class="btn-text mt-3" @click="activeFilter = 'all'">
          Clear Filter
        </button>
      </div>


      <div v-else class="bookings-grid">
       
        <BookingCard 
          v-for="booking in filteredBookings" 
          :key="booking.booking_id"
          :booking="booking"
          :isCancelling="isCancelling"
          @cancel="cancelBooking"
        />
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

import BookingCard from '@/components/User/BookingCard.vue'; 

const loading = ref(true);
const isCancelling = ref(null); 

const summary = ref({
  total_bookings: 0,
  upcoming_treks: 0,
  completed_treks: 0,
  cancelled_bookings: 0
});

const bookings = ref([]);
const activeFilter = ref('all');

// Core filtering logic for the tabs
const filteredBookings = computed(() => {
  if (activeFilter.value === 'upcoming') {
    return bookings.value.filter(b => 
      b.booking_status !== 'Cancelled' && 
      ['Active', 'Open', 'Started'].includes(b.trek_status)
    );
  } 
  if (activeFilter.value === 'completed') {
    return bookings.value.filter(b => b.booking_status !== 'Cancelled' && b.trek_status === 'Completed');
  } 
  if (activeFilter.value === 'cancelled') {
    
    return bookings.value.filter(b => 
      b.booking_status === 'Cancelled' || 
      b.trek_status === 'Cancelled'
    );
  }
  return bookings.value;
});

const filterTitle = computed(() => {
  if (activeFilter.value === 'upcoming') return 'Upcoming Treks';
  if (activeFilter.value === 'completed') return 'Completed Treks';
  if (activeFilter.value === 'cancelled') return 'Cancelled Bookings';
  return 'All Bookings';
});

// Fetch all data for the dashboard
const fetchDashboardData = async () => {
  try {
    const [summaryRes, bookingsRes] = await Promise.all([
      axios.get('/api/user/dashboard/summary'),
      axios.get('/api/user/bookings')
    ]);

    summary.value = summaryRes.data;
    

    bookings.value = bookingsRes.data.history.sort((a, b) => {
      if (a.booking_status === 'Confirmed' && b.booking_status === 'Cancelled') return -1;
      if (a.booking_status === 'Cancelled' && b.booking_status === 'Confirmed') return 1;
      return 0;
    });

  } catch (error) {
    console.error("Failed to fetch dashboard data:", error);
    if (error.response?.status === 403) {
      alert("Unauthorized access.");
    }
  } finally {
    loading.value = false;
  }
};


const cancelBooking = async (bookingId, trekName) => {
  if (!confirm(`Are you sure you want to cancel your booking for ${trekName}?`)) {
    return;
  }

  isCancelling.value = bookingId;
  try {
    const response = await axios.post(`/api/bookings/${bookingId}/cancel`);
    alert(response.data.msg);
    
    await fetchDashboardData();

    activeFilter.value = 'cancelled';
  } catch (error) {
    console.error("Failed to cancel booking:", error);
    alert(error.response?.data?.msg || "Failed to cancel booking.");
  } finally {
    isCancelling.value = null;
  }
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<style scoped>

.user-dashboard { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }

/* Header Layout */
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;}
.page-header h1 { font-size: 2.25rem; color: #0f172a; font-weight: 700; margin-bottom: 0.25rem; }
.page-header p { color: #64748b; font-size: 1.1rem; }
.btn-primary { background: #4f46e5; color: white; padding: 0.6rem 1.25rem; border-radius: 8px; text-decoration: none; font-weight: 600; transition: 0.2s; }
.btn-primary:hover { background: #4338ca; }

/* Empty & Loading States */
.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; background: #f8fafc; border-radius: 12px; border: 2px dashed #cbd5e1; }
.empty-state h3 { font-size: 1.35rem; color: #0f172a; margin-bottom: 0.5rem; text-transform: capitalize; font-weight: 700;}
.btn-text { background: none; border: none; color: #4f46e5; font-weight: 600; cursor: pointer; padding: 0.5rem; transition: 0.2s;}
.btn-text:hover { text-decoration: underline; color: #4338ca;}
.mt-3 { margin-top: 1rem; }

/* Stats Grid & Filters */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
.stat-card { 
  background: #ffffff; padding: 1.5rem; border-radius: 12px; 
  border: 2px solid transparent; 
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); 
  cursor: pointer; 
  transition: all 0.2s ease; 
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
.stat-card h3 { font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;}
.stat-number { font-size: 2.25rem; font-weight: 800; color: #0f172a; }

/* Active States */
.stat-card.is-active { border-color: #94a3b8; background: #f8fafc; }
.highlight-indigo .stat-number { color: #4f46e5; }
.highlight-indigo.is-active { border-color: #4f46e5; background: #eef2ff; }
.highlight-green .stat-number { color: #16a34a; }
.highlight-green.is-active { border-color: #16a34a; background: #f0fdf4; }
.highlight-red .stat-number { color: #e11d48; }
.highlight-red.is-active { border-color: #e11d48; background: #fff1f2; }

/* List Separator */
.section-divider { margin-bottom: 1.5rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.75rem; }
.section-divider h2 { font-size: 1.5rem; color: #0f172a; font-weight: 700; transition: color 0.3s; }


.bookings-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); 
  gap: 1.5rem; 
  align-items: stretch; 
}
</style>