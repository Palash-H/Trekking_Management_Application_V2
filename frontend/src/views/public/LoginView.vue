<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>Welcome Back</h2>
      <p class="subtitle">Enter your details to access your account.</p>

      <div v-if="errorMsg" class="alert alert-error">{{ errorMsg }}</div>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label>Email</label>
          <input type="email" v-model="email" required placeholder="name@example.com" />
        </div>
        <div class="input-group">
          <label>Password</label>
          <input type="password" v-model="password" required placeholder="••••••••" />
        </div>
        <button type="submit" class="btn btn-primary full-width" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Log In' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  loading.value = true; errorMsg.value = '';
  const res = await authStore.login(email.value, password.value);
  
  if (res.success) {
    // Check role and push to appropriate dashboard!
    if (authStore.isAdmin) {
      router.push('/admin/dashboard');
    } else if (authStore.isStaff) {
      router.push('/staff/dashboard'); // We will build this later
    } else {
      router.push('/trekker/explore'); // We will build this later
    }
  } else {
    errorMsg.value = res.msg;
  }
  loading.value = false;
};
</script>

<style>
/* Shared Auth CSS */
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem 1rem;
}
.auth-card {
  background: var(--card-bg);
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 420px;
  border: 1px solid var(--border);
}
.auth-card h2 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  color: var(--text-main);
  text-align: center;
}
.subtitle {
  color: var(--text-muted);
  text-align: center;
  margin-bottom: 2rem;
}
.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
}
.alert-error {
  background: #fee2e2;
  color: #991b1b;
}
.alert-success {
  background: #dcfce3;
  color: #166534;
}
</style>
