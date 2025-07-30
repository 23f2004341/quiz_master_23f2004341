<template>
  <div class="container mt-5">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div class="mb-3">
        <label>Email</label>
        <input v-model="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <button class="btn btn-primary" type="submit">Login</button>
      <router-link to="/register" class="btn btn-link">Register</router-link>
      <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
    </form>
  </div>
</template>
<script>
import axios from 'axios';
export default {
  data() {
    return {
      email: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async login() {
      try {
        const res = await axios.post('/api/login', { email: this.email, password: this.password });
        const user = res.data.user;
        localStorage.setItem('role', user.role);
        if (user.role === 'admin') {
          this.$router.push('/admin/dashboard');
        } else {
          this.$router.push('/user/dashboard');
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed';
      }
    }
  }
};
</script>
