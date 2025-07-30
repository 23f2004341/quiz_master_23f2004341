<template>
  <div class="container mt-5">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label>Email</label>
        <input v-model="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <div class="mb-3">
        <label>Full Name</label>
        <input v-model="full_name" type="text" class="form-control" required />
      </div>
      <div class="mb-3">
        <label>Qualification</label>
        <input v-model="qualification" type="text" class="form-control" />
      </div>
      <div class="mb-3">
        <label>Date of Birth</label>
        <input v-model="dob" type="date" class="form-control" />
      </div>
      <button class="btn btn-primary" type="submit">Register</button>
      <router-link to="/login" class="btn btn-link">Login</router-link>
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
      full_name: '',
      qualification: '',
      dob: '',
      error: ''
    };
  },
  methods: {
    async register() {
      try {
        await axios.post('/api/register', {
          email: this.email,
          password: this.password,
          full_name: this.full_name,
          qualification: this.qualification,
          dob: this.dob
        });
        this.$router.push('/login');
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed';
      }
    }
  }
};
</script>
