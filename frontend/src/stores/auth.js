import { defineStore } from 'pinia';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Force Axios to hit your specific Flask port
axios.defaults.baseURL = 'http://127.0.0.1:5050';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.role === 'admin',
    isStaff: (state) => state.role === 'trekstaff',
    isTrekker: (state) => state.role === 'trekker'
  },
  
  actions: {
    initAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      }
    },

    async login(email, password) {
      try {
        const response = await axios.post('/api/login', { email, password });
        this.token = response.data.token || response.data.access_token;
        this.role = jwtDecode(this.token).role;
        
        localStorage.setItem('token', this.token);
        localStorage.setItem('role', this.role);
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
        
        return { success: true };
      } catch (error) {
        return { success: false, msg: error.response?.data?.msg || "Invalid credentials." };
      }
    },

    async register(name, email, contact, password) {
      try {
        const response = await axios.post('/api/register', { name, email, contact, password });
        return { success: true, msg: response.data.msg };
      } catch (error) {
        return { success: false, msg: error.response?.data?.msg || "Registration failed." };
      }
    },

    logout() {
      this.token = null;
      this.role = null;
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      delete axios.defaults.headers.common['Authorization'];
    }
  }
});