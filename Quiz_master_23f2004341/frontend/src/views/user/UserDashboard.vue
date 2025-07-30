<template>
  <div class="user-dashboard-bg min-vh-100 py-4">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="dashboard-title"><i class="fas fa-user-graduate me-2"></i>User Dashboard</h2>
        <button class="btn btn-danger btn-lg px-4" @click="logout"><i class="fas fa-sign-out-alt me-2"></i>Logout</button>
      </div>

      <!-- Summary Statistics Cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-primary text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-list-ol"></i></div>
              <h3 class="card-title mb-0">{{ analytics.total_quizzes }}</h3>
              <p class="card-text">Total Quizzes</p>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-success text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-chart-line"></i></div>
              <h3 class="card-title mb-0">{{ analytics.average_score }}</h3>
              <p class="card-text">Average Score</p>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-warning text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-trophy"></i></div>
              <h3 class="card-title mb-0">{{ analytics.best_score }}</h3>
              <p class="card-text">Best Score</p>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card shadow-sm text-center stat-card bg-info text-white">
            <div class="card-body">
              <div class="display-5 mb-2"><i class="fas fa-star"></i></div>
              <h3 class="card-title mb-0">{{ analytics.total_score }}</h3>
              <p class="card-text">Total Points</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-light fw-bold">
              <i class="fas fa-book-open me-2"></i>Performance by Subject
            </div>
            <div class="card-body">
              <canvas id="subjectChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card shadow-sm h-100">
            <div class="card-header bg-light fw-bold">
              <i class="fas fa-chart-area me-2"></i>Score Trend (Last 10 Attempts)
            </div>
            <div class="card-body">
              <canvas id="trendChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity Section -->
      <div class="mb-4" v-if="analytics.recent_activity.length > 0">
        <h4 class="section-title mb-3"><i class="fas fa-history me-2"></i>Recent Activity</h4>
        <div class="card shadow-sm p-3 bg-white rounded">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Quiz ID</th>
                  <th>Subject</th>
                  <th>Chapter</th>
                  <th>Score</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="activity in analytics.recent_activity" :key="activity.quiz_id">
                  <td>{{ activity.quiz_id }}</td>
                  <td>{{ activity.subject }}</td>
                  <td>{{ activity.chapter }}</td>
                  <td>
                    <span class="badge" :class="getScoreBadgeClass(activity.score)">
                      {{ activity.score }}
                    </span>
                  </td>
                  <td>{{ activity.date }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Available Quizzes Section with Filter -->
      <div class="mb-4">
        <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
          <h4 class="section-title mb-0"><i class="fas fa-question-circle me-2"></i>Available Quizzes</h4>
          <div class="input-group w-auto">
            <select class="form-select" v-model="selectedChapter">
              <option value="">All Chapters</option>
              <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">{{ chapter.name }}</option>
            </select>
            <input type="text" class="form-control" v-model="quizSearch" placeholder="Search quizzes...">
          </div>
        </div>
        <div class="card shadow-sm p-3 bg-white rounded">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Quiz ID</th>
                  <th>Chapter</th>
                  <th>Date</th>
                  <th>Duration</th>
                  <th>Remarks</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="quiz in filteredQuizzes" :key="quiz.id">
                  <td>{{ quiz.id }}</td>
                  <td>{{ getChapterName(quiz.chapter_id) }}</td>
                  <td>{{ quiz.date_of_quiz }}</td>
                  <td>{{ quiz.duration }}</td>
                  <td>{{ quiz.remarks }}</td>
                  <td>
                    <router-link :to="`/user/quiz/${quiz.id}/attempt`" class="btn btn-primary btn-sm"><i class="fas fa-play me-1"></i>Attempt</router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Performance by Chapter Section -->
      <div class="mb-4">
        <h4 class="section-title mb-3"><i class="fas fa-layer-group me-2"></i>Performance (Average Score per Chapter)</h4>
        <div class="card shadow-sm p-3 bg-white rounded">
          <ul class="list-group list-group-flush">
            <li v-for="(score, chapter) in performance" :key="chapter" class="list-group-item d-flex justify-content-between align-items-center">
              <span>{{ chapter }}</span>
              <span class="badge bg-success rounded-pill">{{ score.toFixed(2) }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Actions -->
      <div class="d-flex gap-3 flex-wrap mt-4">
        <router-link to="/user/quiz_history" class="btn btn-info btn-lg"><i class="fas fa-history me-2"></i>View Quiz History</router-link>
        <button class="btn btn-success btn-lg" @click="exportCSV" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <i class="fas fa-file-csv me-2"></i>{{ exporting ? 'Exporting...' : 'Export CSV' }}
        </button>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios';
import Chart from 'chart.js/auto';

export default {
  data() {
    return {
      quizzes: [],
      chapters: [],
      performance: {},
      analytics: {
        total_quizzes: 0,
        average_score: 0,
        best_score: 0,
        total_score: 0,
        recent_activity: [],
        performance_by_subject: {},
        performance_by_chapter: {},
        score_trend: []
      },
      exporting: false,
      subjectChart: null,
      trendChart: null,
      selectedChapter: '',
      quizSearch: ''
    };
  },
  computed: {
    filteredQuizzes() {
      let filtered = this.quizzes;
      if (this.selectedChapter) {
        filtered = filtered.filter(q => q.chapter_id === this.selectedChapter || q.chapter_id === Number(this.selectedChapter));
      }
      if (this.quizSearch) {
        const term = this.quizSearch.toLowerCase();
        filtered = filtered.filter(q =>
          (q.remarks && q.remarks.toLowerCase().includes(term)) ||
          (this.getChapterName(q.chapter_id) && this.getChapterName(q.chapter_id).toLowerCase().includes(term)) ||
          (q.id && String(q.id).includes(term))
        );
      }
      return filtered;
    }
  },
  async mounted() {
    await this.loadData();
    this.renderCharts();
  },
  methods: {
    async loadData() {
      try {
        const [quizRes, chapterRes, perfRes, analyticsRes] = await Promise.all([
          axios.get('/api/quizzes'),
          axios.get('/api/chapters'),
          axios.get('/api/user/quiz_history'),
          axios.get('/api/user/analytics')
        ]);
        this.quizzes = quizRes.data.quizzes;
        this.chapters = chapterRes.data.chapters;
        this.analytics = analyticsRes.data;
        // Calculate average score per chapter for existing performance section
        const scores = perfRes.data.history;
        const chapterScores = {};
        scores.forEach(s => {
          const chapter = this.getChapterName(this.getQuizChapterId(s.quiz_id));
          if (!chapterScores[chapter]) chapterScores[chapter] = [];
          chapterScores[chapter].push(s.total_score);
        });
        Object.keys(chapterScores).forEach(ch => {
          this.performance[ch] = chapterScores[ch].reduce((a, b) => a + b, 0) / chapterScores[ch].length;
        });
      } catch (error) {
        console.error('Error loading data:', error);
      }
    },
    renderCharts() {
      // Subject Performance Chart
      const subjectCtx = document.getElementById('subjectChart');
      if (subjectCtx && Object.keys(this.analytics.performance_by_subject).length > 0) {
        this.subjectChart = new Chart(subjectCtx, {
          type: 'bar',
          data: {
            labels: Object.keys(this.analytics.performance_by_subject),
            datasets: [{
              label: 'Average Score',
              data: Object.values(this.analytics.performance_by_subject),
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                max: 10
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
      // Score Trend Chart
      const trendCtx = document.getElementById('trendChart');
      if (trendCtx && this.analytics.score_trend.length > 0) {
        this.trendChart = new Chart(trendCtx, {
          type: 'line',
          data: {
            labels: this.analytics.score_trend.map(item => `Attempt ${item.attempt}`),
            datasets: [{
              label: 'Score',
              data: this.analytics.score_trend.map(item => item.score),
              borderColor: 'rgba(75, 192, 192, 1)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              tension: 0.1,
              fill: true
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                max: 10
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
    },
    getChapterName(id) {
      const chapter = this.chapters.find(c => c.id === id);
      return chapter ? chapter.name : 'Unknown';
    },
    getQuizChapterId(quizId) {
      const quiz = this.quizzes.find(q => q.id === quizId);
      return quiz ? quiz.chapter_id : null;
    },
    getScoreBadgeClass(score) {
      if (score >= 8) return 'bg-success';
      if (score >= 6) return 'bg-warning';
      return 'bg-danger';
    },
    async logout() {
      await axios.post('/api/logout');
      localStorage.clear();
      this.$router.push('/login');
    },
    async exportCSV() {
      this.exporting = true;
      try {
        const response = await axios.get('/api/user/export_quiz_history_direct', { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'quiz_history.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        alert('Quiz history exported successfully! Check your email for notification.');
      } catch (error) {
        alert('Failed to export quiz history.');
        console.error(error);
      } finally {
        this.exporting = false;
      }
    }
  }
};
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.user-dashboard-bg {
  background: linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%);
  font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
}
.dashboard-title {
  color: #2c3e50;
  font-weight: 700;
  letter-spacing: 1px;
}
.section-title {
  color: #1a237e;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
}
.card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.08);
}
.stat-card {
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.table {
  background: #fff;
  border-radius: 1rem;
  overflow: hidden;
}
.table th, .table td {
  vertical-align: middle;
}
.btn-primary {
  background: linear-gradient(90deg, #4f8cff 0%, #1a73e8 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.btn-primary:hover {
  background: linear-gradient(90deg, #1a73e8 0%, #4f8cff 100%);
}
.btn-danger {
  font-weight: 600;
  letter-spacing: 0.5px;
}
.btn-info {
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #fff;
  background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
  border: none;
}
.btn-info:hover {
  background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%);
}
.list-group-item {
  font-size: 1.1rem;
  background: transparent;
  border: none;
}
.bg-success {
  background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%) !important;
  color: #fff !important;
  font-weight: 600;
}
.bg-primary {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
}
.bg-warning {
  background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%) !important;
}
.bg-info {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%) !important;
}
</style>
