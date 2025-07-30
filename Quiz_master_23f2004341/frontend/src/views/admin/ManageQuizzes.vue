<template>
  <div class="container mt-4">
    <h2>Manage Quizzes</h2>
    <form @submit.prevent="addQuiz" class="mb-4">
      <div class="row">
        <div class="col-md-3">
          <select v-model="newQuiz.chapter_id" class="form-control" required>
            <option disabled value="">Select Chapter</option>
            <option v-for="c in chapters" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <input v-model="newQuiz.date_of_quiz" class="form-control" type="date" placeholder="Date of Quiz" required />
        </div>
        <div class="col-md-2">
          <input v-model="newQuiz.duration" class="form-control" type="text" placeholder="Duration (hh:mm)" required />
        </div>
        <div class="col-md-2">
          <input v-model="newQuiz.remarks" class="form-control" placeholder="Remarks" />
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
          <th>Chapter</th>
          <th>Date</th>
          <th>Duration</th>
          <th>Remarks</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="quiz in quizzes" :key="quiz.id">
          <td>{{ quiz.id }}</td>
          <td>
            <select v-model="quiz.chapter_id" class="form-control">
              <option v-for="c in chapters" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </td>
          <td><input v-model="quiz.date_of_quiz" class="form-control" type="date" /></td>
          <td><input v-model="quiz.duration" class="form-control" type="text" /></td>
          <td><input v-model="quiz.remarks" class="form-control" /></td>
          <td>
            <button class="btn btn-primary btn-sm" @click="updateQuiz(quiz)">Update</button>
            <button class="btn btn-danger btn-sm" @click="deleteQuiz(quiz.id)">Delete</button>
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
      quizzes: [],
      chapters: [],
      newQuiz: { chapter_id: '', date_of_quiz: '', duration: '', remarks: '' },
      msg: ''
    };
  },
  async mounted() {
    await this.fetchQuizzes();
    await this.fetchChapters();
  },
  methods: {
    async fetchQuizzes() {
      const res = await axios.get('/api/quizzes');
      this.quizzes = res.data.quizzes;
    },
    async fetchChapters() {
      const res = await axios.get('/api/chapters');
      this.chapters = res.data.chapters;
    },
    async addQuiz() {
      // Only send required fields
      const payload = {
        chapter_id: this.newQuiz.chapter_id,
        date_of_quiz: this.newQuiz.date_of_quiz,
        duration: this.newQuiz.duration,
        remarks: this.newQuiz.remarks
      };
      await axios.post('/api/quizzes', payload);
      this.msg = 'Quiz added!';
      this.newQuiz = { chapter_id: '', date_of_quiz: '', duration: '', remarks: '' };
      await this.fetchQuizzes();
    },
    async updateQuiz(quiz) {
      const payload = {
        chapter_id: quiz.chapter_id,
        date_of_quiz: quiz.date_of_quiz,
        duration: quiz.duration,
        remarks: quiz.remarks
      };
      await axios.put(`/api/quizzes/${quiz.id}`, payload);
      this.msg = 'Quiz updated!';
      await this.fetchQuizzes();
    },
    async deleteQuiz(id) {
      await axios.delete(`/api/quizzes/${id}`);
      this.msg = 'Quiz deleted!';
      await this.fetchQuizzes();
    }
  }
};
</script>
