<template>
  <div class="container mt-4">
    <h2>Search Analytics</h2>
    <form @submit.prevent="search" class="mb-4">
      <div class="row">
        <div class="col-md-4">
          <input v-model="query" class="form-control" placeholder="Search users, quizzes, subjects..." />
        </div>
        <div class="col-md-2">
          <button class="btn btn-primary w-100" type="submit">Search</button>
        </div>
      </div>
    </form>
    <div v-if="results.length">
      <h5>Results:</h5>
      <ul class="list-group">
        <li v-for="r in results" :key="r.id" class="list-group-item">
          <span v-if="r.type === 'user'">User: {{ r.username }} ({{ r.email }})</span>
          <span v-else-if="r.type === 'quiz'">Quiz: {{ r.title }}</span>
          <span v-else-if="r.type === 'subject'">Subject: {{ r.name }}</span>
        </li>
      </ul>
    </div>
    <div v-if="msg" class="alert alert-info mt-2">{{ msg }}</div>
  </div>
</template>
<script>
import axios from 'axios';
export default {
  data() {
    return {
      query: '',
      results: [],
      msg: ''
    };
  },
  methods: {
    async search() {
      if (!this.query) return;
      const res = await axios.post('/api/admin/search', { term: this.query });
      // Flatten results for display
      this.results = [];
      const data = res.data.results;
      if (data.users) this.results.push(...data.users.map(u => ({ type: 'user', ...u })));
      if (data.quizzes) this.results.push(...data.quizzes.map(q => ({ type: 'quiz', ...q })));
      if (data.subjects) this.results.push(...data.subjects.map(s => ({ type: 'subject', ...s })));
      if (data.chapters) this.results.push(...data.chapters.map(c => ({ type: 'chapter', ...c })));
      if (data.questions) this.results.push(...data.questions.map(q => ({ type: 'question', ...q })));
      this.msg = this.results.length ? '' : 'No results found.';
    }
  }
};
</script>
