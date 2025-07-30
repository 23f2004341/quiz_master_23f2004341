<template>
  <div class="container mt-4">
    <h2>Attempt Quiz</h2>
    <div v-if="quiz">
      <div class="mb-3">
        <span class="badge bg-info text-dark">Time Left: {{ formattedTime }}</span>
      </div>
      <form @submit.prevent="submitQuiz">
        <div v-for="q in questions" :key="q.id" class="mb-3">
          <label><strong>{{ q.question_statement }}</strong></label>
          <div v-for="i in 4" :key="i">
            <input type="radio" :name="q.id" :value="i" v-model="answers[q.id]" />
            {{ q['option' + i] }}
          </div>
        </div>
        <button class="btn btn-success" type="submit" :disabled="timer === 0">Submit</button>
      </form>
      <div v-if="result" class="alert alert-info mt-3">
        Your Score: {{ result.total_score }}
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios';
export default {
  data() {
    return {
      quiz: null,
      questions: [],
      answers: {},
      result: null,
      timer: 0,
      timerInterval: null
    };
  },
  computed: {
    formattedTime() {
      const min = Math.floor(this.timer / 60);
      const sec = this.timer % 60;
      return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    }
  },
  async mounted() {
    const quizId = this.$route.params.id;
    const quizRes = await axios.get(`/api/quizzes/${quizId}`);
    this.quiz = quizRes.data.quiz;
    const qRes = await axios.get('/api/questions');
    this.questions = qRes.data.questions.filter(q => q.quiz_id === this.quiz.id);
    // Parse duration (hh:mm or mm)
    let totalSeconds = 0;
    if (this.quiz.duration.includes(':')) {
      const [h, m] = this.quiz.duration.split(':').map(Number);
      totalSeconds = (h * 60 + m) * 60;
    } else {
      totalSeconds = Number(this.quiz.duration) * 60;
    }
    this.timer = totalSeconds;
    this.startTimer();
  },
  beforeDestroy() {
    if (this.timerInterval) clearInterval(this.timerInterval);
  },
  methods: {
    startTimer() {
      this.timerInterval = setInterval(() => {
        if (this.timer > 0) {
          this.timer--;
        } else {
          clearInterval(this.timerInterval);
          if (!this.result) this.submitQuiz();
        }
      }, 1000);
    },
    async submitQuiz() {
      if (this.result) return; // Prevent double submit
      if (this.timerInterval) clearInterval(this.timerInterval);
      const payload = { answers: this.answers };
      const res = await axios.post(`/api/quizzes/${this.quiz.id}/attempt`, payload);
      this.result = { total_score: res.data.total_score };
    }
  }
};
</script>
