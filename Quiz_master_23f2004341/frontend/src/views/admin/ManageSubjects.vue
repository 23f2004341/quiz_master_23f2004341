<template>
  <div class="container mt-4">
    <h2>Manage Subjects</h2>
    <form @submit.prevent="addSubject" class="mb-4">
      <div class="row">
        <div class="col-md-4">
          <input v-model="newSubject.name" class="form-control" placeholder="Subject Name" required />
        </div>
        <div class="col-md-6">
          <input v-model="newSubject.description" class="form-control" placeholder="Description" />
        </div>
        <div class="col-md-2">
          <button class="btn btn-success w-100" type="submit">Add</button>
        </div>
      </div>
    </form>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Description</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subject in subjects" :key="subject.id">
          <td>{{ subject.id }}</td>
          <td>
            <input v-model="subject.name" class="form-control" />
          </td>
          <td>
            <input v-model="subject.description" class="form-control" />
          </td>
          <td>
            <button class="btn btn-primary btn-sm" @click="updateSubject(subject)">Update</button>
            <button class="btn btn-danger btn-sm" @click="deleteSubject(subject.id)">Delete</button>
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
      subjects: [],
      newSubject: { name: '', description: '' },
      msg: ''
    };
  },
  async mounted() {
    await this.fetchSubjects();
  },
  methods: {
    async fetchSubjects() {
      const res = await axios.get('/api/subjects');
      this.subjects = res.data.subjects;
    },
    async addSubject() {
      await axios.post('/api/subjects', this.newSubject);
      this.msg = 'Subject added!';
      this.newSubject = { name: '', description: '' };
      await this.fetchSubjects();
    },
    async updateSubject(subject) {
      await axios.put(`/api/subjects/${subject.id}`, subject);
      this.msg = 'Subject updated!';
      await this.fetchSubjects();
    },
    async deleteSubject(id) {
      await axios.delete(`/api/subjects/${id}`);
      this.msg = 'Subject deleted!';
      await this.fetchSubjects();
    }
  }
};
</script>
