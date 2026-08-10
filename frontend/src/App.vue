<template>
  <router-view />
</template>
<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';


const router = useRouter();


const handleStorageChange = (event) => {
  
  if (event.key === 'token' && event.newValue === null) {
    
    
    alert("Logged out in another tab.");
    
    
    localStorage.removeItem('userRole');
    
    
    router.push('/login');
    
    
    setTimeout(() => window.location.reload(), 100);
  }
};

onMounted(() => {
  
  window.addEventListener('storage', handleStorageChange);
});

onUnmounted(() => {
  
  window.removeEventListener('storage', handleStorageChange);
});
</script>