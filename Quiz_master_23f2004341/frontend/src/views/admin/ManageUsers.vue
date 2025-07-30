<template>
  <div class="container mt-4">
    <h2>Manage Users</h2>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Full Name</th>
          <th>Email</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td><input v-model="user.full_name" class="form-control" /></td>
          <td><input v-model="user.email" class="form-control" /></td>
          <td>
            <select v-model="user.is_active" class="form-control">
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </td>
          <td>
            <button class="btn btn-primary btn-sm" @click="updateUser(user)">Update</button>
            <button class="btn btn-danger btn-sm" @click="deleteUser(user.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="msg" class="alert alert-info mt-2">{{ msg }}</div>
  </div>
</template>
<script>
import axios from 'axios';
export default {
  data() {
    return {
      users: [],
      msg: ''
    };
  },
  async mounted() {
    await this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      const res = await axios.get('/api/users');
      this.users = res.data.users;
    },
    async updateUser(user) {
      await axios.put(`/api/users/${user.id}`, user);
      this.msg = 'User updated!';
      await this.fetchUsers();
    },
    async deleteUser(id) {
      await axios.delete(`/api/users/${id}`);
      this.msg = 'User deleted!';
      await this.fetchUsers();
    }
  }
};
</script>
