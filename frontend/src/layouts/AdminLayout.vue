<template>
  <Navbar/>
  <div class="admin-wrapper">
    <!-- Sidebar -->
    <aside class="sidebar">
      <!-- <div class="sidebar-header">
        <h2>🏔️ TrekAdmin</h2>
      </div> -->
      <nav class="sidebar-nav">
        <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/admin/reports" class="nav-link"> Reports & Analytics </router-link>
        <router-link to="/admin/treks" class="nav-link">Manage Treks</router-link>
        <router-link to="/admin/users" class="nav-link">Manage Users</router-link>
        <router-link to="/admin/bookings" class="nav-link">Manage Bookings</router-link>
        <button @click="handleLogout" class="nav-link btn-logout">Log Out</button>
      </nav>
    </aside>
    

    <!-- Main Content Area -->
    <main class="admin-content">
      <router-view /> <!-- This is where the Admin Dashboard will render! -->
    </main>
  </div>
  <Footer/>
</template>

<script setup>
import Navbar from '@/components/navigation/NavBar.vue'
import Footer from '@/components/navigation/Footer.vue'
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.admin-wrapper {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-color);
}

.sidebar {
  width: 260px;
  background-color: #1e293b; /* Dark slate */
  color: white;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #334155;
  text-align: center;
}

.sidebar-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.sidebar-nav {
  padding: 1.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-link {
  padding: 0.8rem 1.5rem;
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 500;
  transition: 0.2s;
  background: transparent;
  border: none;
  text-align: left;
  font-size: 1rem;
  cursor: pointer;
}

.nav-link:hover, .router-link-active {
  background-color: #334155;
  color: white;
  border-left: 4px solid var(--primary);
}

.btn-logout {
  margin-top: auto;
  color: #f87171;
}
.btn-logout:hover {
  background-color: rgba(248, 113, 113, 0.1);
  border-left: 4px solid #f87171;
}

.admin-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}
</style>