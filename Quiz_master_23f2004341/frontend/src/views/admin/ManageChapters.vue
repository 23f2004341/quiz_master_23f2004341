<template>
  <div class="container mt-4">
    <h2>Manage Chapters</h2>
    <form @submit.prevent="addChapter" class="mb-4">
      <div class="row">
        <div class="col-md-3">
          <input v-model="newChapter.name" class="form-control" placeholder="Chapter Name" required />
        </div>
        <div class="col-md-5">
          <input v-model="newChapter.description" class="form-control" placeholder="Description" />
        </div>
        <div class="col-md-2">
          <select v-model="newChapter.subject_id" class="form-control" required>
            <option disabled value="">Select Subject</option>
            <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
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
          <th>Subject</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="chapter in chapters" :key="chapter.id">
          <td>{{ chapter.id }}</td>
          <td><input v-model="chapter.name" class="form-control" /></td>
          <td><input v-model="chapter.description" class="form-control" /></td>
          <td>
            <select v-model="chapter.subject_id" class="form-control">
              <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </td>
          <td>
            <button class="btn btn-primary btn-sm" @click="updateChapter(chapter)">Update</button>
            <button class="btn btn-danger btn-sm" @click="deleteChapter(chapter.id)">Delete</button>
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
      chapters: [],
      subjects: [],
      newChapter: { name: '', description: '', subject_id: '' },
      msg: ''
    };
  },
  async mounted() {
    await this.fetchChapters();
    await this.fetchSubjects();
  },
  methods: {
    async fetchChapters() {
      const res = await axios.get('/api/chapters');
      this.chapters = res.data.chapters;
    },
    async fetchSubjects() {
      const res = await axios.get('/api/subjects');
      this.subjects = res.data.subjects;
    },
    async addChapter() {
      await axios.post('/api/chapters', this.newChapter);
      this.msg = 'Chapter added!';
      this.newChapter = { name: '', description: '', subject_id: '' };
      await this.fetchChapters();
    },
    async updateChapter(chapter) {
      await axios.put(`/api/chapters/${chapter.id}`, chapter);
      this.msg = 'Chapter updated!';
      await this.fetchChapters();
    },
    async deleteChapter(id) {
      await axios.delete(`/api/chapters/${id}`);
      this.msg = 'Chapter deleted!';
      await this.fetchChapters();
    }
  }
};
</script>
