<template>
  <div class="container mt-4">
    <h2>Manage Questions</h2>
    <form @submit.prevent="addQuestion" class="mb-4">
      <div class="row">
        <div class="col-md-3">
          <input v-model="newQuestion.text" class="form-control" placeholder="Question Text" required />
        </div>
        <div class="col-md-2">
          <select v-model="newQuestion.quiz_id" class="form-control" required>
            <option disabled value="">Select Quiz</option>
            <option v-for="q in quizzes" :key="q.id" :value="q.id">Quiz #{{ q.id }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <input v-model="newQuestion.option_a" class="form-control" placeholder="Option A" required />
        </div>
        <div class="col-md-2">
          <input v-model="newQuestion.option_b" class="form-control" placeholder="Option B" required />
        </div>
        <div class="col-md-2">
          <input v-model="newQuestion.option_c" class="form-control" placeholder="Option C" required />
        </div>
        <div class="col-md-1">
          <input v-model="newQuestion.option_d" class="form-control" placeholder="Option D" required />
        </div>
      </div>
      <div class="row mt-2">
        <div class="col-md-2">
          <select v-model="newQuestion.correct_option" class="form-control" required>
            <option disabled value="">Correct Option</option>
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="D">D</option>
          </select>
        </div>
        <div class="col-md-2">
          <input v-model.number="newQuestion.marks" class="form-control" type="number" placeholder="Marks" required />
        </div>
        <div class="col-md-2">
          <button class="btn btn-success w-100" type="submit">Add</button>
        </div>
        <div class="col-md-6" v-if="selectedQuizRemarks">
          <div class="alert alert-info py-1 my-1">Quiz Remarks: {{ selectedQuizRemarks }}</div>
        </div>
      </div>
    </form>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Text</th>
          <th>Quiz</th>
          <th>Options</th>
          <th>Correct</th>
          <th>Marks</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="question in questions" :key="question.id">
          <td>{{ question.id }}</td>
          <td><input v-model="question.text" class="form-control" /></td>
          <td>
            <select v-model="question.quiz_id" class="form-control">
              <option v-for="q in quizzes" :key="q.id" :value="q.id">Quiz #{{ q.id }}</option>
            </select>
          </td>
          <td>
            <input v-model="question.option_a" class="form-control mb-1" placeholder="A" />
            <input v-model="question.option_b" class="form-control mb-1" placeholder="B" />
            <input v-model="question.option_c" class="form-control mb-1" placeholder="C" />
            <input v-model="question.option_d" class="form-control mb-1" placeholder="D" />
          </td>
          <td>
            <select v-model="question.correct_option" class="form-control">
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
            </select>
          </td>
          <td><input v-model.number="question.marks" class="form-control" type="number" /></td>
          <td>
            <button class="btn btn-primary btn-sm" @click="updateQuestion(question)">Update</button>
            <button class="btn btn-danger btn-sm" @click="deleteQuestion(question.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="msg" class="alert alert-info mt-2">{{ msg }}</div>
  </div>
</template>
<script>
import axios from 'axios';
const optionMap = { 'A': 1, 'B': 2, 'C': 3, 'D': 4 };
export default {
  data() {
    return {
      questions: [],
      quizzes: [],
      newQuestion: {
        text: '', quiz_id: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: '', marks: ''
      },
      msg: ''
    };
  },
  computed: {
    selectedQuizRemarks() {
      const quiz = this.quizzes.find(q => q.id === this.newQuestion.quiz_id);
      return quiz ? quiz.remarks : '';
    }
  },
  async mounted() {
    await this.fetchQuestions();
    await this.fetchQuizzes();
  },
  methods: {
    async fetchQuestions() {
      const res = await axios.get('/api/questions');
      this.questions = res.data.questions;
    },
    async fetchQuizzes() {
      const res = await axios.get('/api/quizzes');
      this.quizzes = res.data.quizzes;
    },
    async addQuestion() {
      const payload = {
        quiz_id: this.newQuestion.quiz_id,
        question_statement: this.newQuestion.text,
        option1: this.newQuestion.option_a,
        option2: this.newQuestion.option_b,
        option3: this.newQuestion.option_c,
        option4: this.newQuestion.option_d,
        correct_option: optionMap[this.newQuestion.correct_option] || 1
      };
      await axios.post('/api/questions', payload);
      this.msg = 'Question added!';
      this.newQuestion = { text: '', quiz_id: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: '', marks: '' };
      await this.fetchQuestions();
    },
    async updateQuestion(question) {
      const payload = {
        quiz_id: question.quiz_id,
        question_statement: question.text,
        option1: question.option_a,
        option2: question.option_b,
        option3: question.option_c,
        option4: question.option_d,
        correct_option: optionMap[question.correct_option] || 1
      };
      await axios.put(`/api/questions/${question.id}`, payload);
      this.msg = 'Question updated!';
      await this.fetchQuestions();
    },
    async deleteQuestion(id) {
      await axios.delete(`/api/questions/${id}`);
      this.msg = 'Question deleted!';
      await this.fetchQuestions();
    }
  }
};
</script>
