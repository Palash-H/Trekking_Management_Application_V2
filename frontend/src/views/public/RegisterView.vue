<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>Join TrekApp</h2>
      <p class="subtitle">Start your trekking journey today.</p>

      <div v-if="msg" :class="['alert', isSuccess ? 'alert-success' : 'alert-error']">
        {{ msg }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="input-group">
          <label>Full Name</label>
          <input type="text" v-model="name" required placeholder="John Doe" />
        </div>
        <div class="input-group">
          <label>Email</label>
          <input type="email" v-model="email" required placeholder="name@example.com" />
        </div>
        <div class="input-group">
          <label>Contact Number</label>
          <input type="text" v-model="contact" required placeholder="10-digit number" />
        </div>
        <div class="input-group">
          <label>Password</label>
          <input type="password" v-model="password" required placeholder="Create a password" />
        </div>
        <button type="submit" class="btn btn-primary full-width" :disabled="loading">
          {{ loading ? 'Creating Account...' : 'Sign Up' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const name = ref('')
const email = ref('')
const contact = ref('')
const password = ref('')
const msg = ref('')
const isSuccess = ref(false)
const loading = ref(false)

const authStore = useAuthStore()
const router = useRouter()

const handleRegister = async () => {
  loading.value = true
  msg.value = ''
  const res = await authStore.register(name.value, email.value, contact.value, password.value)

  if (res.success) {
    isSuccess.value = true
    msg.value = 'Success! Redirecting to login...'
    setTimeout(() => router.push('/login'), 2000)
  } else {
    isSuccess.value = false
    msg.value = res.msg
  }
  loading.value = false
}
</script>
