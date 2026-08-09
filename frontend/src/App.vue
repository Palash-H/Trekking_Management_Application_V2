<template>
  <router-view />
</template>
<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
// import Navbar from './components/Navbar.vue'; // (Assuming you have this)

const router = useRouter();

// 🌟 Cross-Tab Sync Logic
const handleStorageChange = (event) => {
  // If the 'token' key was modified and is now null, it means a logout happened!
  if (event.key === 'token' && event.newValue === null) {
    
    // 1. Alert the user
    alert("Logged out in another tab.");
    
    // 2. Clear any lingering role data in this specific tab just to be safe
    localStorage.removeItem('userRole');
    
    // 3. Kick them back to the login screen instantly
    router.push('/login');
    
    // Optional: Force a small page reload to completely wipe the Vue memory state
    setTimeout(() => window.location.reload(), 100);
  }
};

onMounted(() => {
  // Start listening to other tabs the moment the app opens
  window.addEventListener('storage', handleStorageChange);
});

onUnmounted(() => {
  // Clean up the listener if the app unmounts
  window.removeEventListener('storage', handleStorageChange);
});
</script>